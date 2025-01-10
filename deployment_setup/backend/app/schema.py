from pydantic import BaseModel, EmailStr
from enum import Enum
from datetime import datetime

# SQL instance
class SQLInstance(BaseModel):
  project_id: str
  service_account_file: str
  instance_name: str
  region: str
  database_name: str
  db_user: str
  db_pass: str

class setProject(BaseModel):
  project_id: str
  service_account_file: str

class DeployAppData(BaseModel):
  project_id: str
  instance_name: str
  region: str
  db_name: str
  db_user: str
  db_pass: str
  service_name: str
  clientId: str
  superuser_email: EmailStr
  superuser_username: str

class DeploymentCreate(BaseModel):
  project_id: str
  instance_name: str
  deployment_status: str
  service_name: str = None
  service_url: str = None

class DeploymentResponse(BaseModel):
  id: int
  project_id: str
  instance_name: str
  deployment_status: str
  service_name: str = None
  service_url: str = None
  deployed_at: datetime
  # active: bool