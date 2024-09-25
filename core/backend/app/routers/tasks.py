from typing import List, Dict, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Form

from fastapi.requests import Request
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

import core.backend.app.crud as crud
import core.backend.app.schema as schema
import core.backend.app.model as model
from core.backend.app.database import get_db
from core.backend.app.dependencies import get_current_role, get_current_user

router = APIRouter()

@router.get("/")
async def get_tasks_by_label_status(request: Request,
                                    project_id: int,
                                    labeled: Optional[bool] = None,
                                    db: Session = Depends(get_db),
                                    role: str = Depends(get_current_role)):
    user_info = get_current_user(request)
    user_id = user_info["user_id"]
    user = crud.get_user(db, user_id)
    
    assigned_tasks = crud.get_assigned_tasks_by_type_and_project(db, 
                                user_id=user_id, assignment_type=schema.RoleToAssignment[role].value, project_id=project_id)
    
    if labeled is not None:
      if role == schema.UserRole.annotator:
        assigned_tasks = [task for task in assigned_tasks if any(annotation.user_id == user.user_id for annotation in task.annotations) == labeled]
      else:
        assigned_tasks = [task for task in assigned_tasks if any(review.user_id == user.user_id for review in task.reviews) == labeled]
    return assigned_tasks

@router.get("/{task_id}", response_class=JSONResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
  task = crud.get_task(db, task_id)
  image_url = task.image.replace("gs://", "https://storage.cloud.google.com/")
  response_data = {
      "task_id": task.task_id,
      "image": image_url,
  }
  return response_data

# Update Task Endpoint
@router.put("/{task_id}", response_model=schema.Task)
def update_task(task_id: str, task: schema.TaskUpdate, db: Session = Depends(get_db)):
  db_task = crud.update_task(db=db, task_id=task_id, task_update=task)
  if db_task is None:
    raise HTTPException(status_code=404, detail="Task not found")
  return db_task

# Delete Task Endpoint
@router.delete("/{task_id}", response_model=schema.Task)
def delete_task(task_id: str, db: Session = Depends(get_db)):
  db_task = crud.delete_task(db=db, task_id=task_id)
  if db_task is None:
    raise HTTPException(status_code=404, detail="Task not found")
  return db_task

@router.get("/task-details")
async def get_task_details(request: Request,
                          project_id: int,
                          task_id: str,
                          role: str,
                          db: Session = Depends(get_db)
                          ):
  task = crud.get_task(db, task_id=task_id)
  if not task:
    raise HTTPException(status_code=404, detail="Task not found")

  image_url = task.image.replace("gs://", "https://storage.cloud.google.com/")
  response_data = {
      "task_id": task.task_id,
      "image": image_url,
  }

  if role == schema.UserRole.admin:
    users_assigned_to_task = crud.get_users_assigned_to_task(db, task_id=task_id, project_id=project_id)
    response_data["assigned_users"] = [crud.get_user(db, user.user_id) for user in users_assigned_to_task]
    return JSONResponse(content=response_data)
  else:
    user_info = get_current_user(request)
    user_id = user_info["user_id"]
    user = crud.get_user(db, user_id)

    all_assigned_tasks = crud.get_assigned_tasks_by_type_and_project(db,
                              user_id=user_id, assignment_type=schema.RoleToAssignment[role].value, project_id=project_id)
    current_task_index = next((i for i, t in enumerate(all_assigned_tasks) if t.task_id == task_id), -1)
    all_tasks_dict = [
        {"task_id": t.task_id, "image": t.image.replace("gs://", "https://storage.cloud.google.com/")} for t in all_assigned_tasks
    ]
    response_data.update({
        "tasks_json": all_tasks_dict,
        "current_task_index": current_task_index,
        "user_id": user.user_id,
    })
    return JSONResponse(content=response_data)

@router.get("/{task_id}/is_labeled")
async def is_task_labeled(task_id: str, user_id: int, task_type: str, db: Session = Depends(get_db)):
  if task_type == schema.AssignmentType.annotation:
    query_response = db.query(model.Annotation).filter(
        model.Annotation.task_id == task_id,
        model.Annotation.user_id == user_id
    ).first()
  elif task_type == schema.AssignmentType.review:
    query_response = db.query(model.Review).filter(
        model.Review.task_id == task_id,
        model.Review.user_id == user_id
    ).first()
  else:
    raise HTTPException(status_code=404, detail="Task not found")

  is_labeled = query_response is not None
  return {"is_labeled": is_labeled}

@router.post("/labels/is_labeled")
async def are_tasks_labeled(label_check: schema.LabelCheck, db: Session = Depends(get_db)) -> Dict[str, bool]:
  if label_check.task_type not in [schema.AssignmentType.annotation, schema.AssignmentType.review]:
    raise HTTPException(status_code=400, detail="Invalid task type")
  
  if label_check.task_type == schema.AssignmentType.annotation:
    query_response = db.query(model.Annotation.task_id).filter(
        model.Annotation.task_id.in_(label_check.task_ids),
        model.Annotation.user_id == label_check.user_id
    ).all()
  elif label_check.task_type == schema.AssignmentType.review:
    query_response = db.query(model.Review.task_id).filter(
        model.Review.task_id.in_(label_check.task_ids),
        model.Review.user_id == label_check.user_id
    ).all()

  labeled_task_ids = {result[0] for result in query_response}
  return {task_id: task_id in labeled_task_ids for task_id in label_check.task_ids}

@router.get("/fetchall/imgUrl-and-labelStatus", response_model=List[schema.TaskResponse])
async def get_tasks_url_label_status(project_id: int,
                                  user_id: int,
                                  role: str,
                                  db: Session = Depends(get_db)
                                  ):
  
  user = crud.get_user(db, user_id)

  if role == schema.UserRole.admin:
    tasks = crud.get_tasks_in_project(db, project_id=project_id)
  
  elif role == schema.UserRole.annotator:
    tasks = crud.get_assigned_tasks_by_type_and_project(db, 
                      user_id=user_id, assignment_type=schema.RoleToAssignment[role].value, project_id=project_id)
  
  elif role == schema.UserRole.reviewer:
    tasks = crud.get_assigned_tasks_by_type_and_project(db, 
                      user_id=user_id, assignment_type=schema.RoleToAssignment[role].value, project_id=project_id)
  else:
    return []

  tasks_response = []
  for task in tasks:
    if role == schema.UserRole.annotator:
      completion_status = any(annotation.user_id == user.user_id for annotation in task.annotations)
    else:
      completion_status = any(review.user_id == user.user_id for review in task.reviews)
    image_url =  task.image.replace("gs://", "https://storage.cloud.google.com/")

    tasks_response.append({
        "task_id": task.task_id,
        "image_url": image_url,
        "completion_status": completion_status,
        "annotations": [annotation.label for annotation in task.annotations],
        "reviews": [review.label for review in task.reviews]
    })
  return tasks_response

@router.get("/fetch/imgUrl-and-labelStatus", response_model=schema.TaskResponse)
async def get_tasks_url_label_status(project_id: int,
                                  user_id: int,
                                  role: str,
                                  task_id: str,
                                  db: Session = Depends(get_db)
                                  ):
  
  user = crud.get_user(db, user_id)

  if role == schema.UserRole.admin:
    tasks = crud.get_tasks_in_project(db, project_id=project_id)
  
  elif role == schema.UserRole.annotator:
    tasks = crud.get_assigned_tasks_by_type_and_project(db, 
                      user_id=user_id, assignment_type=schema.RoleToAssignment[role].value, project_id=project_id)
  
  else:
    tasks = crud.get_assigned_tasks_by_type_and_project(db, 
                      user_id=user_id, assignment_type=schema.RoleToAssignment[role].value, project_id=project_id)
  
  task = crud.get_task(db=db, task_id=task_id)
  # Transform tasks to match the expected response structure
  task_response = []
  # for task in tasks:
  if role == schema.UserRole.admin:
    completion_status = False
  elif role == schema.UserRole.annotator:
    completion_status = any(annotation.user_id == user.user_id for annotation in task.annotations)
  else:
    completion_status = any(review.user_id == user.user_id for review in task.reviews)
  
  image_url =  task.image.replace("gs://", "https://storage.cloud.google.com/")

  task_response = {
      "task_id": task.task_id,
      "image_url": image_url,
      "completion_status": completion_status,
      "annotations": [annotation.label for annotation in task.annotations],
      "reviews": [review.label for review in task.reviews]
  }
  return task_response

@router.get("/{task_id}/user/{user_id}/annotations", response_model=Optional[schema.Annotation])
def read_annotation_by_task_and_user(task_id: str, user_id: int, db: Session = Depends(get_db)):
  annotation = crud.get_annotation_by_task_annotator(db=db, annotator_id=user_id, task_id=task_id)
  return annotation

@router.get("/{task_id}/user/{user_id}/reviews", response_model=Optional[schema.Review])
def read_review_by_task_and_user(task_id: str, user_id: int, db: Session = Depends(get_db)):
  review = crud.get_review_by_task_reviewer(db=db, reviewer_id=user_id, task_id=task_id)
  return review

# Auto Assign Tasks Endpoint
@router.get("/assign-tasks/auto", response_model=List[schema.TaskRetrieve])
async def auto_assign_task(project_id: int, db: Session = Depends(get_db)):
  tasks = crud.auto_assign_tasks_to_users(db, project_id=project_id)
  return tasks

@router.post("/{task_id}/assign", response_class=JSONResponse)
async def assign_review_task(task_id: str, assignData: schema.TaskAssign , db: Session = Depends(get_db)):
  try:
    tasks = crud.assign_task(db, task_id, assignData.user_id, assignData.assignment_type)
    return tasks
  except Exception as e:
    return JSONResponse(status_code=400, content={"message": str(e)})

# Unassign Task Endpoint
@router.post("/{task_id}/unassign", response_class=JSONResponse)
async def unassign_task(task_id: str, taskUnAssign: schema.TaskUnAssign, db: Session = Depends(get_db)):
  try:
    crud.unassign_task(db, task_id=task_id, assignment_type=taskUnAssign.assignment_type)
    return {"message": "Task unassigned successfully"}
  except Exception as e:
    return JSONResponse(status_code=400, content={"message": str(e)})

@router.get("/{task_id}/default_label", response_model=schema.AnnotationRetrieve)
def get_default_label(task_id: str, user_id: int, task_type: str, db: Session = Depends(get_db)):
  if task_type==schema.AssignmentType.review:
    query_response = crud.get_default_review(db, task_id=task_id, user_id=user_id)
  else:
    query_response = crud.get_default_label(db, task_id=task_id, user_id=user_id)
  return {"label": query_response.label if query_response else None}

def preprocess_labels(labels_str):
  return [label.strip(' "') for label in labels_str.split(",")]

@router.get("/{task_id}/labels", response_model=List[str])
async def get_task_labels(task_id: str, db: Session = Depends(get_db)):
  string_labels = crud.get_task(db, task_id).project.configurations.labels
  labels = preprocess_labels(string_labels)
  return labels

@router.get("/{task_id}/reviewers", response_model=List[schema.UserRetrieve])
async def get_reviewers_by_task(task_id: str, db: Session = Depends(get_db)):
  reviewers = crud.get_reviewers_by_task(db, task_id=task_id)
  return reviewers

@router.get("/{task_id}/assigned_users", response_model=schema.AssignedUsersRetrieve)
async def get_annotators_and_reviewers_assigned_to_task(task_id: str, db: Session = Depends(get_db)):
  users = crud.get_assigned_users_for_task(db, task_id=task_id)
  assigned_annotators, assigned_reviewers = users
  assigned_users = {
    'assigned_annotators': assigned_annotators,
    'assigned_reviewers': assigned_reviewers}
  return assigned_users

