import csv
import json
from typing import List, Dict
import pandas as pd
from io import StringIO, BytesIO
import xml.etree.ElementTree as ET
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

import app.crud as crud
import app.schema as schema
import app.model as model
from app.database import get_db
from app.dependencies import get_current_role, get_current_user

router = APIRouter()

@router.post("/projects/{project_id}/tasks", response_model=schema.Task)
def create_task(project_id: int, task: schema.TaskCreate, db: Session = Depends(get_db)):
  return crud.create_task(db=db, project_id=project_id, task=task)

# @router.get("/tasks")
# def get_tasks():
#   tasks = crud.get_assigned_tasks(db, user_id=user_id)
#   return tasks
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

@router.get("/api/projects/{project_id}/tasks/{task_id}")
async def get_task_details(request: Request,
                          project_id: int,
                          task_id: str,
                          db: Session = Depends(get_db),
                          role: str = Depends(get_current_role)):
  task = crud.get_task(db, task_id=task_id)
  if not task:
    raise HTTPException(status_code=404, detail="Task not found")

  image_url = task.image.replace("gs://", "https://storage.cloud.google.com/")
  response_data = {
      "task_id": task.task_id,
      "image": image_url,
  }

  if role == schema.UserRole.admin:
    users_assigned_to_task = crud.get_users_assigned_to_task(db, task_id=task_id, project_id=project_id)
    response_data["assigned_users"] = [crud.get_user(db, user.user_id) for user in users_assigned_to_task]
    return JSONResponse(content=response_data)
  else:
    user_info = get_current_user(request)
    user_id = user_info["user_id"]
    user = crud.get_user(db, user_id)

    all_assigned_tasks = crud.get_assigned_tasks_by_type_and_project(db,
                              user_id=user_id, assignment_type=schema.RoleToAssignment[role].value, project_id=project_id)
    current_task_index = next((i for i, t in enumerate(all_assigned_tasks) if t.task_id == task_id), -1)
    all_tasks_dict = [
        {"task_id": t.task_id, "image": t.image.replace("gs://", "https://storage.cloud.google.com/")} for t in all_assigned_tasks
    ]
    response_data.update({
        "tasks_json": all_tasks_dict,
        "current_task_index": current_task_index,
        "user": {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email
        }
    })
    return JSONResponse(content=response_data)

@router.get("/tasks/{task_id}/is_labeled")
async def is_task_labeled(task_id: str, user_id: int, task_type: str, db: Session = Depends(get_db)):
  if task_type == schema.AssignmentType.annotation:
    query_response = db.query(model.Annotation).filter(
        model.Annotation.task_id == task_id,
        model.Annotation.user_id == user_id
    ).first()
  elif task_type == schema.AssignmentType.review:
    query_response = db.query(model.Review).filter(
        model.Review.task_id == task_id,
        model.Review.user_id == user_id
    ).first()
  else:
    raise HTTPException(status_code=404, detail="Task not found")

  is_labeled = query_response is not None
  return {"is_labeled": is_labeled}

@router.post("/tasks/labels/is_labeled")
async def are_tasks_labeled(label_check: schema.LabelCheck, db: Session = Depends(get_db)) -> Dict[str, bool]:
  if label_check.task_type not in [schema.AssignmentType.annotation, schema.AssignmentType.review]:
    raise HTTPException(status_code=400, detail="Invalid task type")
  
  if label_check.task_type == schema.AssignmentType.annotation:
    query_response = db.query(model.Annotation.task_id).filter(
        model.Annotation.task_id.in_(label_check.task_ids),
        model.Annotation.user_id == label_check.user_id
    ).all()
  elif label_check.task_type == schema.AssignmentType.review:
    query_response = db.query(model.Review.task_id).filter(
        model.Review.task_id.in_(label_check.task_ids),
        model.Review.user_id == label_check.user_id
    ).all()

  labeled_task_ids = {result[0] for result in query_response}
  return {task_id: task_id in labeled_task_ids for task_id in label_check.task_ids}

from typing import Optional
@router.get("/tasks")
async def get_tasks_by_label_status(request: Request,
                                    project_id: int,
                                    labeled: Optional[bool] = None,
                                    db: Session = Depends(get_db),
                                    role: str = Depends(get_current_role)):
    user_info = get_current_user(request)
    user_id = user_info["user_id"]
    user = crud.get_user(db, user_id)
    
    assigned_tasks = crud.get_assigned_tasks_by_type_and_project(db, 
                                user_id=user_id, assignment_type=schema.RoleToAssignment[role].value, project_id=project_id)
    
    if labeled is not None:
      if role == schema.UserRole.annotator:
        assigned_tasks = [task for task in assigned_tasks if any(annotation.user_id == user.user_id for annotation in task.annotations) == labeled]
      else:
        assigned_tasks = [task for task in assigned_tasks if any(review.user_id == user.user_id for review in task.reviews) == labeled]
    print("Getting assigned tasks here! ", assigned_tasks)
    return assigned_tasks

# @router.get("/tasks-with-imgUrl-and-labelStatus")
# async def get_tasks_url_label_status(request: Request,
#                                     project_id: int,
#                                     db: Session = Depends(get_db),
#                                     role: str = Depends(get_current_role)):
#     user_info = get_current_user(request)
#     user_id = user_info["user_id"]
#     user = crud.get_user(db, user_id)
    
#     assigned_tasks = crud.get_assigned_tasks_by_type_and_project(db, 
#                                 user_id=user_id, assignment_type=schema.RoleToAssignment[role].value, project_id=project_id)
    
#     # if labeled is not None:
#     for task in assigned_tasks:
#       if role == schema.UserRole.annotator:
#         task.completion_status = any(annotation.user_id == user.user_id for annotation in task.annotations)
#       else:
#         task.completion_status = any(review.user_id == user.user_id for review in task.reviews)
#       print("Getting assigned tasks here! ", assigned_tasks)
#     return assigned_tasks

@router.get("/tasks-with-imgUrl-and-labelStatus", response_model=List[schema.TaskResponse])
async def get_tasks_url_label_status(request: Request,
                                  project_id: int,
                                  db: Session = Depends(get_db),
                                  role: str = Depends(get_current_role)):
  user_info = get_current_user(request)
  user_id = user_info["user_id"]
  user = crud.get_user(db, user_id)
  
  assigned_tasks = crud.get_assigned_tasks_by_type_and_project(db, 
                      user_id=user_id, assignment_type=schema.RoleToAssignment[role].value, project_id=project_id)
  
  # Transform tasks to match the expected response structure
  tasks_response = []
  for task in assigned_tasks:
    if role == schema.UserRole.annotator:
      completion_status = any(annotation.user_id == user.user_id for annotation in task.annotations)
    else:
      completion_status = any(review.user_id == user.user_id for review in task.reviews)
    image_url =  task.image.replace("gs://", "https://storage.cloud.google.com/")

    tasks_response.append({
        "task_id": task.task_id,
        "image_url": image_url,
        "completion_status": completion_status
    })
  return tasks_response

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

# Auto Assign Tasks Endpoint
@router.get("/projects/{project_id}/tasks/auto/assign-tasks", response_class=HTMLResponse)
async def auto_assign_task(project_id: int, db: Session = Depends(get_db)):
  crud.auto_assign_tasks_to_users(db, project_id=project_id)
  return RedirectResponse(url=f'/projects/{project_id}/tasks', status_code=303)

# Assign Task Endpoint
@router.post("/assign_task/{task_id}/{reviewer_id}", response_class=JSONResponse)
async def assign_task(task_id: str, reviewer_id: int, db: Session = Depends(get_db)):
  try:
    crud.assign_task(db, task_id=task_id, user_id=reviewer_id, assignment_type=schema.AssignmentType.review)
    return {"message": "Task assigned successfully"}
  except Exception as e:
    return JSONResponse(status_code=400, content={"message": str(e)})

# Unassign Task Endpoint
@router.post("/unassign_task/{task_id}/{reviewer_id}", response_class=JSONResponse)
async def unassign_task(task_id: str, reviewer_id: int, db: Session = Depends(get_db)):
  try:
    crud.unassign_task(db, task_id=task_id, user_id=reviewer_id, assignment_type=schema.AssignmentType.review)
    return {"message": "Task unassigned successfully"}
  except Exception as e:
    return JSONResponse(status_code=400, content={"message": str(e)})
    
# Remove Task Endpoint
@router.get("/remove_task/{task_id}", response_class=HTMLResponse)
async def remove_task(task_id: str, db: Session = Depends(get_db)):
  crud.delete_task(db=db, task_id=task_id)
  return RedirectResponse(url='admin/task_panel', status_code=303)

@router.get("/tasks/{task_id}/default_label", response_model=schema.AnnotationRetrieve)
def get_default_label(task_id: str, user_id: int, task_type: str, db: Session = Depends(get_db)):
  if task_type==schema.AssignmentType.review:
    query_response = crud.get_default_review(db, task_id=task_id, user_id=user_id)
  else:
    query_response = crud.get_default_label(db, task_id=task_id, user_id=user_id)
  return {"label": query_response.label if query_response else None}

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