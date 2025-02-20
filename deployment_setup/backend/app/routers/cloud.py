import os
import logging
from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from fastapi.responses import JSONResponse
from google.oauth2 import service_account
from google.api_core.exceptions import NotFound
from pydantic_settings import BaseSettings
from pydantic import EmailStr

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


@router.post("/deploy/to-cloud", response_class=JSONResponse)
async def setup_cloud_run(
    project_id: str = Form(...),
    instance_name: str = Form(...),
    region: str = Form(...),
    db_name: str = Form(...),
    db_user: str = Form(...),
    db_pass: str = Form(...),
    service_name: str = Form(...),
    clientId: str = Form(...),
    superuser_email: EmailStr = Form(...),
    superuser_username: str = Form(...),
    service_account_file: UploadFile = File(None)  # Optional file field
):
    instance_connection_name = f"{project_id}:{region}:{instance_name}"
    # Assume you have a function to get configuration values:
    cfg = configs.get_configs()
    container_image = cfg['CONTAINER_IMAGE']

    envs_backend = {
        "PROJECT_ID": project_id,
        "REGION": region,
        "DB_NAME": db_name,
        "DB_PASS": db_pass,
        "DB_USER": db_user,
        "INSTANCE_NAME": instance_name,
        "SUPERUSER_EMAIL": superuser_email,
        "SUPERUSER_USERNAME": superuser_username,
        "GOOGLE_CLIENT_ID": clientId
    }

    try:
        logger.info(f"Deploying service with file: {service_account_file.filename if service_account_file else 'None'}")
        logger.info("print env dict: {envs_backend}")
        envs_vars_str = ",".join([f'{k}={v}' for k, v in envs_backend.items()])
        logger.info("Done parsing dict to strings for env variables {envs_vars_str}")

        import tempfile

        # Read the file contents from the UploadFile
        file_contents = await service_account_file.read()

        # Save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
            tmp.write(file_contents)
            tmp_path = tmp.name

        utils.run_deploy(
            service_account_file=tmp_path,
            service_name=service_name,
            project_id=project_id,
            container_image=container_image,
            instance_connection_name=instance_connection_name,
            region=region,
            env_vars=envs_vars_str
        )

        logger.info("Fetching Cloud Run service URL")
        service_url = utils.get_cloud_run_url(
            service_name=service_name,
            project_id=project_id,
            region=region
        )
        return {"message": "Deployment successful", "service_url": service_url}
    except Exception as e:
        logger.error(f"Error deploying service: {e}")
        raise HTTPException(status_code=500, detail=str(e))
