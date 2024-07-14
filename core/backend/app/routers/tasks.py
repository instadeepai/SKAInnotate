import csv
import json
from typing import List
import pandas as pd
from io import StringIO, BytesIO
import xml.etree.ElementTree as ET
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session

import app.crud as crud
import app.schema as schema
import app.model as model
from app.database import get_db
from app.dependencies import get_current_role

router = APIRouter()
templates = Jinja2Templates(directory="/app/frontend/public")

@router.post("/projects/{project_id}/tasks", response_model=schema.Task)
def create_task(project_id: int, task: schema.TaskCreate, db: Session = Depends(get_db)):
  return crud.create_task(db=db, project_id=project_id, task=task)

# Update Tasks from CSV Endpoint
@router.post("/projects/{project_id}/tasks/update-from-csv", response_class=HTMLResponse)
async def update_csv(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
  if file.content_type != 'text/csv':
    raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are accepted.")
  
  contents = await file.read()
  df = pd.read_csv(StringIO(contents.decode('utf-8')))

  for _, row in df.iterrows():
    task_id = row['example_id']
    image = row['image']
    additional_data = {col: row[col] for col in df.columns if col not in ['example_id', 'image']}

    existing_task = crud.get_task(db=db, task_id=task_id)
    if existing_task:
      existing_task.image = image
      existing_task.additional_data = json.dumps(additional_data)
      db.commit()
      db.refresh(existing_task)
    else:
      task = schema.TaskCreate(
          task_id=task_id,
          project_id=project_id,
          image=image,
          additional_data=additional_data
      )
      crud.create_task(db=db, task=task)

  return RedirectResponse(url=f'/projects/{project_id}/tasks', status_code=303)

# Read Tasks Endpoint
@router.get("/projects/{project_id}/tasks", response_class=HTMLResponse)
def read_tasks(request: Request, project_id: int, db: Session = Depends(get_db)):
  tasks = crud.get_tasks_in_project(db=db, project_id=project_id)
  return templates.TemplateResponse("admin/task_panel.html", 
                                    {"request": request, "tasks": tasks, "project_id": project_id})

# Get Task Details Endpoint
@router.get("/projects/{project_id}/tasks/{task_id}", response_class=HTMLResponse)
async def get_task_details(request: Request, 
                           project_id: int, 
                           task_id: str, 
                           db: Session = Depends(get_db), 
                           role: str = Depends(get_current_role)):
  task = crud.get_task(db, task_id=task_id)
  if not task:
    raise HTTPException(status_code=404, detail="Task not found")

  image_url = task.image.replace("gs://", "https://storage.cloud.google.com/")
  if role == schema.UserRole.admin:
    users_assigned_to_task = crud.get_users_assigned_to_task(db, task_id=task_id, project_id=project_id)
    return templates.TemplateResponse("admin/task_single.html", {
        "request": request,
        "task": {
            "task_id": task.task_id,
            "image": image_url,
            "assigned_users": [crud.get_user(db, user.user_id) for user in users_assigned_to_task]
        }
    })
  else:
    user_info = request.session.get("user")
    user_email = user_info.get("email")
    user = crud.get_user_by_email_and_role(db, user_email=user_email, role_name=role)
    all_tasks = crud.get_tasks_in_project(db, project_id)
    task_dict = {
      "task_id": task.task_id,
      "image": image_url,
    }
    current_task_index = all_tasks.index(task)
    all_tasks_dict = [
      {"task_id": t.task_id, "image": t.image.replace("gs://", "https://storage.cloud.google.com/")} for t in all_tasks]

    return templates.TemplateResponse("annotator/task_single.html", {
        "request": request,
        "task": task_dict,
        "tasks_json": json.dumps(all_tasks_dict),
        "current_task_index": current_task_index,
        "user": user
    })

# Update Task Endpoint
@router.put("/projects/{project_id}/tasks/{task_id}", response_model=schema.Task)
def update_task(task_id: str, task: schema.TaskUpdate, db: Session = Depends(get_db)):
  db_task = crud.update_task(db=db, task_id=task_id, task_update=task)
  if db_task is None:
    raise HTTPException(status_code=404, detail="Task not found")
  return db_task

# Delete Task Endpoint
@router.delete("/projects/{project_id}/tasks/{task_id}", response_model=schema.Task)
def delete_task(task_id: str, db: Session = Depends(get_db)):
  db_task = crud.delete_task(db=db, task_id=task_id)
  if db_task is None:
    raise HTTPException(status_code=404, detail="Task not found")
  return db_task

# Add Task Form Endpoint
@router.get("/projects/{project_id}/tasks/add_task", response_class=HTMLResponse)
async def add_task_form(request: Request):
  return templates.TemplateResponse("admin/add_task.html", {"request": request})

# Auto Assign Tasks Endpoint
@router.get("/projects/{project_id}/tasks/auto/assign-tasks", response_class=HTMLResponse)
async def auto_assign_task(project_id: int, db: Session = Depends(get_db)):
  crud.auto_assign_tasks_to_users(db, project_id=project_id)
  return RedirectResponse(url=f'/projects/{project_id}/tasks', status_code=303)

# Assign Task Endpoint
@router.get("/assign_task/{task_id}/{reviewer_id}", response_class=HTMLResponse)
async def assign_task(task_id: str, db: Session = Depends(get_db)):
  # TODO: will implement assignment logic
  return RedirectResponse(url='admin/task_panel', status_code=303)

# Unassign Task Endpoint
@router.get("/unassign_task/{task_id}/{reviewer_id}", response_class=HTMLResponse)
async def unassign_task(task_id: str, db: Session = Depends(get_db)):
  # TODO: Implement unassign logic
  return RedirectResponse(url='admin/task_panel', status_code=303)

# Remove Task Endpoint
@router.get("/remove_task/{task_id}", response_class=HTMLResponse)
async def remove_task(task_id: str, db: Session = Depends(get_db)):
  crud.delete_task(db=db, task_id=task_id)
  return RedirectResponse(url='admin/task_panel', status_code=303)

@router.get("/tasks/{task_id}/default_label", response_model=schema.AnnotationRetrieve)
def get_default_label(task_id: str, user_id: str, db: Session = Depends(get_db)):
  query_response = (db.query(model.Annotation)
                    .filter(model.Annotation.task_id == task_id, model.Annotation.user_id == user_id)
                    .first())
  if not query_response:
    return None
  return {"label": query_response.label}

def preprocess_labels(labels_str):
  return [label.strip(' "') for label in labels_str.split(",")]

@router.get("/tasks/{task_id}/labels", response_model=List[str])
async def get_task_labels(task_id: str, db: Session = Depends(get_db)):
  string_labels = crud.get_task(db, task_id).project.configurations.labels
  labels = preprocess_labels(string_labels)
  return labels

@router.post("/tasks/export-annotations")
def export_annotations(format: str = Form(...), db: Session = Depends(get_db)):

  annotations = db.query(model.Annotation).all()
  
  if format == 'csv':
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['task_id', 'user_id', 'label'])
    for annotation in annotations:
      writer.writerow([annotation.task_id, annotation.user_id, annotation.label])
    output.seek(0)
    response = StreamingResponse(output, media_type='text/csv', 
                                 headers={'Content-Disposition': 'attachment; filename="annotations.csv"'})
  
  elif format == 'json':
    output = json.dumps([{
        'task_id': a.task_id,
        'user_id': a.user_id,
        'label': a.label
    } for a in annotations], indent=4)
    response = StreamingResponse(BytesIO(output.encode('utf-8')), 
                                 media_type='application/json', 
                                 headers={'Content-Disposition': 'attachment; filename="annotations.json"'})

  elif format == 'xml':
    root = ET.Element("annotations")
    for annotation in annotations:
      ann = ET.SubElement(root, "annotation")
      ET.SubElement(ann, "task_id").text = str(annotation.task_id)
      ET.SubElement(ann, "user_id").text = str(annotation.user_id)
      ET.SubElement(ann, "label").text = annotation.label
    output = BytesIO()
    tree = ET.ElementTree(root)
    tree.write(output, encoding='utf-8', xml_declaration=True)
    output.seek(0)
    response = StreamingResponse(output, media_type='application/xml', 
                                 headers={'Content-Disposition': 'attachment; filename="annotations.xml"'})

  else:
    raise HTTPException(status_code=400, detail="Unsupported file format")
  return response