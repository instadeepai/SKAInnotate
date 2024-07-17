from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from typing import List

import app.crud as crud
import app.schema as schemas
from app.database import get_db
from app.dependencies import get_current_user
router = APIRouter()
templates = Jinja2Templates(directory="/app/frontend/public")

@router.post("/annotations/submit/label", response_model=schemas.Annotation)
def create_annotation(annotation: schemas.AnnotationCreate, db: Session = Depends(get_db)):
  return crud.create_or_update_annotation(db=db, label=annotation.label, task_id=annotation.task_id, annotator_id=annotation.user_id)

@router.get("/{annotation_id}", response_model=schemas.Annotation)
def read_annotation(annotation_id: int, db: Session = Depends(get_db)):
  db_annotation = crud.get_annotation(db=db, annotation_id=annotation_id)
  if db_annotation is None:
    raise HTTPException(status_code=404, detail="Annotation not found")
  return db_annotation

@router.get("/task/{task_id}", response_model=bool)
def read_annotation_by_user(request: Request, task_id: str, db: Session = Depends(get_db)):
  user_info = get_current_user(request)

  if not user_info:
    raise HTTPException(status_code=401, detail="User not authenticated")
  
  user_email = user_info.get("email")
  user = crud.get_user_by_email_and_role(db, user_email=user_email, role_name='annotator')
  if not user:
    raise HTTPException(status_code=404, detail="User not found")

  db_annotation = crud.get_annotation_user_task_id(db=db, user_id=user.user_id, task_id=task_id)
  return bool(db_annotation)

@router.get("/projects/{project_id}/annotations", response_model=List[schemas.Annotation])
def read_annotations(request: Request, project_id: int, db: Session = Depends(get_db)):
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
  
  return templates.TemplateResponse("admin/annotations.html", {"request": request, "tasks": tasks})

@router.put("/{annotation_id}", response_model=schemas.Annotation)
def update_annotation(annotation_id: int, annotation: schemas.AnnotationUpdate, db: Session = Depends(get_db)):
  db_annotation = crud.update_annotation(db=db, annotation_id=annotation_id, annotation_update=annotation)
  if db_annotation is None:
    raise HTTPException(status_code=404, detail="Annotation not found")
  return db_annotation

@router.delete("/{annotation_id}", response_model=schemas.Annotation)
def delete_annotation(annotation_id: int, db: Session = Depends(get_db)):
  db_annotation = crud.delete_annotation(db=db, annotation_id=annotation_id)
  if db_annotation is None:
    raise HTTPException(status_code=404, detail="Annotation not found")
  return db_annotation
