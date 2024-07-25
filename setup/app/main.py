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

def write_config_variable(variable_name, data):
  config_file = "configs.yaml"
  if os.path.exists(config_file):
    with open(config_file, "r") as file:
      config = yaml.safe_load(file)
  else:
    config = {}

  config[variable_name] = data

  with open(config_file, "w") as file:
    yaml.safe_dump(config, file)

def get_config_variable(variable_name):
  config_file = "configs.yaml"
  if os.path.exists(config_file):
    with open(config_file, "r") as file:
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

    write_config_variable("PROJECT_ID", project_id)
    write_config_variable("SERVICE_ACCOUNT_FILE", service_account_file)
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
      write_config_variable("BUCKET_NAME", bucket_name)
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

  write_config_variable("REGION", region)
  write_config_variable("DB_USER", db_user)
  write_config_variable("DB_PASS", db_pass)
  write_config_variable("DB_NAME", database_name)
  write_config_variable("DATABASE_NAME", database_name)
  write_config_variable('INSTANCE_NAME', instance_name)

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
async def setup_google_auth(google_client_id: str = Form(...), google_client_secret: str = Form(...)):
  try:
    write_config_variable("GOOGLE_CLIENT_ID", google_client_id)
    write_config_variable("GOOGLE_CLIENT_SECRET", google_client_secret)
    return {"message": "Google Authentication setup completed successfully.", "next_step": "Super user setup"}
  except Exception as e:
    return {"error": str(e)}

@app.post("/setup-superuser", response_class=JSONResponse)
async def setup_superuser(superuser_username: str = Form(...), superuser_email: str = Form(...)):
  try:
    write_config_variable("SUPERUSER_USERNAME", superuser_username)
    write_config_variable("SUPERUSER_EMAIL", superuser_email)
    return {"message": "Super user setup completed successfully.", "next_step": "Container image setup"}
  except Exception as e:
    return {"error": str(e)}

@app.post("/setup-gcp-container", response_class=JSONResponse)
async def setup_cloud_container(container_image: str = Form(...), build_option: str = Form(...)):
  if build_option not in ['none', 'local', 'cloud']:
    return JSONResponse(status_code=400, content={"error": "Invalid build option."})

  if build_option == 'local':
    os.system(f"bash build.sh {container_image}")

  elif build_option == 'cloud':
    os.system(f"gcloud builds submit --tag {container_image} .")
  
  write_config_variable("CONTAINER_IMAGE", container_image)
  return {"message": "GCP Container setup completed successfully.", "next_step": "Cloud Run deployment"}

@app.post("/setup-cloud-run", response_class=JSONResponse)
async def setup_cloud_run(service_name: str = Form(...), region: str = Form(...)):
  container_image = get_config_variable('CONTAINER_IMAGE')
  project_id = get_config_variable("PROJECT_ID")
  instance_name = get_config_variable('INSTANCE_NAME')
  instance_connection_name = f"{project_id}:{region}:{instance_name}"

  try:
    os.system(f"bash deploy.sh " 
              f"{service_name} " 
              f"{container_image}  " 
              f"{region}  " +
              f"{instance_connection_name} " +
              'configs.yaml')
    
    service_url = f"Example URL: https://<service-name>-<hashing>-<region>.a.run.app"
    return {"message": "Deployment successful", "service_url": service_url}
  except Exception as e:
    return {"error": str(e)}

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=8000)
