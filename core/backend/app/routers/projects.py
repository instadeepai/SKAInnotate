from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
import app.crud as crud
import app.schema as schemas
from app.database import get_db
from app.dependencies import get_current_role, get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="/app/frontend/public")

@router.get("/", response_model=List[schemas.Project])
async def get_projects_data(db: Session = Depends(get_db)):
  projects = crud.get_projects(db)
  return projects

@router.post("/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
  project = crud.create_project(db=db, project=project)
  return project

@router.get("/projects-page", response_class=HTMLResponse)
async def render_projects_page(request: Request, db: Session = Depends(get_db)):
  role = request.cookies.get("current_role")
  if not role:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
  projects = crud.get_projects(db)
  return templates.TemplateResponse("/projects.html", {"request": request, "role": role, "projects": projects})

@router.get("/create-project-form", response_model=None)
def render_create_project_form(request: Request):
  return templates.TemplateResponse("admin/create_project.html", {"request": request})

@router.get("/{project_id}/dashboard", response_class=HTMLResponse)
def render_project_dashboard(request: Request, project_id: int, db: Session = Depends(get_db)):
  role = get_current_role(request=request)
  if role == schemas.UserRole.admin:
    return templates.TemplateResponse(f"{role}/dashboard.html", {"request": request, "project_id": project_id})

  user_info = get_current_user(request)
  if not user_info or "email" not in user_info:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User info not found in session")

  user = crud.get_user_by_email(db, user_info.get('email'))
  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

  assignment_type = schemas.AssignmentType.annotation if role == schemas.UserRole.annotator else schemas.AssignmentType.review
  assigned_tasks = crud.get_assigned_tasks_by_type_and_project(db, user.user_id, assignment_type, project_id)

  for task in assigned_tasks:
    if role == schemas.UserRole.annotator:
      task.completion_status = any(annotation.user_id == user.user_id for annotation in task.annotations) if task.annotations else False
    else:
      task.completion_status = any(review.user_id == user.user_id for review in task.reviews) if task.reviews else False
    task.image_url = task.image.replace("gs://", "https://storage.cloud.google.com/")

  return templates.TemplateResponse(f"{role}/dashboard.html", {
    "request": request,
    "project_id": project_id,
    "tasks": assigned_tasks
  })

@router.put("/{project_id}/configurations/edit", response_model=schemas.Project)
def update_project(project_id: int, project: schemas.ProjectUpdate, db: Session = Depends(get_db)):
  existing_project = crud.get_project(db, project_id)
  if existing_project is None:
    raise HTTPException(status_code=404, detail="Project not found")
  updated_project = crud.update_project(db, project_id, project)
  return updated_project

@router.get("/{project_id}/configurations/", response_model=List[schemas.ProjectConfigurations])
def read_project_configurations(request: Request, project_id: int, db: Session = Depends(get_db)):
  project = crud.get_project(db, project_id=project_id)
  project_configurations = crud.get_project_config_by_project(db=db, project_id=project_id)
  return templates.TemplateResponse("admin/project_configurations.html", {
    "request": request,
    "project": project,
    "project_configurations": project_configurations,
    "project_id": project_id
  })

@router.put("/{project_id}/edit", response_model=None)
def update_project(request: Request, project_id: int, db: Session = Depends(get_db)):
  project_configurations = crud.get_project_config_by_project(db=db, project_id=project_id)
  project = crud.get_project(db, project_id=project_id)
  return project

@router.get("/{project_id}/edit-page", response_model=None)
def render_edit_project(request: Request, project_id: int, db: Session = Depends(get_db)):
  project_configurations = crud.get_project_config_by_project(db=db, project_id=project_id)
  project = crud.get_project(db, project_id=project_id)
  return templates.TemplateResponse("admin/project_configurations_edit.html", {
    "request": request,
    "project": project,
    "project_configurations": project_configurations
  })

@router.get("/{project_id}", response_model=schemas.Project)
def read_project(request: Request, project_id: int, db: Session = Depends(get_db)):
  project = crud.get_project(db, project_id=project_id)
  return project

@router.delete("/{project_id}", response_model=schemas.Project)
def delete_project(project_id: int, db: Session = Depends(get_db)):
  project = crud.delete_project(db, project_id)
  if project is None:
    raise HTTPException(status_code=404, detail="Project not found")
  return project