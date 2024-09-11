from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import datetime
import json

import app.schema as schema
from app.model import (User, 
                      Role,
                      Task,
                      Annotation,
                      Review,
                      AssignedTask,
                      Project,
                      user_tasks,
                      user_roles)
from app.assignment import round_robin_algorithm

# Project CRUD operations
def get_project(db: Session, project_id: int):
  return db.query(Project).filter(Project.project_id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 10):
  return db.query(Project).group_by(Project.project_id).offset(skip).limit(limit).all()

def create_project(db: Session, project: schema.ProjectCreate):
  db_project = Project(
    project_title=project.project_title, 
    project_description=project.project_description,
    labels=project.labels,
    max_annotators_per_task=project.max_annotators_per_task,
    completion_deadline=project.completion_deadline,
    created_at=datetime.datetime.utcnow()
  )
  db.add(db_project)
  db.commit()
  db.refresh(db_project)
  return db_project

def delete_project(db: Session, project_id: int):
  project = db.query(Project).filter(Project.project_id == project_id).first()
  if project is None:
    return None
  db.delete(project)
  db.commit()
  return project

def update_project(db: Session, project_id: int, project_update: schema.ProjectUpdate):
  db_project = db.query(Project).filter(Project.project_id == project_id).first()
  if db_project:
    if project_update.project_title is not None:
      db_project.project_title = project_update.project_title
    if project_update.project_description is not None:
      db_project.project_description = project_update.project_description
    if project_update.labels is not None:
      db_project.labels = project_update.labels
    if project_update.max_annotators_per_task is not None:
      db_project.max_annotators_per_task = project_update.max_annotators_per_task
    if project_update.completion_deadline is not None:
      db_project.completion_deadline = project_update.completion_deadline
    db.commit()
    db.refresh(db_project)
  return db_project

# User CRUD operations
def create_user(db: Session, username: str, email: Optional[str] = None) -> User:
  user = db.query(User).filter(User.username == username, User.email == email).first()
  if not user:
    user = User(username=username, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
  return user

def get_user(db: Session, user_id: int) -> Optional[User]:
  return db.query(User).filter(User.user_id == user_id).first()

def get_user_role_by_email(db: Session, user_email: str):
  return db.query(User, Role).join(user_roles).join(Role).filter(User.email == user_email).all()

def get_user_by_email(db: Session, user_email: str):
  return db.query(User).join(User.roles).filter(
    User.email == user_email
  ).one_or_none()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
  return db.query(User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, username: Optional[str] = None, email: Optional[str] = None) -> Optional[User]:
  user = get_user(db, user_id)
  if user is None:
    return None
  if username:
    user.username = username
  if email:
    user.email = email
  db.commit()
  db.refresh(user)
  return user

def delete_user(db: Session, user_id: int) -> Optional[User]:
  user = get_user(db, user_id)
  if user is None:
      return None
  db.delete(user)
  db.commit()
  return user

def assign_role_to_user(db: Session, role_name: str, user_name: Optional[str] = None, user_email: Optional[str] = None):
  user = db.query(User).filter(User.email == user_email, User.username == user_name).first()
  role = db.query(Role).filter(Role.role_name == role_name).first()

  if user is None:
    raise ValueError(f"User with email {user_email} and username {user_name} not found")

  if role is None:
    raise ValueError(f"Role {role_name} not found")

  if role not in user.roles:
    user.roles.append(role)
    db.commit()

def unassign_role_from_user(db: Session, role_name: str, user_name: Optional[str] = None, user_email: Optional[str] = None):
  user = db.query(User).filter(User.email == user_email, User.username == user_name).first()
  role = db.query(Role).filter(Role.role_name == role_name).first()

  if user is None:
    raise ValueError(f"User with email {user_email} and username {user_name} not found")

  if role is None:
    raise ValueError(f"Role {role_name} not found")

  if role in user.roles:
    user.roles.remove(role)
    db.commit()
  if not user.roles:
    db.delete(user)
    db.commit()

def assign_roles_to_user(db: Session, role_names: List[str], user: User):
  if user:
    for role_name in role_names:
      role = db.query(Role).filter(Role.role_name == role_name).first()
      if role and role not in user.roles:
        user.roles.append(role)
    db.commit()

def assign_role(db: Session, role: str, user_id: int):
  user = get_user(db, user_id=user_id)
  role = db.query(Role).filter(Role.role_name == role).first()
  if not user:
    raise ValueError("User not found")
  if not role:
    raise ValueError("Role not found")
  if role not in user.roles:
    user.roles.append(role)
    db.commit()
    db.refresh(user)
  return user

def unassign_role(db: Session, role: str, user_id: int):
  user = get_user(db, user_id=user_id)
  role = db.query(Role).filter(Role.role_name == role).first()
  if not user:
    raise ValueError("User not found")
  if not role:
    raise ValueError("Role not found")
  if role in user.roles:
    user.roles.remove(role)
    db.commit()
  return user

def get_users_by_role(db: Session, role: str):
  return db.query(User).join(User.roles).filter(Role.role_name == role).all()

def get_reviewers_by_task(db: Session, task_id: str):
  return (
    db.query(User)
    .join(user_tasks, User.user_id == user_tasks.c.user_id)
    .join(user_roles, User.user_id == user_roles.c.user_id)
    .join(Role, user_roles.c.role_id == Role.role_id)
    .filter(user_tasks.c.task_id == task_id)
    .filter(Role.role_name == 'reviewer')
    .distinct()
    .all()
  )

# Role CRUD operations
def create_role(db: Session, role_name: str) -> Role:
  role = Role(role_name=role_name)
  db.add(role)
  db.commit()
  db.refresh(role)
  return role

def get_role(db: Session, role_id: int) -> Optional[Role]:
  return db.query(Role).filter(Role.role_id == role_id).first()

def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
  return db.query(Role).offset(skip).limit(limit).all()

def update_role(db: Session, role_id: int, role_name: str) -> Optional[Role]:
  role = get_role(db, role_id)
  if role is None:
    return None
  role.role_name = role_name
  db.commit()
  db.refresh(role)
  return role

def delete_role(db: Session, role_id: int) -> Optional[Role]:
  role = get_role(db, role_id)
  if role is None:
    return None
  db.delete(role)
  db.commit()
  return role

# Task CRUD operations
def create_task(db: Session, task: schema.TaskCreate) -> Task:
  new_task = Task(
      task_id=task.task_id,
      project_id=task.project_id,
      image=task.image,
      additional_data=json.dumps(task.additional_data)
  )
  try:
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
  except IntegrityError:
    db.rollback()
  return new_task

def upsert_task(db: Session, project_id: int, task: schema.TaskCreate) -> Task:
  existing_task = db.query(Task).filter(Task.task_id == task.task_id, Task.project_id == project_id).first()
  if existing_task:
    update_task(db, project_id, task.task_id, task.image, task.additional_data)
    return existing_task
  else:
    new_task = Task(
        task_id=task.task_id,
        project_id=project_id,
        image=task.image,
        additional_data=json.dumps(task.additional_data)
    )
    try:
      db.add(new_task)
      db.commit()
      db.refresh(new_task)
    except IntegrityError:
      db.rollback()
    return new_task

def get_task(db: Session, task_id: str) -> Optional[Task]:
  return db.query(Task).filter(Task.task_id == task_id).first()

def get_tasks_in_project(db: Session, project_id: int) -> List[Task]:
  return db.query(Task).filter(Task.project_id == project_id).all()

def assign_task_to_user(db: Session, task_id: str, project_id: int, user: User):
  task = get_task(db, task_id, project_id)
  if task:
    task.assigned_users.append(user)
    db.commit()
    db.refresh(task)
  return task

def assign_task(db: Session, task_id: str, user_id: int, assignment_type: schema.AssignmentType):
  existing_assignment = db.query(AssignedTask).filter_by(task_id=task_id, user_id=user_id, assignment_type=assignment_type).first()
  if existing_assignment:
    return existing_assignment

  assigned_task = AssignedTask(task_id=task_id, user_id=user_id, assignment_type=assignment_type)
  db.add(assigned_task)
  db.commit()
  db.refresh(assigned_task)
  return assigned_task

def unassign_task(db: Session, task_id: str, assignment_type: schema.AssignmentType):
  existing_assignment = db.query(AssignedTask).filter_by(task_id=task_id,
                        assignment_type=assignment_type).first()
  if not existing_assignment:
    return
  db.delete(existing_assignment)
  db.commit()
  return

def get_users_assigned_to_task(db: Session, task_id: str, project_id: int):
  assigned_users = (
      db.query(AssignedTask)
      .join(Task, Task.task_id == AssignedTask.task_id)
      .filter(Task.project_id == project_id, Task.task_id == task_id)
      .all()
  )
  return assigned_users

def get_assigned_users_for_task(db: Session, task_id: str):
  annotators_subquery = (
      db.query(AssignedTask.user_id)
      .filter(
          AssignedTask.task_id == task_id,
          AssignedTask.assignment_type == schema.AssignmentType.annotation
      )
      .subquery()
  )
  
  annotators = (
      db.query(User)
      .filter(User.user_id.in_(annotators_subquery))
      .all()
  )
  reviewers_subquery = (
      db.query(AssignedTask.user_id)
      .filter(
          AssignedTask.task_id == task_id,
          AssignedTask.assignment_type == schema.AssignmentType.review
      )
      .subquery()
  )
  
  reviewers = (db.query(User)
      .filter(User.user_id.in_(reviewers_subquery))
      .all()
  )
  return (annotators, reviewers)

def auto_assign_tasks_to_users(db: Session, project_id: int):
  tasks = get_tasks_in_project(db, project_id)
  annotators = get_users_by_role(db, schema.UserRole.annotator)
  max_annotators_per_task = (
      db.query(Project)
      .filter(Project.project_id == project_id)
      .first()
      .max_annotators_per_task
  )
  if len(tasks) > 0 and len(annotators) > 0:
    tasks_to_annotators_map = round_robin_algorithm(tasks, annotators, max_annotators_per_example=max_annotators_per_task)
    for task_id, annotator_ids in tasks_to_annotators_map.items():
      for annotator_id in annotator_ids:
        assign_task(db, task_id, annotator_id, schema.AssignmentType.annotation)
    return tasks
  return []

def update_task(db: Session, task_id: str, image: Optional[str] = None, additional_data: Optional[str] = None) -> Optional[Task]:
  task = get_task(db, task_id)
  if task is None:
      return None
  if image:
      task.image = image
  if additional_data:
      task.additional_data = additional_data
  db.commit()
  db.refresh(task)
  return task

def delete_task(db: Session, task_id: str) -> Optional[Task]:
  task = get_task(db, task_id)
  if task is None:
    return None
  db.delete(task)
  db.commit()
  return task

# Annotation CRUD operations
def create_annotation(db: Session, label: str, task_id: str, annotator_id: int) -> Annotation:
  annotation = (db.query(Annotation)
                .filter(Annotation.task_id == task_id, 
                Annotation.user_id == annotator_id).first()
  )
  annotation = Annotation(
      label=label,
      task_id=task_id,
      user_id=annotator_id
  )
  db.add(annotation)
  db.commit()
  db.refresh(annotation)
  return annotation

def get_default_label(db: Session, task_id: str, user_id: int):
  return (db.query(Annotation)
          .filter(Annotation.task_id == task_id, Annotation.user_id == user_id)
          .first())

def get_default_review(db: Session, task_id: str, user_id: int):
  return (db.query(Review)
          .filter(Review.task_id == task_id, Review.user_id == user_id)
          .first())

def get_annotation(db: Session, annotation_id: int) -> Optional[Annotation]:
  return db.query(Annotation).filter(Annotation.annotation_id == annotation_id).first()

def get_annotations(db: Session, project_id: int) -> List[Annotation]:
  query = db.query(Annotation).join(Task).filter(Task.project_id == project_id)
  return query.all()


def get_annotation_by_task_annotator(db: Session, task_id: Optional[str] = None, annotator_id: Optional[int] = None) -> List[Annotation]:
  query = db.query(Annotation)
  if task_id:
    query = query.filter(Annotation.task_id == task_id)
  if annotator_id:
    query = query.filter(Annotation.user_id == annotator_id)
  return query.first()

def get_review_by_task_reviewer(db: Session, task_id: Optional[str] = None, reviewer_id: Optional[int] = None) -> List[Review]:
  query = db.query(Review)
  if task_id:
    query = query.filter(Review.task_id == task_id)
  if reviewer_id:
    query = query.filter(Review.user_id == reviewer_id)
  return query.first()

def get_tasks_with_annotations(db: Session, project_id: int):
  tasks = (
    db.query(Task)
    .join(Project)
    .filter(Task.project_id == project_id)
    .all()
  )
  
  tasks_with_annotations = []
  for task in tasks:
    annotations = db.query(Annotation).filter(Annotation.task_id == task.task_id).all()
    if annotations:
      task_info = {
        "task_id": task.task_id,
        "image": task.image,
        "labels": [annotation.label for annotation in annotations]
      }
      tasks_with_annotations.append(task_info)
  
  return tasks_with_annotations

def update_annotation(db: Session, annotation_id: int, label: Optional[str] = None) -> Optional[Annotation]:
  annotation = get_annotation(db, annotation_id)
  if annotation is None:
    return None
  if label:
    annotation.label = label
  db.commit()
  db.refresh(annotation)
  return annotation

def delete_annotation(db: Session, annotation_id: int) -> Optional[Annotation]:
  annotation = get_annotation(db, annotation_id)
  if annotation is None:
      return None
  db.delete(annotation)
  db.commit()
  return annotation

# Review CRUD operations
def create_review(db: Session, label: str, task_id: str, reviewer_id: int) -> Review:
  review = (db.query(Review)
            .filter(Review.task_id == task_id, 
            Review.user_id == reviewer_id).first()
  )
  
  if review:
    review.label = label
  else:
    review = Review(
        label=label,
        task_id=task_id,
        user_id=reviewer_id
    )
    db.add(review)
  db.commit()
  db.refresh(review)
  return review

def get_review(db: Session, review_id: int) -> Optional[Review]:
  return db.query(Review).filter(Review.review_id == review_id).first()

def get_reviews(db: Session, task_id: Optional[str] = None, reviewer_id: Optional[int] = None) -> List[Review]:
  query = db.query(Review)
  if task_id:
    query = query.filter(Review.task_id == task_id)
  if reviewer_id:
    query = query.filter(Review.user_id == reviewer_id)
  return query.all()

def update_review(db: Session, review_id: int, label: Optional[str] = None) -> Optional[Review]:
  review = get_review(db, review_id)
  if review is None:
    return None
  if label:
    review.label = label
  db.commit()
  db.refresh(review)
  return review

def update_annotation(db: Session, annotation_id: int, label: Optional[str] = None) -> Optional[Annotation]:
  annotation = get_annotation(db, annotation_id)
  if annotation is None:
    return None
  if label:
    annotation.label = label
  db.commit()
  db.refresh(annotation)
  return annotation

def delete_review(db: Session, review_id: int) -> Optional[Review]:
  review = get_review(db, review_id)
  if review is None:
    return None
  db.delete(review)
  db.commit()
  return review

# Assignment and Task fetch
def get_assigned_tasks_by_type(db: Session, user_id: int, assignment_type: schema.AssignmentType):
  return db.query(Task).join(AssignedTask).filter(
      AssignedTask.user_id == user_id,
      AssignedTask.assignment_type == assignment_type
  ).all()

def get_assigned_tasks_by_type_and_project(db: Session, user_id: int, assignment_type: schema.AssignmentType, project_id: int):
  return db.query(Task).join(AssignedTask).filter(
      AssignedTask.user_id == user_id,
      AssignedTask.assignment_type == assignment_type,
      Task.project_id == project_id
  ).all()

def get_assigned_tasks(db: Session, user_id: int) -> List[AssignedTask]:
  return db.query(AssignedTask).filter(AssignedTask.user_id == user_id).all()

def get_completed_annotations(db: Session, project_id: int):
  max_annotators_per_task = get_project(db, project_id).max_annotators_per_task
  return db.query(Task)\
          .join(Task.annotations)\
          .filter(Task.project_id == project_id)\
          .group_by(Task.task_id)\
          .having(func.count('*') >= max_annotators_per_task)\
          .all()