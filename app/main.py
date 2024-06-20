import uvicorn
import json
import os
from pathlib import Path
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from pydantic import BaseModel
from pydantic import ValidationError
from typing import Optional
from sqlalchemy.orm import Session

from skainnotate.utils import gcloud_tasks
from skainnotate.data.database_handler import DatabaseManager
from skainnotate.project.model import ProjectConfigs
from skainnotate.data.data_handlers import download_images_from_gcs
from skainnotate.tasks.annotation import AnnotationWorkflow
from skainnotate.tasks.tasks import TaskManager
from skainnotate.utils.logger import logger

PROJECT_ID=os.environ.get('PROJECT_ID', '')
INSTANCE_NAME=os.environ.get('INSTANCE_NAME', '')
REGION=os.environ.get('REGION', '')

DATABASE_USER = os.environ.get('DATABASE_USER', '')
PASSWORD = os.environ.get('PASSWORD', '')

ANNOTATOR_USERNAME = os.environ.get('ANNOTATOR_USERNAME', '')
DATABASE_NAME = os.environ.get('DATABASE_NAME', '')
IMAGES_PATH = os.environ.get('IMAGES_PATH', '/static/images')

app = FastAPI()
# Serve static files (if you have any, like images, CSS files, etc.)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

def setup_authentication():
  """Authenticate the user and set the project ID."""
  gcloud_tasks.authenticate_user()
  gcloud_tasks.set_project_id(project_id=PROJECT_ID)

def get_user_account() -> str:
  """Get the active user account."""
  user_account = gcloud_tasks.get_active_user()
  logger.log_info(f"Active User Account: {user_account}")
  return user_account

def init_database() -> Session:
  """Initialize the database connection and return the session."""
  instance_connection_name = f"{PROJECT_ID}:{REGION}:{INSTANCE_NAME}"
  logger.log_info(f"Instance Connection Name: {instance_connection_name}")

  db_manager = DatabaseManager(DATABASE_USER, PASSWORD, DATABASE_NAME, instance_connection_name)
  db_manager.setup()
  return db_manager

def fetch_assigned_tasks(annotator_id=None, annotator_username=None):
  logger.log_info("Fetching assigned tasks...")
  assert annotator_id or annotator_username, 'Enter either annotator id or username'
  assigned_tasks = annotation_workflow.get_tasks_assigned_to_annotator(annotator_id, annotator_username)
  return assigned_tasks

class LabelResponse(BaseModel):
  """Model for label response."""
  label: Optional[str]

class LabelUpdate(BaseModel):
  event: str = "update_label"
  image_id: str
  label: str

class NavigationEvent(BaseModel):
  event: str
  direction: str  # "next" or "previous"


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request, session: Session = Depends(init_database)):
  """Render the index page."""
  labels = project_configs.labels
  user_account = get_user_account()
  return templates.TemplateResponse(
      "index.html", {"request": request, 
                     "user_email": user_account, 
                     "username": ANNOTATOR_USERNAME, 
                     "labels": labels,
                     "images_path": IMAGES_PATH
                     }
  )

@app.on_event("startup")
async def startup_event():
  """Initialize components during application startup."""
  global annotation_workflow, db_session, project_configs, annotator_object
  setup_authentication()
  db_manager = init_database()
  db_session = db_manager.get_session()
  annotation_workflow = AnnotationWorkflow(db_session)
  annotator_object = annotation_workflow.get_annotator(annotator_username=ANNOTATOR_USERNAME)
  project_configs = ProjectConfigs(db_session)

  assigned_tasks = fetch_assigned_tasks(annotator_username=ANNOTATOR_USERNAME)
  if not len(os.path.join('app', IMAGES_PATH)):
    download_images_from_gcs(assigned_tasks, os.path.join('app', IMAGES_PATH))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
  """Handle WebSocket connections."""
  await websocket.accept()
  try:
    while True:
      data = await websocket.receive_text()
      event_data = json.loads(data)

      # Handle label update event
      if event_data.get("event") == "update_label":
        try:
          label_update = LabelUpdate(**event_data)
          example_id = label_update.image_id.split("_")[0]
          annotation_workflow.add_annotation(label_update.label, example_id, annotator_object.annotator_id)
          await websocket.send_text(f"Label updated for example {example_id}: {label_update.label}")
        except ValidationError as e:
          await websocket.send_text(f"Invalid data format: {e}")

      # Handle navigation events
      elif event_data.get("event") == "navigate":
        try:
          navigation_event = NavigationEvent(**event_data)
          if navigation_event.direction == "next":
            # Handle next event
            await websocket.send_text("Next button clicked")
          elif navigation_event.direction == "previous":
            # Handle previous event
            await websocket.send_text("Previous button clicked")
          else:
            await websocket.send_text("Invalid direction")
        except ValidationError as e:
          await websocket.send_text(f"Invalid data format: {e}")

      else:
        await websocket.send_text("Unknown event")
                
  except WebSocketDisconnect:
    print("Client disconnected")

@app.get("/list-images")
async def list_images():
  images_dir = Path(f'app/{IMAGES_PATH}')
  image_files = [f.name for f in images_dir.glob("*") if f.is_file()]
  return image_files

@app.get("/api/label/{image_id}", response_model=LabelResponse)
async def get_label(image_id: str):
  """Get the label for a given image ID."""
  example_id = image_id.split('_')[0]

  label = annotation_workflow.get_annotations_for_example(example_id, annotator_object.annotator_id)
  if label is not None:
    return {"label": label.label}
  else:
    return {"label": None}

if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=5000)
