from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
import app.crud as crud
import app.schema as schemas
from app.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="/app/frontend/public")

@router.get("/add-remove-user", response_model=None)
def add_remove_user(request: Request, db: Session = Depends(get_db)):
  roles = crud.get_roles(db)
  return templates.TemplateResponse("admin/user_management.html", {"request": request, "roles": roles})

@router.post("/add", response_class=HTMLResponse)
async def create_user(request: Request, user_data: schemas.UserCreateRoles, db: Session = Depends(get_db)):
  user = crud.create_user(db=db, username=user_data.username, email=user_data.email)
  for role in user_data.roles:
    crud.assign_role_to_user(db, user_name=user_data.username, user_email=user_data.email, role_name=role)
  return templates.TemplateResponse("admin/user_management.html", {"request": request, "user": user})

@router.post("/remove", response_class=HTMLResponse)
async def create_user(request: Request, user_data: schemas.UserCreateRoles, db: Session = Depends(get_db)):
  user = crud.create_user(db=db, username=user_data.username, email=user_data.email)
  for role in user_data.roles:
    crud.assign_role_to_user(db, user_name=user_data.username, user_email=user_data.email, role_name=role)
  return templates.TemplateResponse("admin/user_management.html", {"request": request, "user": user})

@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
  db_user = crud.get_user(db=db, user_id=user_id)
  if db_user is None:
    raise HTTPException(status_code=404, detail="User not found")
  return db_user

@router.get("/", response_model=List[schemas.User])
def read_users(request: Request, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
  users = crud.get_users(db=db, skip=skip, limit=limit)
  return templates.TemplateResponse("admin/users.html", {"request": request, "users": users})

@router.put("/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
  db_user = crud.update_user(db=db, user_id=user_id, user_update=user)
  if db_user is None:
    raise HTTPException(status_code=404, detail="User not found")
  return db_user

@router.delete("/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
  db_user = crud.delete_user(db=db, user_id=user_id)
  if db_user is None:
    raise HTTPException(status_code=404, detail="User not found")
  return db_user
