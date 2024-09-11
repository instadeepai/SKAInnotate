from typing import List
import csv
import json
import pandas as pd
import json
from io import StringIO
from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from fastapi.responses import StreamingResponse
from io import StringIO, BytesIO
import xml.etree.ElementTree as ET

import app.crud as crud
import app.schema as schema
import app.model as model
from app.database import get_db
from app.utils import get_final_annotation
router = APIRouter()

@router.get("/", response_model=List[schema.Project])
async def get_projects_data(db: Session = Depends(get_db)):
  projects = crud.get_projects(db)
  return projects

@router.post("/", response_model=schema.Project)
async def create_project(project: schema.ProjectCreate, db: Session = Depends(get_db)):
  project = crud.create_project(db=db, project=project)
  return project

@router.put("/{project_id}", response_model=schema.Project)
def update_project(project_id: int, project_update: schema.ProjectUpdate, db: Session = Depends(get_db)):
  project = crud.update_project(db, project_id=project_id, project_update=project_update)
  return project

@router.get("/{project_id}", response_model=schema.Project)
def read_project(request: Request, project_id: int, db: Session = Depends(get_db)):
  project = crud.get_project(db, project_id=project_id)
  return project

@router.delete("/{project_id}", response_model=schema.Project)
def delete_project(project_id: int, db: Session = Depends(get_db)):
  project = crud.delete_project(db, project_id)
  if project is None:
      raise HTTPException(status_code=404, detail="Project not found")
  return project

@router.post("/{project_id}/tasks", response_model=schema.Task)
def create_task(project_id: int, task: schema.TaskCreate, db: Session = Depends(get_db)):
  return crud.create_task(db=db, project_id=project_id, task=task)

@router.get("/{project_id}/tasks", response_model=List[schema.TaskRetrieve])
def get_tasks_by_project(project_id: int, db: Session = Depends(get_db)):
  tasks = crud.get_tasks_in_project(db, project_id=project_id)
  return tasks

@router.get("/{project_id}/statistics", response_model=schema.Stats)
def get_project_statistics(project_id: int, db: Session = Depends(get_db)):
  totalTasks = len(crud.get_tasks_in_project(db=db, project_id=project_id))
  completedTasks = len(crud.get_completed_annotations(db, project_id=project_id))
  pendingTasks = totalTasks - completedTasks
  totalAnnotations = len(crud.get_annotations(db, project_id))
  accuracyRate = 0.00

  stats = schema.Stats(
    totalTasks = totalTasks,
    completedTasks = completedTasks,
    pendingTasks = pendingTasks,
    totalAnnotations = totalAnnotations,
    accuracyRate = accuracyRate
  )
  return stats

@router.get("/{project_id}/user/{user_id}/assigned-annotations/tasks", response_model=List[schema.TaskRetrieve])
def get_assigned_annotation_tasks(project_id: int, user_id: int, db: Session = Depends(get_db)):
  tasks = crud.get_assigned_tasks_by_type_and_project(
    db, user_id=user_id, assignment_type=schema.RoleToAssignment.annotator, project_id=project_id)
  return tasks

@router.get("/{project_id}/user/{user_id}/assigned-reviews/tasks", response_model=List[schema.TaskRetrieve])
def get_assigned_review_tasks(project_id: int, user_id: int, db: Session = Depends(get_db)):
  tasks = crud.get_assigned_tasks_by_type_and_project(
    db, user_id=user_id, assignment_type=schema.RoleToAssignment.reviewer, project_id=project_id)
  return tasks

# Update Tasks from CSV Endpoint
@router.post("/{project_id}/upload-tasks-from-csv", response_class=JSONResponse)
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
 
  return {"message": "Tasks updated successfully"}

@router.get("/{project_id}/annotated-tasks")
def get_annotated_tasks(request: Request, project_id: int, db: Session = Depends(get_db)):
  tasks_with_annotations = crud.get_tasks_with_annotations(db, project_id)
  reviewers = crud.get_reviewers(db)

  tasks = []
  for task in tasks_with_annotations:
    task_info = {
        "task_id": task["task_id"],
        "image": task["image"],
        "labels": task["labels"],
        "reviewers": reviewers
    }
    tasks.append(task_info)
  return tasks

import ast

@router.get("/{project_id}/export-annotations")
def export_annotations(project_id: int, format: str, db: Session = Depends(get_db)):
  annotated_tasks = db.query(model.Task).join(model.Annotation).filter(model.Task.project_id == project_id).all()

  # Placeholder for actual data columns
  filter_columns = ['task_id', 'image']
  computed_columns = ['final_annotations']

  # Assuming all tasks have the same structure of additional_data
  additional_data_columns = list(ast.literal_eval(annotated_tasks[0].additional_data).keys()) if annotated_tasks else []

  if format == 'csv':
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(filter_columns + computed_columns + additional_data_columns)
    for task in annotated_tasks:
      row = [getattr(task, col) for col in filter_columns]
      final_annotation = get_final_annotation([ann.label for ann in task.annotations], [rev.label for rev in task.reviews])
      row.append(final_annotation)
      row.extend([ast.literal_eval(task.additional_data).get(col) for col in additional_data_columns])
      writer.writerow(row)
    output.seek(0)
    response = StreamingResponse(output, media_type='text/csv', headers={'Content-Disposition': f'attachment; filename="{project_id}_annotations.csv"'})

  elif format == 'json':
    data = [{
        **{col: getattr(task, col) for col in filter_columns},
        "final_annotations": get_final_annotation([ann.label for ann in task.annotations], [rev.label for rev in task.reviews]),
        **ast.literal_eval(task.additional_data)
    } for task in annotated_tasks]
    output = json.dumps(data, indent=4)
    response = StreamingResponse(BytesIO(output.encode('utf-8')), media_type='application/json', headers={'Content-Disposition': f'attachment; filename="{project_id}_annotations.json"'})
  else:
    raise HTTPException(status_code=400, detail="Unsupported file format")

  return response
