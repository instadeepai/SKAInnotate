# app/schemas.py
from typing import Any
from pydantic import BaseModel

class ProjectBase(BaseModel):
  name: str
  description: str

class ProjectCreate(ProjectBase):
  pass

class Project(ProjectBase):
  id: int

  class Config:
    orm_mode = True
