import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from google.cloud import storage
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.api_core.exceptions import NotFound
from googleapiclient.errors import HttpError
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.urandom(24))
templates = Jinja2Templates(directory="./setup/templates")

project_id = os.getenv("PROJECT_ID")
service_account_file = os.getenv("SERVICE_ACCOUNT_FILE")
credentials = None

def write_env_variable(variable_name, data):
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, "r") as file:
            lines = file.readlines()
    else:
        lines = []

    with open(env_file, "w") as file:
        variable_written = False
        for line in lines:
            if line.startswith(f"{variable_name}="):
                file.write(f"{variable_name}={data}\n")
                variable_written = True
            else:
                file.write(line)
        if not variable_written:
            file.write(f"{variable_name}={data}\n")

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

        write_env_variable("PROJECT_ID", project_id)
        write_env_variable("SERVICE_ACCOUNT_FILE", service_account_file)
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
    
    write_env_variable("REGION", region)
    write_env_variable("DB_USER", db_user)
    write_env_variable("DB_PASS", db_pass)
    write_env_variable("DB_NAME", database_name)
    write_env_variable("DATABASE_NAME", database_name)
    write_env_variable('INSTANCE_NAME', instance_name)

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
        write_env_variable("GOOGLE_CLIENT_ID", google_client_id)
        write_env_variable("GOOGLE_CLIENT_SECRET", google_client_secret)
        return {"message": "Google Authentication setup completed successfully.", "next_step": "Super user setup"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/setup-superuser", response_class=JSONResponse)
async def setup_superuser(superuser_username: str = Form(...), superuser_email: str = Form(...)):
    try:
        write_env_variable("SUPERUSER_USERNAME", superuser_username)
        write_env_variable("SUPERUSER_EMAIL", superuser_email)
        return {"message": "Super user setup completed successfully.", "next_step": "Container image setup"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/setup-gcp-container", response_class=JSONResponse)
async def setup_cloud_container(image: str = Form(...)):
    try:
        write_env_variable("IMAGE", image)
        return {"message": "Container image setup successful", "next_step": "Cloud Run deployment"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/setup-cloud-run", response_class=JSONResponse)
async def setup_cloud_run(service_name: str = Form(...)):
    try:
        service = build('run', 'v1', credentials=get_credentials())
        service_body = {
            "apiVersion": "serving.knative.dev/v1",
            "kind": "Service",
            "metadata": {"name": service_name, "namespace": "default"},
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "image": f"gcr.io/{project_id}/{service_name}",
                            "ports": [{"containerPort": 8080}]
                        }]
                    }
                }
            }
        }
        request = service.namespaces().services().create(parent=f"namespaces/{project_id}", body=service_body)
        response = request.execute()
        service_url = f"https://{service_name}-run.app"
        return {"message": "Deployment successful", "service_url": service_url}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
