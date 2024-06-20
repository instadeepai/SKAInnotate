# app/models.py
from typing import Any
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from app.database import Base

class ProjectBase(BaseModel):
  name: str
  description: str

class ProjectCreate(ProjectBase):
  pass

class Project(ProjectBase):
  id: int

  class Config:
    orm_mode = True

# Define SQLAlchemy models
class ProjectDB(Base):
  __tablename__ = "projects"

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, index=True)
  description = Column(String)