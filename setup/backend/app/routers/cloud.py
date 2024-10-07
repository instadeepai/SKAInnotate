import os
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from google.oauth2 import service_account
from google.api_core.exceptions import NotFound

import setup.backend.app.utils as utils
import setup.backend.app.configs as configs
import setup.backend.app.schema as schema
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

project_id = os.getenv("PROJECT_ID")
service_account_file = os.getenv("SERVICE_ACCOUNT_FILE")
credentials = None

router = APIRouter()

@router.post("/setup-project", response_class=JSONResponse)
async def get_project_details(setProjectData: schema.setProject):
  global credentials
  if not setProjectData.service_account_file:
    return {"message": "No service account added"}
  try:
    credentials = service_account.Credentials.from_service_account_file(setProjectData.service_account_file)
    os.environ["PROJECT_ID"] = setProjectData.project_id
    os.environ["SERVICE_ACCOUNT_FILE"] = setProjectData.service_account_file

    return {"message": "Project setup verified"}
  except NotFound:
    return {"error": "Project not found"}
  except Exception as e:
    return {"error": str(e)}

@router.post("/setup-gcp-sql", response_class=JSONResponse)
async def setup_cloud_sql(sqlInstanceData: schema.SQLInstance):
  project_id = sqlInstanceData.project_id
  instance_name = sqlInstanceData.instance_name
  region = sqlInstanceData.region
  database_name = sqlInstanceData.database_name
  db_user = sqlInstanceData.db_user
  db_pass = sqlInstanceData.db_pass
  service_account_file = sqlInstanceData.service_account_file

  out=utils.create_cloudsql_instance(project_id=project_id,
                                 service_account_file=service_account_file,
                                 instance_name=instance_name,
                                 region=region,
                                 database_name=database_name,
                                 db_user=db_user,
                                 db_pass=db_pass)

  if out:
    instance_created, database_exists, user_created = out
    return {
        "message": f"Cloud SQL Instance '{instance_name}' setup complete. "
                    f"Database '{database_name}' {'created' if not database_exists else 'already exists'}. "
                    f"User '{db_user}' {'created' if user_created else 'already exists'}."
      }
  else:
    return {"message": "Cloud SQL instance creation failed"}

@router.post("/deploy", response_class=JSONResponse)
async def setup_cloud_run(deployData: schema.DeployAppData):
  instance_connection_name = f"{deployData.project_id}:{deployData.region}:{deployData.instance_name}"
  cfg = configs.get_configs()
  container_image = cfg['CONTAINER_IMAGE']

  envs_backend =  {"PROJECT_ID": deployData.project_id,
                  "REGION": deployData.region,
                  "DB_NAME": deployData.db_name,
                  "DB_PASS": deployData.db_pass, 
                  "DB_USER": deployData.db_user,
                  "INSTANCE_NAME": deployData.instance_name,
                  "SUPERUSER_EMAIL": deployData.superuser_email,
                  "SUPERUSER_USERNAME": deployData.superuser_username,
                  "GOOGLE_CLIENT_ID": deployData.clientId
                  }
  
  try:
    logger.info("Deploying service")
    envs_vars_str=",".join([f'{i}={v}' for i, v in envs_backend.items()])
    utils.run_deploy(service_name=f'{deployData.service_name}',
                 project_id=deployData.project_id,
                 container_image=container_image,
                 instance_connection_name=instance_connection_name,
                 region=deployData.region,
                 env_vars=envs_vars_str)

    logger.info("Fetching Cloud Run service URL")
    service_url = utils.get_cloud_run_url(service_name=f'{deployData.service_name}',
                                          project_id=deployData.project_id,
                                          region=deployData.region)
    return {"message": "Deployment successful", "service_url": service_url}
  except Exception as e:
    return {"error": str(e)}