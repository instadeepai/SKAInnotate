import os
import logging
from google.cloud import storage, run_v2
from google.oauth2 import service_account
from google.api_core.exceptions import NotFound, AlreadyExists
from google.auth import default
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_credentials(service_account_file):
  """Fetch credentials from a service account file."""
  logger.info(f"Service account file: {service_account_file}")
  if not service_account_file:
    raise RuntimeError("Service account file not provided.")
  return service_account.Credentials.from_service_account_file(service_account_file)

def get_sqladmin_client(service_account_file):
  return build('sqladmin', 'v1beta4', credentials=get_credentials(service_account_file))


def get_cloud_run_client(service_account_file):
  """Create a Cloud Run client."""
  credentials = get_credentials(service_account_file)
  return run_v2.ServicesClient(credentials=credentials)

def get_cloud_run_url(service_account, service_name, project_id, region):
  """Fetch the URL of a Cloud Run service."""
  client = get_cloud_run_client(service_account)  # Use default credentials
  service_path = f"projects/{project_id}/locations/{region}/services/{service_name}"
  try:
    service = client.get_service(name=service_path)
    return service.uri
  except NotFound:
    print(f"Service '{service_name}' not found.")
    return None

def run_deploy(service_account_file, service_name, project_id, container_image, region, instance_connection_name, env_vars):
  """Deploy a service to Cloud Run using the Python client."""
  logger.info(f"Inspect service account file: {service_account_file}, service name: {service_name}")
  client = get_cloud_run_client(service_account_file)  # Use default credentials
  parent = f"projects/{project_id}/locations/{region}"

  # Define the service template
  service = run_v2.Service(
      name=f"{parent}/services/{service_name}",
      template=run_v2.RevisionTemplate(
          containers=[
              run_v2.Container(
                  image=container_image,
                  env=[run_v2.EnvVar(name=k, value=v) for k, v in env_vars.items()],
              )
          ],
          service_account=f"{service_name}-sa@{project_id}.iam.gserviceaccount.com",
      ),
  )

  try:
    operation = client.create_service(parent=parent, service=service, service_id=service_name)
    print(f"Deploying service '{service_name}'...")
    operation.result()  # Wait for the operation to complete
    print(f"Service '{service_name}' deployed successfully.")
    return 0
  except AlreadyExists:
    print(f"Service '{service_name}' already exists.")
    return 1
  except Exception as e:
    print(f"Error deploying service: {e}")
    return 1

def delete_service(service_name, project_id, region):
  """Delete a Cloud Run service."""
  client = get_cloud_run_client(None)  # Use default credentials
  service_path = f"projects/{project_id}/locations/{region}/services/{service_name}"

  try:
    operation = client.delete_service(name=service_path)
    operation.result()  # Wait for the operation to complete
    print(f"Service '{service_name}' deleted successfully.")
    return f"Service '{service_name}' deleted successfully."
  except NotFound:
    print(f"Service '{service_name}' not found.")
    return f"Service '{service_name}' not found."
  except Exception as e:
    print(f"Error deleting service: {e}")
    return f"Failed to delete service '{service_name}': {e}"



def create_cloudsql_instance(service_account_file, project_id, instance_name, region, database_name, db_user, db_pass):
  instance_body = {
      'name': instance_name,
      'settings': {'tier': 'db-f1-micro'},
      'databaseVersion': 'POSTGRES_15',
      'region': region
  }
  
  sqladmin = get_sqladmin_client(service_account_file)

  # Check if the Cloud SQL instance already exists
  try:
    sqladmin.instances().get(project=project_id, instance=instance_name).execute()
    instance_exists = True
  except HttpError as e:
    if e.resp.status == 404:
      instance_exists = False
    else:
      print("Error: ", str(e))
      return {"error": f"Failed to check instance existence: {str(e)}"}

  # Create the Cloud SQL instance if it doesn't exist
  if not instance_exists:
    try:
      request = sqladmin.instances().insert(project=project_id, body=instance_body)
      response = request.execute()
      instance_created = True
    except HttpError as e:
      return {"error": f"Failed to create instance: {str(e)}"}
  else:
    instance_created = False

  try:
    sqladmin.databases().get(project=project_id, instance=instance_name, database=database_name).execute()
    database_exists = True
  except HttpError as e:
    if e.resp.status == 404:
      database_exists = False
    else:
      return {"error": f"Failed to check database existence: {str(e)}"}

  # Create the database if it doesn't exist
  if not database_exists:
    try:
      request = sqladmin.databases().insert(project=project_id, instance=instance_name, body={'name': database_name})
      response = request.execute()
    except HttpError as e:
      return {"error": f"Failed to create database: {str(e)}"}

  # Check if the user already exists
  try:
    users_list = sqladmin.users().list(project=project_id, instance=instance_name).execute()
    user_exists = any(user['name'] == db_user for user in users_list.get('items', []))
  except HttpError as e:
    return {"error": f"Failed to check user existence: {str(e)}"}

  # Create the user if it doesn't exist
  if not user_exists:
    user_body = {
        "name": db_user,
        "password": db_pass,
        "host": "%"
    }
    try:
      sqladmin.users().insert(project=project_id, instance=instance_name, body=user_body).execute()
      user_created = True
    except HttpError as e:
      return {"error": f"Failed to create user: {str(e)}"}
  else:
    user_created = False

  # Check if the default postgres user exists and update password if necessary
  try:
    postgres_user = next(user for user in users_list.get('items', []) if user['name'] == 'postgres')
    if postgres_user and 'password' in postgres_user:
        # Update the password if the user exists
      update_body = {
          "name": "postgres",
          "password": db_pass,
          "host": "%"
      }
      sqladmin.users().update(project=project_id, instance=instance_name, body=update_body).execute()
  except StopIteration:
    # Postgres user does not exist, create it
    user_body = {
        "name": "postgres",
        "password": db_pass,
        "host": "%"
    }
    try:
      sqladmin.users().insert(project=project_id, instance=instance_name, body=user_body).execute()
    except HttpError as e:
      return {"error": f"Failed to create postgres user: {str(e)}"}

  return instance_created, database_exists, user_created

# Example usage
# service_account_file = "skai-project-388314-ec99ca5755fb.json"
# project_id = "skai-project-388314"
# region = "us-central1"

# # Create Cloud SQL instance
# create_cloudsql_instance(service_account_file, project_id, "test-instance", region, "test-db", "test-user", "test-pass")

# # Deploy Cloud Run service
# run_deploy(service_account_file, "test-service", project_id, "gcr.io/your-project-id/your-image", region, "test-instance", {"ENV_VAR": "value"})

# # Get Cloud Run URL
# url = get_cloud_run_url(service_account_file, "test-service", project_id, region)
# print(f"Cloud Run URL: {url}")


# def create_cloudsql_instance(service_account_file, project_id, instance_name, region, database_name, db_user, db_pass):
#     """Create a Cloud SQL instance, database, and user."""
#     client = get_sqladmin_client(service_account_file)
#     print("Google cloud client: ", help(client))
#     instance_path = f"projects/{project_id}/instances/{instance_name}"

#     # Check if the instance already exists
#     try:
#         instance = client.get_instance(project=project_id, instance=instance_name)
#         instance_exists = True
#     except NotFound:
#         instance_exists = False

#     # Create the instance if it doesn't exist
#     if not instance_exists:
#         instance_body = {
#             "name": instance_name,
#             "settings": {"tier": "db-f1-micro"},
#             "database_version": "POSTGRES_15",
#             "region": region,
#         }
#         try:
#             operation = client.insert_instance(project=project_id, body=instance_body)
#             operation.result()  # Wait for the operation to complete
#             print(f"Cloud SQL instance '{instance_name}' created.")
#             instance_exists = True
#         except Exception as e:
#             return {"error": f"Failed to create instance: {e}"}

#     # Create the database
#     try:
#         database = client.get_database(project=project_id, instance=instance_name, database=database_name)
#         database_exists = True
#     except NotFound:
#         database_exists = False

#     if not database_exists:
#         database_body = {"name": database_name}
#         try:
#             operation = client.insert_database(project=project_id, instance=instance_name, body=database_body)
#             operation.result()
#             print(f"Database '{database_name}' created.")
#         except Exception as e:
#             return {"error": f"Failed to create database: {e}"}

#     # Create the user
#     try:
#         users = client.list_users(project=project_id, instance=instance_name)
#         user_exists = any(user.name == db_user for user in users)
#     except Exception as e:
#         return {"error": f"Failed to check user existence: {e}"}

#     if not user_exists:
#         user_body = {"name": db_user, "password": db_pass}
#         try:
#             operation = client.insert_user(project=project_id, instance=instance_name, body=user_body)
#             operation.result()
#             print(f"User '{db_user}' created.")
#         except Exception as e:
#             return {"error": f"Failed to create user: {e}"}

#     # Update the postgres user password
#     try:
#         postgres_user = next(user for user in users if user.name == "postgres")
#         if postgres_user:
#             update_body = {"name": "postgres", "password": db_pass}
#             operation = client.update_user(project=project_id, instance=instance_name, body=update_body)
#             operation.result()
#             print("Postgres user password updated.")
#     except StopIteration:
#         print("Postgres user not found.")

#     return instance_exists, database_exists, user_exists


# Delete Cloud Run service
# delete_service("test-service", project_id, region)

# import os
# import subprocess
# import yaml
# from google.cloud import storage
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from google.oauth2 import service_account
# from google.auth import default
# from google.auth.transport.requests import Request
# # from google.cloud import run_v2
# from google.auth import credentials
# # from service_template import create_service_template

# def get_credentials(service_account_file):
#   if service_account_file:
#     credentials = service_account.Credentials.from_service_account_file(service_account_file)
#   else:
#     raise RuntimeError("Service account file not set in environment variables.")
#   return credentials

# def get_sqladmin_client(service_account_file):
#   return build('sqladmin', 'v1beta4', credentials=get_credentials(service_account_file))

# def get_cloud_run_url(service_name, project_id, region):
  
#   try:
#     result = subprocess.run(
#       [
#         "gcloud", "run", "services", "describe", service_name,
#         "--platform", "managed",
#         "--region", region,
#         "--project", project_id,
#         "--format", "value(status.url)"
#       ],
#       capture_output=True, text=True, check=True
#     )
#     return result.stdout.strip()
#   except subprocess.CalledProcessError as e:
#     print(f"Error occurred: {e}")
#     return None

# # def run_deploy_python_client():

# #   credentials, project = google.auth.default()
# #   client = run_v2.ServicesClient(credentials=credentials)

# #   # Create the service template
# #   service_template = create_service_template(
# #       image, env_vars, sql_instance_connection_name
# #   )

# #   # Create the service
# #   parent = f"projects/{project_id}/locations/{region}"
# #   request = run_v2.CreateServiceRequest(
# #       parent=parent, service=service_name, service_template=service_template
# #   )
# #   response = client.create_service(request=request)

# #   print(f"Service created: {response.name}")

# def run_deploy(service_name,
#               project_id,
#               container_image,
#               region,
#               instance_connection_name,
#               env_vars):
#   try:
#     env_vars_str = str(env_vars)

#     result = subprocess.run(
#         ["bash", "deployment_setup/deploy.sh", 
#           f"{service_name}", 
#           f"{project_id}",
#           f"{container_image}", 
#           f"{region}", 
#           f"{instance_connection_name}", 
#           env_vars_str],
#         check=True,
#         capture_output=True,
#         text=True
#     )
    
#     print(f"Output: {result.stdout}")
#     print(f"Error (if any): {result.stderr}")
    
#     return result.returncode

#   except subprocess.CalledProcessError as e:
#     print(f"Error occurred: {e.stderr}")
#     return e.returncode

# def delete_service(service_name, project_id):
#   try:
#     result = subprocess.run(
#         ['gcloud', 'run', 'services', 'delete', service_name, '--project', project_id, '--quiet'],
#         capture_output=True,
#         text=True,
#         check=True
#     )
#     print(result.stdout)  # Print the output from the command
#     return f"Service '{service_name}' deleted successfully."
#   except subprocess.CalledProcessError as e:
#     print(e.stderr)  # Print any error message
#     return f"Failed to delete service '{service_name}': {e.stderr}"

# def create_cloudsql_instance(service_account_file, project_id, instance_name, region, database_name, db_user, db_pass):
#   instance_body = {
#       'name': instance_name,
#       'settings': {'tier': 'db-f1-micro'},
#       'databaseVersion': 'POSTGRES_15',
#       'region': region
#   }
  
#   sqladmin = get_sqladmin_client(service_account_file)

#   # Check if the Cloud SQL instance already exists
#   try:
#     sqladmin.instances().get(project=project_id, instance=instance_name).execute()
#     instance_exists = True
#   except HttpError as e:
#     if e.resp.status == 404:
#       instance_exists = False
#     else:
#       print("Error: ", str(e))
#       return {"error": f"Failed to check instance existence: {str(e)}"}

#   # Create the Cloud SQL instance if it doesn't exist
#   if not instance_exists:
#     try:
#       request = sqladmin.instances().insert(project=project_id, body=instance_body)
#       response = request.execute()
#       instance_created = True
#     except HttpError as e:
#       return {"error": f"Failed to create instance: {str(e)}"}
#   else:
#     instance_created = False

#   try:
#     sqladmin.databases().get(project=project_id, instance=instance_name, database=database_name).execute()
#     database_exists = True
#   except HttpError as e:
#     if e.resp.status == 404:
#       database_exists = False
#     else:
#       return {"error": f"Failed to check database existence: {str(e)}"}

#   # Create the database if it doesn't exist
#   if not database_exists:
#     try:
#       request = sqladmin.databases().insert(project=project_id, instance=instance_name, body={'name': database_name})
#       response = request.execute()
#     except HttpError as e:
#       return {"error": f"Failed to create database: {str(e)}"}

#   # Check if the user already exists
#   try:
#     users_list = sqladmin.users().list(project=project_id, instance=instance_name).execute()
#     user_exists = any(user['name'] == db_user for user in users_list.get('items', []))
#   except HttpError as e:
#     return {"error": f"Failed to check user existence: {str(e)}"}

#   # Create the user if it doesn't exist
#   if not user_exists:
#     user_body = {
#         "name": db_user,
#         "password": db_pass,
#         "host": "%"
#     }
#     try:
#       sqladmin.users().insert(project=project_id, instance=instance_name, body=user_body).execute()
#       user_created = True
#     except HttpError as e:
#       return {"error": f"Failed to create user: {str(e)}"}
#   else:
#     user_created = False

#   # Check if the default postgres user exists and update password if necessary
#   try:
#     postgres_user = next(user for user in users_list.get('items', []) if user['name'] == 'postgres')
#     if postgres_user and 'password' in postgres_user:
#         # Update the password if the user exists
#       update_body = {
#           "name": "postgres",
#           "password": db_pass,
#           "host": "%"
#       }
#       sqladmin.users().update(project=project_id, instance=instance_name, body=update_body).execute()
#   except StopIteration:
#     # Postgres user does not exist, create it
#     user_body = {
#         "name": "postgres",
#         "password": db_pass,
#         "host": "%"
#     }
#     try:
#       sqladmin.users().insert(project=project_id, instance=instance_name, body=user_body).execute()
#     except HttpError as e:
#       return {"error": f"Failed to create postgres user: {str(e)}"}

#   return instance_created, database_exists, user_created

