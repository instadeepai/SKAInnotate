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

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.urandom(24))
templates = Jinja2Templates(directory="./setup/templates")

project_id = os.getenv("PROJECT_ID")
service_account_file = os.getenv("SERVICE_ACCOUNT_FILE")
credentials = None

FILE = {"backend" : "configs_backend.yaml",
      "frontend": "configs_frontend.yaml"}

def write_cloudbuild_yaml(docker_image):
  cloudbuild_yaml = f"""
  steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-f', 'Dockerfile.frontend', '-t', '{docker_image}', '.']
  images:
  - '{docker_image}'
  """

  # Write the content to the cloudbuild.yaml file
  with open("cloudbuild.yaml", "w") as f:
    f.write(cloudbuild_yaml)
  print("cloudbuild.yaml file generated successfully!")

  return


def deploy(service_name, container_image_frontend, container_image_backend, instance_connection_name, region):
  os.system(f"bash deploy.sh " 
    f"{service_name}-backend " 
    f"{container_image_backend}  " 
    f"{region}  " +
    f"{instance_connection_name} " +
    FILE['backend'])

  os.system(f"bash deploy.sh " 
    f"{service_name}-frontend " 
    f"{container_image_frontend}  " 
    f"{region}  " +
    f"{instance_connection_name} " +
    FILE['frontend'])
  return

def write_config_variable(variable_name, data, end_type='backend'):
  if os.path.exists(FILE[end_type]):
    with open(FILE[end_type], "r") as file:
      config = yaml.safe_load(file)
  else:
    config = {}

  config[variable_name] = data

  with open(FILE[end_type], "w") as file:
    yaml.safe_dump(config, file)

def get_config_variable(variable_name, end_type='backend'):
  if os.path.exists(FILE[end_type]):
    with open(FILE[end_type], "r") as file:
      config = yaml.safe_load(file)
      return config.get(variable_name)
  return None

def get_credentials():
  global credentials
  if credentials is None:
    if service_account_file:
      credentials = service_account.Credentials.from_service_account_file(service_account_file)
    else:
      raise RuntimeError("Service account file not set in environment variables.")
  return credentials

def get_storage_client():
  return storage.Client(credentials=get_credentials())

def get_sqladmin_client():
  return build('sqladmin', 'v1beta4', credentials=get_credentials())

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
  return templates.TemplateResponse("index.html", {"request": request})

@app.post("/setup-project", response_class=JSONResponse)
async def get_project_details(project_id: str = Form(...), service_account_file: str = Form(...)):
  global credentials
  if not service_account_file:
    return {"message": "No service account added"}
  try:
    credentials = service_account.Credentials.from_service_account_file(service_account_file)
    os.environ["PROJECT_ID"] = project_id
    os.environ["SERVICE_ACCOUNT_FILE"] = service_account_file

    write_config_variable("PROJECT_ID", project_id, 'backend')
    write_config_variable("SERVICE_ACCOUNT_FILE", service_account_file, 'backend')
    return {"message": "Project setup verified", "next_step": "Bucket setup"}
  except NotFound:
    return {"error": "Project not found"}
  except Exception as e:
    return {"error": str(e)}

@app.post("/setup-gcs", response_class=JSONResponse)
async def setup_cloud_storage(bucket_name: str = Form(...)):
  try:
    client = get_storage_client()
    bucket = storage.Bucket(client, bucket_name)
    if bucket.exists():
      write_config_variable("BUCKET_NAME", bucket_name, 'backend')
      return {"message": "Bucket exists", "next_step": "Database setup"}
    else:
      return {"error": "Bucket not found"}
  except Exception as e:
    return {"error": str(e)}

@app.post("/setup-gcp-sql", response_class=JSONResponse)
async def setup_cloud_sql(instance_name: str = Form(...), region: str = Form(...),
                        database_name: str = Form(...), db_user: str = Form(...),
                        db_pass: str = Form(...)):
  sqladmin = get_sqladmin_client()

  write_config_variable("REGION", region, 'backend')
  write_config_variable("DB_USER", db_user, 'backend')
  write_config_variable("DB_PASS", db_pass, 'backend')
  write_config_variable("DB_NAME", database_name, 'backend')
  write_config_variable("DATABASE_NAME", database_name, 'backend')
  write_config_variable('INSTANCE_NAME', instance_name, 'backend')

  instance_body = {
      'name': instance_name,
      'settings': {'tier': 'db-f1-micro'},
      'databaseVersion': 'POSTGRES_15',
      'region': region
  }
  project_id = os.getenv("PROJECT_ID")
  try:
    sqladmin.instances().get(project=project_id, instance=instance_name).execute()
    instance_exists = True
  except HttpError as e:
    if e.resp.status == 404:
      instance_exists = False
    else:
      print("Error: ", str(e))
      return {"error": f"Failed to check instance existence: {str(e)}"}

  if not instance_exists:
    try:
      request = sqladmin.instances().insert(project=project_id, body=instance_body)
      response = request.execute()
      instance_created = True
    except HttpError as e:
      return {"error": f"Failed to create instance: {str(e)}"}
  else:
    instance_created = False

  database_body = {'name': database_name}

  try:
    sqladmin.databases().get(project=project_id, instance=instance_name, database=database_name).execute()
    database_exists = True
  except HttpError as e:
    if e.resp.status == 404:
      database_exists = False
    else:
      return {"error": f"Failed to check database existence: {str(e)}"}

  if not database_exists:
    try:
      request = sqladmin.databases().insert(project=project_id, instance=instance_name, body=database_body)
      response = request.execute()
      return {"message": f"Cloud SQL Database '{database_name}' created in instance '{instance_name}': {response}"}
    except HttpError as e:
      return {"error": f"Failed to create database: {str(e)}"}
  else:
    return {"message": f"Cloud SQL Database '{database_name}' already exists in instance '{instance_name}'."}

@app.post("/setup-google-auth", response_class=JSONResponse)
async def setup_google_auth(google_client_id: str = Form(...)):
  try:
    write_config_variable("REACT_APP_GOOGLE_CLIENT_ID", google_client_id, 'frontend')
    # write_config_variable("GOOGLE_CLIENT_SECRET", google_client_secret)
    return {"message": "Google Authentication setup completed successfully.", "next_step": "Super user setup"}
  except Exception as e:
    return {"error": str(e)}

@app.post("/setup-superuser", response_class=JSONResponse)
async def setup_superuser(superuser_username: str = Form(...), superuser_email: str = Form(...)):
  try:
    write_config_variable("SUPERUSER_USERNAME", superuser_username, 'backend')
    write_config_variable("SUPERUSER_EMAIL", superuser_email, 'backend')
    return {"message": "Super user setup completed successfully.", "next_step": "Container image setup"}
  except Exception as e:
    return {"error": str(e)}

@app.post("/setup-gcp-container", response_class=JSONResponse)
async def setup_cloud_container(container_image_backend: str = Form(...), container_image_frontend: str = Form(...), build_option: str = Form(...)):
  if build_option not in ['none', 'local', 'cloud']:
    return JSONResponse(status_code=400, content={"error": "Invalid build option."})

  if build_option == 'local':
    os.system(f"bash build.sh {container_image_backend}")
    os.system(f"bash build.sh {container_image_frontend}")

  elif build_option == 'cloud':
    write_cloudbuild_yaml(container_image_frontend)
    os.system(f"gcloud builds submit --tag {container_image_backend} .")
    os.system(f"gcloud builds submit --config cloudbuild.yaml .")
  
  write_config_variable("CONTAINER_IMAGE_FRONTEND", container_image_frontend)
  write_config_variable("CONTAINER_IMAGE_BACKEND", container_image_backend)
  return {"message": "GCP Container setup completed successfully.", "next_step": "Cloud Run deployment"}

@app.post("/setup-cloud-run", response_class=JSONResponse)
async def setup_cloud_run(service_name: str = Form(...), region: str = Form(...)):
  write_config_variable('REGION', region, 'backend')
  write_config_variable('SERVICE_NAME', service_name, 'backend')

  container_image_frontend = get_config_variable('CONTAINER_IMAGE_FRONTEND')
  container_image_backend = get_config_variable('CONTAINER_IMAGE_BACKEND')

  project_id = get_config_variable("PROJECT_ID")
  instance_name = get_config_variable('INSTANCE_NAME')
  instance_connection_name = f"{project_id}:{region}:{instance_name}"

  try:
    deploy(service_name, container_image_frontend, container_image_backend, instance_connection_name, region)
    
    service_url = f"Example URL: https://<service-name>-<hashing>-<region>.a.run.app"
    return {"message": "Deployment successful", "service_url": service_url}
  except Exception as e:
    return {"error": str(e)}
  
@app.post("/setup-url-step", response_class=JSONResponse)
async def setup_urls(service_url_frontend: str = Form(...), service_url_backend: str = Form(...)):
  write_config_variable("REACT_APP_BASE_API_URL", service_url_backend, 'frontend')
  write_config_variable("ORIGINS", f"[{service_url_frontend}]", 'backend')
 
  container_image_frontend = get_config_variable('CONTAINER_IMAGE_FRONTEND', 'backend')
  container_image_backend = get_config_variable('CONTAINER_IMAGE_BACKEND', 'backend')

  project_id = get_config_variable("PROJECT_ID", 'backend')
  region = get_config_variable("REGION", 'backend')
  instance_name = get_config_variable('INSTANCE_NAME', 'backend')
  instance_connection_name = f"{project_id}:{region}:{instance_name}"
  service_name = get_config_variable("SERVICE_NAME", 'backend')

  

  deploy(service_name, container_image_frontend, container_image_backend, instance_connection_name, region)

  return {"message": "Deployment successfully.", "next_step": "Cloud Run deployment"}

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=8000)