import os
import subprocess
from skainnotate.utils.logger import logger

def run_bash_command(command, success_msg=None, failure_msg=None):
  """
  Execute a bash command and handle success or failure.

  Args:
  - command (str): The bash command to execute.
  - success_msg (str, optional): Message to print on success.
  - failure_msg (str, optional): Message to print on failure.

  Returns:
  - str or None: Output of the command as a decoded string, or None on failure.
  """
  try:
    result = subprocess.run(
      command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if result.returncode == 0:
      if success_msg:
        logger.log_info(success_msg)
    else:
      if failure_msg:
        logger.log_error(failure_msg)
      logger.log_info(result.stderr.decode())
  except subprocess.CalledProcessError as e:
    logger.log_exception(e, f"Error running command: {command}")
    return None
  return result.stdout.decode().strip() if result else None

def authenticate_user():
  """
  Authenticate the user using `gcloud auth login`.

  Returns:
  - str or None: Output of the command as a decoded string, or None on failure.
  """
  command = 'gcloud auth login'
  success_msg = 'Authentication Successful'
  failure_msg = 'Authentication Failed'
  return run_bash_command(command, success_msg, failure_msg)

def set_project_id(project_id):
  """
  Set the current project ID using `gcloud config set project`.

  Args:
  - project_id (str): The project ID to set.

  Returns:
  - str or None: Output of the command as a decoded string, or None on failure.
  """
  command = f'gcloud config set project {project_id}'
  return run_bash_command(command)

def get_active_user():
  """
  Retrieve the active user's account using `gcloud auth list`.

  Returns:
  - str or None: Output of the command as a decoded string, or None on failure.
  """
  command = (
    'gcloud auth list ' +
    '--filter=status:ACTIVE ' +
    '--format="value(account)"'
  )
  return run_bash_command(command)

def set_project_policy(project_id, user_account, role):
  """
  Set IAM policy for a project using `gcloud projects add-iam-policy-binding`.

  Args:
  - project_id (str): The project ID.
  - user_account (str): The user's email account.
  - role (str): The role to assign.

  Returns:
  - str or None: Output of the command as a decoded string, or None on failure.
  """
  command = (
    f'gcloud projects add-iam-policy-binding {project_id} '
    f'--member=user:{user_account} '
    f'--role={role}'
  )
  return run_bash_command(command)

def get_database_version(instance_name):
  """
  Retrieve the database version for a Cloud SQL instance using `gcloud sql instances describe`.

  Args:
  - instance_name (str): The name of the Cloud SQL instance.

  Returns:
  - str or None: Output of the command as a decoded string, or None on failure.
  """
  command = (
    f'gcloud sql instances describe {instance_name} '
    '--format="value(databaseVersion)"'
  )
  return run_bash_command(command)

def create_sql_instance(instance_name, region, root_password, instance_settings=None):
  """
  Create a new Cloud SQL instance using `gcloud sql instances create`.

  Args:
  - instance_name (str): The name of the new Cloud SQL instance.
  - region (str): The region for the instance.
  - root_password (str): The root password for the instance.

  Returns:
  - str or None: Output of the command as a decoded string, or None on failure.
  """
  command = (
    f'gcloud sql instances create {instance_name} '
    '--database-version=POSTGRES_15 '
    f'--region={region} '
    '--cpu=1 '
    '--memory=4GB '
    f'--root-password={root_password} '
    '--database-flags=cloudsql.iam_authentication=On'
  )
  return run_bash_command(command)

def create_database(database_name, instance_name):
  """
  Create a new database in a Cloud SQL instance using `gcloud sql databases create`.

  Args:
  - database_name (str): The name of the new database.
  - instance_name (str): The name of the Cloud SQL instance.

  Returns:
  - str or None: Output of the command as a decoded string, or None on failure.
  """
  command = (
    f'gcloud sql databases create {database_name} '
    f'--instance={instance_name}'
  )
  return run_bash_command(command)

def grant_sql_access(user_email, project_id):
  """
  Grant SQL access to a user using `gcloud projects add-iam-policy-binding`.

  Args:
  - user_email (str): The email of the user to grant access.
  - project_id (str): The project ID.

  Returns:
  - str or None: Output of the command as a decoded string, or None on failure.
  """
  command = (
    f'gcloud projects add-iam-policy-binding {project_id} '
    f'--member=user:{user_email} '
    '--role="roles/cloudsql.client"'
  )
  return run_bash_command(command)

def grant_gcs_access(user_email, bucket_name):
  """
  Grant access to a user for a Google Cloud Storage bucket using `gsutil iam ch`.

  Args:
  - user_email (str): The email of the user to grant access.
  - bucket_name (str): The name of the GCS bucket.

  Returns:
  - str or None: Output of the command as a decoded string, or None on failure.
  """
  gcs_path = bucket_name if bucket_name.startswith("gs://") else os.path.join("gs://", bucket_name)
  command = f'gsutil iam ch user:{user_email}:objectViewer {gcs_path}'
  return run_bash_command(command)

def remove_sql_access(user_email, project_id):
  """
  Remove SQL access from a user using `gcloud projects remove-iam-policy-binding`.

  Args:
  - user_email (str): The email of the user to remove access.
  - project_id (str): The project ID.

  Returns:
  - str or None: Output of the command as a decoded string, or None on failure.
  """
  command = (
    f'gcloud projects remove-iam-policy-binding {project_id} '
    f'--member=user:{user_email} '
    '--role="roles/cloudsql.client"'
  )
  return run_bash_command(command)

def remove_gcs_access(user_email, bucket_name):
  """
  Remove access from a user for a Google Cloud Storage bucket using `gsutil iam ch -d`.

  Args:
  - user_email (str): The email of the user to remove access.
  - bucket_name (str): The name of the GCS bucket.

  Returns:
  - str or None: Output of the command as a decoded string, or None on failure.
  """
  gcs_path = bucket_name if bucket_name.startswith("gs://") else os.path.join("gs://", bucket_name)
  command = f'gsutil iam ch -d user:{user_email}:objectViewer {gcs_path}'
  return run_bash_command(command)

def create_user(username, password, instance_name):
  """
  Create a new user in a Cloud SQL instance using `gcloud sql users create`.

  Args:
  - username (str): The name of the new user.
  - password (str): The password for the new user.
  - instance_name (str): The name of the Cloud SQL instance.

  Returns:
  - str or None: Output of the command as a decoded string, or None on failure.
  """
  command = (
    f'gcloud sql users create {username} '
    f'--instance={instance_name} '
    f'--password={password}'
  )
  return run_bash_command(command)

def delete_user(username, instance_name):
  """
  Delete a user from a Cloud SQL instance using `gcloud sql users delete`.

  Args:
  - username (str): The name of the user to delete.
  - instance_name (str): The name of the Cloud SQL instance.

  Returns:
  - str or None: Output of the command as a decoded string, or None on failure.
  """
  command = (
    f'gcloud sql users delete {username} '
    f'--instance={instance_name}'
  )
  return run_bash_command(command)