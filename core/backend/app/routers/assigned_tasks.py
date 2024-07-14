# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from typing import List

# import app.crud as crud
# import app.schema as schemas
# from app.database import get_db

# router = APIRouter()

# @router.post("/", response_model=schemas.AssignedTask)
# def create_assigned_task(assigned_task: schemas.AssignedTaskCreate, db: Session = Depends(get_db)):
#   return crud.create_assigned_task(db=db, assigned_task=assigned_task)

# @router.get("/{assigned_task_id}", response_model=schemas.AssignedTask)
# def read_assigned_task(assigned_task_id: int, db: Session = Depends(get_db)):
#   db_assigned_task = crud.get_assigned_task(db=db, assigned_task_id=assigned_task_id)
#   if db_assigned_task is None:
#     raise HTTPException(status_code=404, detail="Assigned Task not found")
#   return db_assigned_task

# @router.get("/", response_model=List[schemas.AssignedTask])
# def read_assigned_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#   assigned_tasks = crud.get_assigned_tasks(db=db, skip=skip, limit=limit)
#   return assigned_tasks

# @router.put("/{assigned_task_id}", response_model=schemas.AssignedTask)
# def update_assigned_task(assigned_task_id: int, assigned_task: schemas.AssignedTaskUpdate, db: Session = Depends(get_db)):
#   db_assigned_task = crud.update_assigned_task(db=db, assigned_task_id=assigned_task_id, assigned_task_update=assigned_task)
#   if db_assigned_task is None:
#     raise HTTPException(status_code=404, detail="Assigned Task not found")
#   return db_assigned_task

# @router.delete("/{assigned_task_id}", response_model=schemas.AssignedTask)
# def delete_assigned_task(assigned_task_id: int, db: Session = Depends(get_db)):
#   db_assigned_task = crud.delete_assigned_task(db=db, assigned_task_id=assigned_task_id)
#   if db_assigned_task is None:
#     raise HTTPException(status_code=404, detail="Assigned Task not found")
#   return db_assigned_task
