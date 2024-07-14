from pydantic import BaseModel
from enum import Enum
from typing import Optional, List, Dict
import datetime

# Project configs
class ProjectConfigurationsBase(BaseModel):
  labels: str
  max_annotators_per_task: Optional[int] = 1
  completion_deadline: Optional[datetime.datetime] = None

class ProjectBase(BaseModel):
  project_title: str
  project_description: Optional[str] = ""

class ProjectCreate(ProjectBase, ProjectConfigurationsBase):
  pass

class ProjectUpdate(BaseModel):
  project_title: Optional[str]
  project_description: Optional[str]
  labels: Optional[str]
  max_annotators_per_task: Optional[int]
  completion_deadline: Optional[datetime.datetime]

class Project(ProjectBase):
  project_id: int
  created_at: datetime.datetime

  class Config:
    from_attributes = True

class ProjectConfigurations(ProjectConfigurationsBase):
  pass

# User Role models
class UserRole(str, Enum):
  admin = "admin"
  annotator = "annotator"
  reviewer = "reviewer"

class AssignmentType(str, Enum):
  annotation = "annotation"
  review = "review"

class RoleToAssignment(str, Enum):
  annotator = 'annotation'
  reviewer = 'review'

class RoleBase(BaseModel):
  role_name: str

class RoleCreate(RoleBase):
  pass

class RoleUpdate(RoleBase):
  pass

class Role(RoleBase):
  role_id: int

  class Config:
    from_attributes = True

# User models
class UserBase(BaseModel):
  username: str
  email: Optional[str] = None

class UserCreate(UserBase):
  pass

class UserCreateRoles(UserBase):
  roles: List[str]

class UserUpdate(UserBase):
  pass

class User(UserBase):
  user_id: int
  roles: List[str]

  class Config:
    from_attributes = True

# Task models
class TaskBase(BaseModel):
  task_id: str

class Task(TaskBase):
  project_id: int
  image: str
  additional_data: Optional[Dict] = None

  class Config:
    from_attributes = True

class TaskCreate(TaskBase):
  project_id: int
  image: str
  additional_data: Optional[Dict] = None

class TaskUpsert(TaskBase):
  project_id: int
  image: str
  additional_data: Optional[Dict] = None

class TaskUpdate(TaskBase):
  pass

# Annotation models
class AnnotationBase(BaseModel):
  label: str

class AnnotationCreate(AnnotationBase):
  task_id: str
  user_id: int

class AnnotationUpdate(AnnotationBase):
  pass

class Annotation(AnnotationBase):
  annotation_id: int
  task_id: str
  user_id: int

  class Config:
    from_attributes = True

class AnnotationRetrieve(BaseModel):
  label: Optional[str]

class AdminRetrieveAllAnnotations(BaseModel):
  task_id: str
  image: str
  annotations: str

# Review models
class ReviewBase(BaseModel):
  label: str

class ReviewCreate(ReviewBase):
  task_id: str
  user_id: int

class ReviewUpdate(ReviewBase):
  pass

class Review(ReviewBase):
  review_id: int
  task_id: str
  user_id: int

  class Config:
    from_attributes = True

# AssignedTask models
class AssignedTaskBase(BaseModel):
  task_type: str

class AssignedTaskCreate(AssignedTaskBase):
  task_id: str
  user_id: int

class AssignedTaskUpdate(AssignedTaskBase):
  pass

class AssignedTask(AssignedTaskBase):
  assignment_id: int
  task_id: str
  user_id: int

  class Config:
    from_attributes = True
