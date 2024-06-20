# app/routes/projects.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(SessionLocal)):
  return crud.create_project(db=db, project=project)

@router.get("/", response_model=list[schemas.Project])
def read_projects(skip: int = 0, limit: int = 10, db: Session = Depends(SessionLocal)):
  projects = crud.get_projects(db=db, skip=skip, limit=limit)
  return projects