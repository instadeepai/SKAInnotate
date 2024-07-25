from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import app.crud as crud
import app.schema as schema
from app.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schema.Project])
async def get_projects_data(db: Session = Depends(get_db)):
  projects = crud.get_projects(db)
  return projects

@router.post("/", response_model=schema.Project)
def create_project(project: schema.ProjectCreate, db: Session = Depends(get_db)):
  project = crud.create_project(db=db, project=project)
  return project

@router.put("/{project_id}/configurations/edit", response_model=schema.Project)
def update_project(project_id: int, project: schema.ProjectUpdate, db: Session = Depends(get_db)):
  existing_project = crud.get_project(db, project_id)
  if existing_project is None:
    raise HTTPException(status_code=404, detail="Project not found")
  updated_project = crud.update_project(db, project_id, project)
  return updated_project

@router.put("/{project_id}/edit", response_model=None)
def update_project(request: Request, project_id: int, db: Session = Depends(get_db)):
  project_configurations = crud.get_project_config_by_project(db=db, project_id=project_id)
  project = crud.get_project(db, project_id=project_id)
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