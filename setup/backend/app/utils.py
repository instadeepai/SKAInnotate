import os
import subprocess
import yaml
from google.cloud import storage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from google.auth import default
from google.auth.transport.requests import Request


def get_credentials(service_account_file):
  if service_account_file:
    credentials = service_account.Credentials.from_service_account_file(service_account_file)
  else:
    raise RuntimeError("Service account file not set in environment variables.")
  return credentials

def get_sqladmin_client(service_account_file):
  return build('sqladmin', 'v1beta4', credentials=get_credentials(service_account_file))

def get_cloud_run_url(service_name, project_id, region):
  
  try:
    result = subprocess.run(
      [
        "gcloud", "run", "services", "describe", service_name,
        "--platform", "managed",
        "--region", region,
        "--project", project_id,
        "--format", "value(status.url)"
      ],
      capture_output=True, text=True, check=True
    )
    return result.stdout.strip()
  except subprocess.CalledProcessError as e:
    print(f"Error occurred: {e}")
    return None

def run_deploy(service_name,
              project_id,
              container_image,
              region,
              instance_connection_name,
              env_vars):
  try:
    env_vars_str = str(env_vars)

    result = subprocess.run(
        ["bash", "setup/deploy.sh", 
          f"{service_name}", 
          f"{project_id}",
          f"{container_image}", 
          f"{region}", 
          f"{instance_connection_name}", 
          env_vars_str],
        check=True,
        capture_output=True,
        text=True
    )
    
    print(f"Output: {result.stdout}")
    print(f"Error (if any): {result.stderr}")
    
    return result.returncode

  except subprocess.CalledProcessError as e:
    print(f"Error occurred: {e.stderr}")
    return e.returncode

def delete_service(service_name, project_id):
  try:
    result = subprocess.run(
        ['gcloud', 'run', 'services', 'delete', service_name, '--project', project_id, '--quiet'],
        capture_output=True,
        text=True,
        check=True
    )
    print(result.stdout)  # Print the output from the command
    return f"Service '{service_name}' deleted successfully."
  except subprocess.CalledProcessError as e:
    print(e.stderr)  # Print any error message
    return f"Failed to delete service '{service_name}': {e.stderr}"

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

