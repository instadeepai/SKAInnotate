from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
import app.crud as crud
import app.schema as schema
from app.database import get_db
from app.dependencies import get_current_role

router = APIRouter()

@router.get("/", response_model=List[schema.User])
def read_users(request: Request, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
  users = crud.get_users(db=db, skip=skip, limit=limit)
  return users

@router.post("/", response_class=HTMLResponse)
async def create_user(request: Request, user_data: schema.UserCreateRoles, db: Session = Depends(get_db)):
  user = crud.create_user(db=db, username=user_data.username, email=user_data.email)
  return user

@router.get("/role")
def get_current_role(request: Request, role = Depends(get_current_role)):
  return role

@router.get("/reviewers/", response_model=List[schema.UserRetrieve])
def get_reviewers(db: Session = Depends(get_db)):
  reviewers = crud.get_reviewers(db)
  return reviewers

@router.get("/reviewers/{task_id}", response_model=List[schema.UserRetrieve])
def get_reviewers_by_task(task_id: str, db: Session = Depends(get_db)):
  reviewers = crud.get_reviewers_by_task(db, task_id=task_id)
  return reviewers

@router.get("/{user_id}", response_model=schema.User)
async def read_user(user_id: int, db: Session = Depends(get_db)):
  db_user = crud.get_user(db=db, user_id=user_id)
  if db_user is None:
    raise HTTPException(status_code=404, detail="User not found")
  return db_user

@router.put("/{user_id}", response_model=schema.User)
def update_user(user_id: int, user: schema.UserUpdate, db: Session = Depends(get_db)):
  db_user = crud.update_user(db=db, user_id=user_id, user_update=user)
  if db_user is None:
    raise HTTPException(status_code=404, detail="User not found")
  return db_user

@router.delete("/{user_id}", response_model=schema.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
  db_user = crud.delete_user(db=db, user_id=user_id)
  if db_user is None:
    raise HTTPException(status_code=404, detail="User not found")
  return db_user
