import os
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from google.oauth2 import service_account
from google.api_core.exceptions import NotFound
from pydantic_settings import BaseSettings

import deployment_setup.backend.app.utils as utils
import deployment_setup.backend.app.configs as configs
import deployment_setup.backend.app.schema as schema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
  project_id: str = os.getenv("PROJECT_ID") or ""
  service_account_file: str = os.getenv("SERVICE_ACCOUNT_FILE") or ""

  class Config:
    env_file = ".env"

settings = Settings()

router = APIRouter()

def get_credentials(service_account_file: str):
  return service_account.Credentials.from_service_account_file(service_account_file)

@router.post("/setup-project", response_class=JSONResponse)
async def get_project_details(setProjectData: schema.setProject):
  if not setProjectData.service_account_file:
    raise HTTPException(status_code=400, detail="No service account added")

  try:
    credentials = get_credentials(setProjectData.service_account_file)
    os.environ["PROJECT_ID"] = setProjectData.project_id
    os.environ["SERVICE_ACCOUNT_FILE"] = setProjectData.service_account_file

    return {"message": "Project setup verified"}
  except NotFound:
    raise HTTPException(status_code=404, detail="Project not found")
  except Exception as e:
    logger.error(f"Error setting up project: {e}")
    raise HTTPException(status_code=500, detail=str(e))

@router.post("/setup-gcp-sql", response_class=JSONResponse)
async def setup_cloud_sql(sqlInstanceData: schema.SQLInstance):
  try:
      out = utils.create_cloudsql_instance(
          project_id=sqlInstanceData.project_id,
          service_account_file=sqlInstanceData.service_account_file,
          instance_name=sqlInstanceData.instance_name,
          region=sqlInstanceData.region,
          database_name=sqlInstanceData.database_name,
          db_user=sqlInstanceData.db_user,
          db_pass=sqlInstanceData.db_pass
      )

      if out:
        instance_created, database_exists, user_created = out
        return {
            "message": f"Cloud SQL Instance '{sqlInstanceData.instance_name}' setup complete. "
                        f"Database '{sqlInstanceData.database_name}' {'created' if not database_exists else 'already exists'}. "
                        f"User '{sqlInstanceData.db_user}' {'created' if user_created else 'already exists'}."
        }
      else:
        raise HTTPException(status_code=500, detail="Cloud SQL instance creation failed")
  except Exception as e:
    logger.error(f"Error setting up Cloud SQL: {e}")
    raise HTTPException(status_code=500, detail=str(e))

@router.post("/deploy", response_class=JSONResponse)
async def setup_cloud_run(deployData: schema.DeployAppData):
  instance_connection_name = f"{deployData.project_id}:{deployData.region}:{deployData.instance_name}"
  cfg = configs.get_configs()
  container_image = cfg['CONTAINER_IMAGE']

  envs_backend = {
      "PROJECT_ID": deployData.project_id,
      "REGION": deployData.region,
      "DB_NAME": deployData.db_name,
      "DB_PASS": deployData.db_pass,
      "DB_USER": deployData.db_user,
      "INSTANCE_NAME": deployData.instance_name,
      "SUPERUSER_EMAIL": deployData.superuser_email,
      "SUPERUSER_USERNAME": deployData.superuser_username,
      "GOOGLE_CLIENT_ID": deployData.clientId,
      "SERVICE_ACCOUNT_FILE": deployData.service_account_file
  }

  try:
    logger.info(f"Deploying service {deployData.service_account_file}")
    envs_vars_str = ",".join([f'{i}={v}' for i, v in envs_backend.items()])
    utils.run_deploy(
      service_account_file=deployData.service_account_file,
      service_name=deployData.service_name,
      project_id=deployData.project_id,
      container_image=container_image,
      instance_connection_name=instance_connection_name,
      region=deployData.region,
      env_vars=envs_vars_str
    )

    logger.info("Fetching Cloud Run service URL")
    service_url = utils.get_cloud_run_url(
      service_name=deployData.service_name,
      project_id=deployData.project_id,
      region=deployData.region
    )
    return {"message": "Deployment successful", "service_url": service_url}
  except Exception as e:
    logger.error(f"Error deploying service: {e}")
    raise HTTPException(status_code=500, detail=str(e))