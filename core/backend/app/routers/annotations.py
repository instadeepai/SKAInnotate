from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from io import StringIO, BytesIO
import xml.etree.ElementTree as ET

import core.backend.app.crud as crud
import core.backend.app.schema as schema
from core.backend.app.database import get_db

router = APIRouter()

@router.get("/", response_model = List[schema.Annotation])
def read_annotations(project_id: int, db: Session = Depends(get_db)):
  return crud.get_annotations(db, project_id=project_id)

@router.post("/", response_model=schema.Annotation)
def create_annotation(annotation: schema.AnnotationCreate, db: Session = Depends(get_db)):
  return crud.create_annotation(db=db, label=annotation.label, task_id=annotation.task_id, annotator_id=annotation.user_id)

@router.get("/{annotation_id}", response_model=schema.Annotation)
def read_annotation(annotation_id: int, db: Session = Depends(get_db)):
  db_annotation = crud.get_annotation(db=db, annotation_id=annotation_id)
  if db_annotation is None:
    raise HTTPException(status_code=404, detail="Annotation not found")
  return db_annotation

@router.put("/{annotation_id}", response_model=schema.Annotation)
def update_annotation(annotation_id: int, annotation: schema.AnnotationUpdate, db: Session = Depends(get_db)):
  db_annotation = crud.update_annotation(db=db, annotation_id=annotation_id, label=annotation.label)
  if db_annotation is None:
    raise HTTPException(status_code=404, detail="Annotation not found")
  return db_annotation

@router.delete("/{annotation_id}", response_model=schema.Annotation)
def delete_annotation(annotation_id: int, db: Session = Depends(get_db)):
  db_annotation = crud.delete_annotation(db=db, annotation_id=annotation_id)
  if db_annotation is None:
    raise HTTPException(status_code=404, detail="Annotation not found")
  return db_annotation