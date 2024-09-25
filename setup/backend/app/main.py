import os
import yaml
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from google.cloud import storage
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.api_core.exceptions import NotFound
from googleapiclient.errors import HttpError
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import setup.backend.app.schema as schema
import setup.backend.app.utils as utils
import setup.backend.app.configs as configs
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()
app.mount("/static", StaticFiles(directory="setup/frontend/build/static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=os.urandom(24))
app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://127.0.0.1", "http://localhost"], 
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

templates = Jinja2Templates(directory="setup/frontend/build")
project_id = os.getenv("PROJECT_ID")
service_account_file = os.getenv("SERVICE_ACCOUNT_FILE")
credentials = None

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
  return FileResponse("setup/frontend/build/index.html")

@app.post("/setup-project", response_class=JSONResponse)
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

@app.post("/setup-gcp-sql", response_class=JSONResponse)
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

@app.post("/deploy", response_class=JSONResponse)
async def setup_cloud_run(deployData: schema.DeployAppData):
  instance_connection_name = f"{deployData.project_id}:{deployData.region}:{deployData.instance_name}"
  cfg = configs.get_configs()
  container_image_backend = cfg['CONTAINER_IMAGE_BACKEND']
  container_image_frontend = cfg['CONTAINER_IMAGE_FRONTEND']

  envs_backend =  {"PROJECT_ID": deployData.project_id,
                  "REGION": deployData.region,
                  "DB_NAME": deployData.db_name,
                  "DB_PASS": deployData.db_pass, 
                  "DB_USER": deployData.db_user,
                  "INSTANCE_NAME": deployData.instance_name,
                  "SUPERUSER_EMAIL": deployData.superuser_email,
                  "SUPERUSER_USERNAME": deployData.superuser_username
                  }
  
  envs_frontend = {"REACT_APP_GOOGLE_CLIENT_ID": deployData.clientId}
  try:
    logger.info("Deploying frontend service")
    envs_frontend_str=",".join([f'{i}={v}' for i, v in envs_frontend.items()])
    utils.run_deploy(service_name=f'{deployData.service_name}',
                 project_id=deployData.project_id,
                 container_image=container_image_frontend,
                 instance_connection_name=instance_connection_name,
                 region=deployData.region,
                 env_vars=envs_frontend_str)
    
    logger.info("Deploying backend service")
    envs_backend_str=",".join([f'{i}={v}' for i, v in envs_backend.items()])
    utils.run_deploy(service_name=f'{deployData.service_name}-backend',
                 project_id=deployData.project_id,
                 container_image=container_image_backend,
                 instance_connection_name=instance_connection_name,
                 region=deployData.region,
                 env_vars=envs_backend_str)

    logger.info("Fetching Cloud Run URLs")
    frontend_url = utils.get_cloud_run_url(service_name=f'{deployData.service_name}',
                                           project_id=deployData.project_id,
                                          region=deployData.region)
    backend_url = utils.get_cloud_run_url(service_name=f'{deployData.service_name}-backend',
                                          project_id=deployData.project_id,
                                          region=deployData.region)

    if not frontend_url or not backend_url:
      raise RuntimeError("Could not retrieve Cloud Run URLs")
    
    envs_backend.update({"ORIGIN": frontend_url})
    envs_frontend.update({"REACT_APP_BASE_API_URL": backend_url})

    logger.info("Redeploying frontend service with updated environment variables")
    envs_frontend_str=",".join([f'{i}={v}' for i, v in envs_frontend.items()])
    utils.run_deploy(service_name=f'{deployData.service_name}',
                 project_id=deployData.project_id,
                 container_image=container_image_frontend,
                 instance_connection_name=instance_connection_name,
                 region=deployData.region,
                 env_vars=envs_frontend_str)
    
    logger.info("Redeploying backend service with updated environment variables")
    envs_backend_str=",".join([f'{i}={v}' for i, v in envs_backend.items()])
    utils.run_deploy(service_name=f'{deployData.service_name}-backend',
                 project_id=deployData.project_id,
                 container_image=container_image_backend,
                 instance_connection_name=instance_connection_name,
                 region=deployData.region,
                 env_vars=envs_backend_str)
    
    service_url = frontend_url

    return {"message": "Deployment successful", "service_url": service_url}
  except Exception as e:
    return {"error": str(e)}
  
if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=8000)
