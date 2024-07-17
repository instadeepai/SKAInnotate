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

@router.post("/create", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
  return crud.create_project(db=db, project=project)

@router.get("/create", response_model=None)
def create_project(request: Request):
  return templates.TemplateResponse(f"/admin/create_project.html", {"request": request})

@router.get("/", response_class=HTMLResponse)
async def read_projects(request: Request, db: Session = Depends(get_db)):
  projects = crud.get_projects(db)
  role = request.cookies.get("current_role")
  if not role:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
  return templates.TemplateResponse("/projects.html", {"request": request, "projects": projects, "role": role})

@router.get("/{project_id}", response_model=schemas.Project)
def read_project(request: Request, project_id: int, db: Session = Depends(get_db)):
  return RedirectResponse(url=f"/projects/{project_id}/dashboard")

@router.get("/{project_id}/dashboard", response_class=HTMLResponse)
def redirect_to_dashboard(request: Request, project_id: int, db: Session = Depends(get_db)):
  role = get_current_role(request=request)
  if role == schemas.UserRole.admin:
    return templates.TemplateResponse(f"{role}/dashboard.html", {"request": request, "project_id": project_id})

  user_info = get_current_user(request)
  if not user_info or "email" not in user_info:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User info not found in session")

  user_email = user_info["email"]
  user = crud.get_user_by_email_and_role(db, user_email, role)
  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

  assignment_type = schemas.AssignmentType.annotation if role == schemas.UserRole.annotator else schemas.AssignmentType.review
  assigned_tasks = crud.get_assigned_tasks_by_type_and_project(db, user.user_id, assignment_type, project_id)

  for task in assigned_tasks:
    task.labeling_status = any(annotation.user_id == user.user_id for annotation in task.annotations) if task.annotations else False

  labeling_status = [any(annotation.user_id == user.user_id for annotation in task.annotations) if task.annotations else False for task in assigned_tasks]

  return templates.TemplateResponse(f"{role}/dashboard.html", {
    "request": request,
    "project_id": project_id,
    "tasks": assigned_tasks,
    "labeling_status": labeling_status
  })

@router.put("/{project_id}/configurations/edit/", response_model=schemas.Project)
def update_project(project_id: int, project: schemas.ProjectUpdate, db: Session = Depends(get_db)):
  existing_project = crud.get_project(db, project_id)
  if existing_project is None:
    raise HTTPException(status_code=404, detail="Project not found")
  updated_project = crud.update_project(db, project_id, project)
  return updated_project

@router.delete("/{project_id}", response_model=schemas.Project)
def delete_project(project_id: int, db: Session = Depends(get_db)):
  project = crud.delete_project(db, project_id)
  if project is None:
    raise HTTPException(status_code=404, detail="Project not found")
  return project

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

@router.get("/{project_id}/configurations/edit/", response_model=None)
def edit_project_configurations(request: Request, project_id: int, db: Session = Depends(get_db)):
  project_configurations = crud.get_project_config_by_project(db=db, project_id=project_id)
  project = crud.get_project(db, project_id=project_id)
  return templates.TemplateResponse("admin/project_configurations_edit.html", {
    "request": request,
    "project": project,
    "project_configurations": project_configurations
  })
