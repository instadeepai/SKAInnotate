# app/crud.py
from typing import Any
from sqlalchemy.orm import Session
from app.models import ProjectDB, ProjectCreate

def create_project(db: Session, project: ProjectCreate):
    db_project = ProjectDB(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_projects(db: Session, skip: int = 0, limit: int = 10):
    return db.query(ProjectDB).offset(skip).limit(limit).all()
