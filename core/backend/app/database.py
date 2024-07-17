from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import app.crud as crud
from app.model import Role, User, Base
import os
import json
from google.cloud.sql.connector import Connector
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")
INSTANCE_NAME = os.getenv("INSTANCE_NAME")

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

def get_connection() -> str:
  conn = connector.connect(
        f"{PROJECT_ID}:{REGION}:{INSTANCE_NAME}",
        "pg8000",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME
  )

  return conn

engine = create_engine(
      "postgresql+pg8000://",
      creator=get_connection,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

if not all([DB_USER, DB_PASS, DB_NAME]):
  raise ValueError("Missing required environment variables for database configuration.")

connector = Connector()

def db_configs(username: str, database: str):
  return {
      'username': username,
      'database': database
  }

def add_initial_roles(db: Session):
  roles = ["admin", "annotator", "reviewer"]
  for role_name in roles:
    existing_role = db.query(Role).filter_by(role_name=role_name).first()
    if not existing_role:
      role = Role(role_name=role_name)
      db.add(role)
  db.commit()

def init_admin(db: Session):
  super_user_username = os.getenv("SUPERUSER_USERNAME")
  super_user_email = os.getenv("SUPERUSER_EMAIL")

  if super_user_username and super_user_email:
    user = crud.create_user(db, super_user_username, super_user_email)
    crud.assign_role_to_user(db, user_name=super_user_username, user_email=super_user_email, role_name='admin')
  else:
    print("Error: SUPER_USER does not contain 'username' or 'email'")

def init_db():
  Base.metadata.create_all(bind=engine)
  with SessionLocal() as db:
    add_initial_roles(db)
    init_admin(db)

def get_db() -> Generator:
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
