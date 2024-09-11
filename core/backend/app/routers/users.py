from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.responses import JSONResponse
import app.crud as crud
import app.schema as schema
from app.database import get_db
from app.dependencies import get_current_role

router = APIRouter()

@router.get("/", response_model=List[schema.UserRetrieve])
async def read_users(skip: int = 0, limit: int = None, db: Session = Depends(get_db)):
  users = crud.get_users(db=db, skip=skip, limit=limit)
  return users

@router.get("/role/{role}", response_model=List[schema.UserRetrieve])
async def read_users(role: str, skip: int = 0, limit: int = None, db: Session = Depends(get_db)):
  users = crud.get_users_by_role(db=db, role=role)
  return users

@router.post("/", response_model=schema.User)
async def create_user(user_data: schema.UserCreate, db: Session = Depends(get_db)):
  user = crud.create_user(db=db, username=user_data.username, email=user_data.email)
  return user

@router.get("/role", response_model=schema.RoleBase)
async def get_current_role(role=Depends(get_current_role)):
  return JSONResponse(content={"role": role})

@router.get("/user-roles", response_model=List[str])
async def get_current_user_info(user_id, db = Depends(get_db)):
  user = crud.get_user(db, user_id=user_id)
  return [role.role_name for role in user.roles]

@router.post("/assign-role", response_model=schema.User)
def assign_role_to_user(role_assignment: schema.RoleAssignment, db: Session = Depends(get_db)):
  user = crud.assign_role(db, role=role_assignment.role, user_id=role_assignment.user_id)
  return user

@router.post("/unassign-role", response_model=schema.User)
def unassign_role_to_user(role_assignment: schema.RoleAssignment, db: Session = Depends(get_db)):
  user = crud.unassign_role(db, role=role_assignment.role, user_id=role_assignment.user_id)
  return user

@router.get("", response_model=List[schema.UserRetrieve])
async def get_users_by_role(role: str, db: Session = Depends(get_db)):
  users = crud.get_users_by_role(db, role)
  return users

@router.get("/{user_id}", response_model=schema.User)
async def read_user(user_id: int, db: Session = Depends(get_db)):
  db_user = crud.get_user(db=db, user_id=user_id)
  if db_user is None:
    raise HTTPException(status_code=404, detail="User not found")
  return db_user

@router.put("/{user_id}", response_model=schema.User)
async def update_user(user_id: int, user: schema.UserUpdate, db: Session = Depends(get_db)):
  db_user = crud.update_user(db=db, user_id=user_id, username=user.username, email=user.email)
  if db_user is None:
    raise HTTPException(status_code=404, detail="User not found")
  return db_user

@router.delete("/{user_id}", response_model=schema.User)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
  db_user = crud.delete_user(db=db, user_id=user_id)
  if db_user is None:
    raise HTTPException(status_code=404, detail="User not found")
  return db_user