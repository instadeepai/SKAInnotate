from pydantic import BaseModel, EmailStr
from enum import Enum

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