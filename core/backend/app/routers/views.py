import os
import logging
from typing import List
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse

from sqlalchemy.orm import Session
import app.crud as crud
import app.schema as schema
from app.dependencies import get_current_user, get_current_role
from app.database import get_db
# Configure logging
logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="/app/frontend/public")

@router.get("/role", response_class=HTMLResponse)
async def select_user_role(request: Request, user_info: dict = Depends(get_current_user)):
  """Render the page for selecting a user role."""
  logger.info("Rendering the role selection page.")
  return templates.TemplateResponse("roles.html", {"request": request, "user_info": user_info})

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
  """Render the login page."""
  logger.info("Rendering the login page.")
  return templates.TemplateResponse("login.html", {"request": request})

@router.get("/projects/{project_id}/annotations", response_model=List[schema.Annotation])
def render_annotations_page(request: Request, project_id: int, db: Session = Depends(get_db)):
  tasks_with_annotations = crud.get_tasks_with_annotations(db, project_id)
  reviewers = crud.get_reviewers(db)

  tasks = []
  for task in tasks_with_annotations:
    task_info = {
        "task_id": task["task_id"],
        "image": task["image"],
        "labels": task["labels"],
        "reviewers": reviewers
    }
    tasks.append(task_info)
  
  return templates.TemplateResponse("admin/annotations.html", {"request": request, "tasks": tasks})

@router.get("/projects-page", response_class=HTMLResponse)
async def render_projects_page(request: Request, db: Session = Depends(get_db)):
  role = request.cookies.get("current_role")
  if not role:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
  return templates.TemplateResponse("projects.html", {"request": request, "role": role})

@router.get("/create-project-form", response_model=None)
def render_create_project_form(request: Request):
  return templates.TemplateResponse("admin/create_project.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
def render_project_dashboard(request: Request, 
                            project_id: int, #db: Session = Depends(get_db), 
                            role = Depends(get_current_role)):
  return templates.TemplateResponse(f"{role}/dashboard.html", {
    "request": request,
    "project_id": project_id
    # "tasks": assigned_tasks
  })
#   role = get_current_role(request=request)
#   if role == schema.UserRole.admin:
#     return templates.TemplateResponse(f"{role}/dashboard.html", {"request": request, "project_id": project_id})
#   user_info = get_current_user(request)
#   if not user_info or "email" not in user_info:
#     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User info not found in session")

#   user = crud.get_user_by_email(db, user_info.get('email'))
#   if not user:
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

#   assignment_type = schema.AssignmentType.annotation if role == schema.UserRole.annotator else schema.AssignmentType.review
#   assigned_tasks = crud.get_assigned_tasks_by_type_and_project(db, user.user_id, assignment_type, project_id)

#   for task in assigned_tasks:
#     if role == schema.UserRole.annotator:
#       task.completion_status = any(annotation.user_id == user.user_id for annotation in task.annotations) if task.annotations else False
#     else:
#       task.completion_status = any(review.user_id == user.user_id for review in task.reviews) if task.reviews else False
#     task.image_url = task.image.replace("gs://", "https://storage.cloud.google.com/")

#   return templates.TemplateResponse(f"{role}/dashboard.html", {
#     "request": request,
#     "project_id": project_id,
#     "tasks": assigned_tasks
#   })

@router.get("/configurations", response_model=List[schema.ProjectConfigurations])
def read_project_configurations(request: Request, project_id: int, db: Session = Depends(get_db)):
  project = crud.get_project(db, project_id=project_id)
  project_configurations = crud.get_project_config_by_project(db=db, project_id=project_id)
  return templates.TemplateResponse("admin/project_configurations.html", {
    "request": request,
    "project": project,
    "project_configurations": project_configurations,
    "project_id": project_id
  })

@router.get("/edit-page", response_model=None)
def render_edit_project(request: Request, project_id: int, db: Session = Depends(get_db)):
  project_configurations = crud.get_project_config_by_project(db=db, project_id=project_id)
  project = crud.get_project(db, project_id=project_id)
  return templates.TemplateResponse("admin/project_configurations_edit.html", {
    "request": request,
    "project": project,
    "project_configurations": project_configurations
  })

# Read Tasks Endpoint
@router.get("/projects/{project_id}/tasks", response_class=HTMLResponse)
def render_read_tasks(request: Request, project_id: int, db: Session = Depends(get_db)):
  tasks = crud.get_tasks_in_project(db=db, project_id=project_id)
  return templates.TemplateResponse("admin/task_panel.html", 
                                    {"request": request, "tasks": tasks, "project_id": project_id})

@router.get("/tasks-page", response_class=HTMLResponse)
async def render_task_page(request: Request,
                          #  project_id: int,
                          #  task_id: str,
                           role: str = Depends(get_current_role)):
    return templates.TemplateResponse(f"{role}/task_single.html", {
        "request": request,
        # "task_id": task_id,
        # "project_id": project_id,
    })

#  Add Task Form Endpoint
@router.get("/projects/{project_id}/tasks/add_task", response_class=HTMLResponse)
async def render_add_task_form(request: Request):
  return templates.TemplateResponse("admin/add_task.html", {"request": request})

@router.get("/users-page", response_model=List[schema.User])
def render_users_page(request: Request, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
  users = crud.get_users(db=db, skip=skip, limit=limit)
  return templates.TemplateResponse("admin/users.html", {"request": request, "users": users})

@router.post("/add", response_class=HTMLResponse)
async def render_create_user_page(request: Request, user_data: schema.UserCreateRoles, db: Session = Depends(get_db)):
  user = crud.create_user(db=db, username=user_data.username, email=user_data.email)
  for role in user_data.roles:
    crud.assign_role_to_user(db, user_name=user_data.username, user_email=user_data.email, role_name=role)
  return templates.TemplateResponse("admin/user_management.html", {"request": request, "user": user})

@router.get("/modify-users", response_model=None)
async def render_add_remove_user_page(request: Request, db: Session = Depends(get_db)):
  roles = crud.get_roles(db)
  return templates.TemplateResponse("admin/user_management.html", {"request": request, "roles": roles})

@router.post("/remove", response_class=HTMLResponse)
async def render_remove_user_page(request: Request, user_data: schema.UserCreateRoles, db: Session = Depends(get_db)):
  user = crud.create_user(db=db, username=user_data.username, email=user_data.email)
  for role in user_data.roles:
    crud.unassign_role_from_user(db, user_name=user_data.username, user_email=user_data.email, role_name=role)
  return templates.TemplateResponse("admin/user_management.html", {"request": request, "user": user})
