from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

import app.crud as crud
import app.schema as schema
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/annotations/submit/label", response_model=schema.Annotation)
def create_annotation(annotation: schema.AnnotationCreate, db: Session = Depends(get_db)):
  return crud.create_or_update_annotation(db=db, label=annotation.label, task_id=annotation.task_id, annotator_id=annotation.user_id)

@router.get("/{annotation_id}", response_model=schema.Annotation)
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
  
  user_id = user_info.get("user_id")
  user = crud.get_user(db, user_id)
  if not user:
    raise HTTPException(status_code=404, detail="User not found")

  db_annotation = crud.get_annotation_user_task_id(db=db, user_id=user.user_id, task_id=task_id)
  return bool(db_annotation)

@router.put("/{annotation_id}", response_model=schema.Annotation)
def update_annotation(annotation_id: int, annotation: schema.AnnotationUpdate, db: Session = Depends(get_db)):
  db_annotation = crud.update_annotation(db=db, annotation_id=annotation_id, annotation_update=annotation)
  if db_annotation is None:
    raise HTTPException(status_code=404, detail="Annotation not found")
  return db_annotation

@router.delete("/{annotation_id}", response_model=schema.Annotation)
def delete_annotation(annotation_id: int, db: Session = Depends(get_db)):
  db_annotation = crud.delete_annotation(db=db, annotation_id=annotation_id)
  if db_annotation is None:
    raise HTTPException(status_code=404, detail="Annotation not found")
  return db_annotation
