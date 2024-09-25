from typing import List
import datetime
import reprlib
from sqlalchemy.sql import func
import sqlalchemy as sqla
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Table, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()
import core.backend.app.schema as schema

# Association table for the many-to-many relationship between users and roles
# We want user to potentially have more than one role
user_roles = Table('user_roles', Base.metadata,
                   Column('user_id', Integer, ForeignKey('users.user_id'), primary_key=True),
                   Column('role_id', Integer, ForeignKey('roles.role_id'), primary_key=True))

# Association table for the many-to-many relationship between users and tasks
#
user_tasks = Table('user_tasks', Base.metadata,
                   Column('user_id', Integer, ForeignKey('users.user_id'), primary_key=True),
                   Column('task_id', String(255), ForeignKey('tasks.task_id'), primary_key=True))

class Project(Base):
  __tablename__ = 'projects'

  project_id = Column(Integer, primary_key=True, autoincrement=True)
  project_title = Column(String(255), nullable=False)
  project_description = Column(String(255), nullable=True, default="")
  created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
  labels = Column(String(255), nullable=False, default="")
  max_annotators_per_task = Column(Integer, nullable=True, default=1)
  completion_deadline = Column(TIMESTAMP, nullable=True)

  tasks = relationship("Task", back_populates="project", cascade='all, delete-orphan')

  def __repr__(self) -> str:
    return (f'Project('
            f'project_id={self.project_id!r}, '
            f'project_title={self.project_title!r}, '
            f'created_at={self.created_at!r}, '
            f'labels={self.labels!r}, '
            f'max_annotators_per_task={self.max_annotators_per_task!r}, '
            f'completion_deadline={self.completion_deadline!r})')

class Task(Base):
  __tablename__ = 'tasks'

  task_id = Column(String(255), primary_key=True)
  project_id = Column(Integer, ForeignKey('projects.project_id'), nullable=False)
  image = Column(String(255), nullable=False)
  additional_data = Column(Text, nullable=True)

  project = relationship("Project", back_populates="tasks")
  annotations = relationship("Annotation", back_populates="task")
  reviews = relationship("Review", back_populates="task")
  assigned_tasks = relationship("AssignedTask", back_populates="task")
  users = relationship("User", secondary=user_tasks, back_populates="tasks")

  def __repr__(self) -> str:
    return (f'Task('
            f'task_id={self.task_id!r}, '
            f'project_id={self.project_id!r}, '
            f'image={self.image!r}, '
            f'annotations={reprlib.repr(self.annotations)}, '
            f'reviews={reprlib.repr(self.reviews)})')

class User(Base):
  __tablename__ = 'users'

  user_id = Column(Integer, primary_key=True, autoincrement=True)
  username = Column(String(255))
  email = Column(String(255), nullable=True)

  annotations = relationship("Annotation", back_populates="user")
  reviews = relationship("Review", back_populates="user")
  assigned_tasks = relationship("AssignedTask", back_populates="user")
  tasks = relationship("Task", secondary=user_tasks, back_populates="users")
  roles = relationship('Role', secondary=user_roles, back_populates='users')

  def __repr__(self) -> str:
    return (f'User('
            f'user_id={self.user_id!r}, '
            f'username={self.username!r}, '
            f'email={self.email!r})')

class Role(Base):
  __tablename__ = 'roles'

  role_id = Column(Integer, primary_key=True, autoincrement=True)
  role_name = Column(String(255), nullable=False, unique=True)

  users = relationship('User', secondary=user_roles, back_populates='roles')

  def __repr__(self) -> str:
    return (f'Role('
            f'role_id={self.role_id!r}, '
            f'role_name={self.role_name!r})')

class Annotation(Base):
  __tablename__ = 'annotations'

  annotation_id = Column(Integer, primary_key=True, autoincrement=True)
  label = Column(String(60), nullable=False)
  task_id = Column(String(255), ForeignKey('tasks.task_id'), nullable=False)
  user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)

  task = relationship("Task", back_populates='annotations')
  user = relationship("User", back_populates='annotations')

  def __repr__(self) -> str:
    return (f'Annotation('
            f'annotation_id={self.annotation_id!r}, '
            f'label={self.label!r}, '
            f'task_id={self.task_id!r}, '
            f'user_id={self.user_id!r})')

class Review(Base):
  __tablename__ = 'reviews'

  review_id = Column(Integer, primary_key=True, autoincrement=True)
  label = Column(String(60), nullable=False)
  task_id = Column(String(255), ForeignKey('tasks.task_id'), nullable=False)
  user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)

  task = relationship("Task", back_populates='reviews')
  user = relationship("User", back_populates='reviews')

  def __repr__(self) -> str:
    return (f'Review('
            f'review_id={self.review_id!r}, '
            f'label={self.label!r}, '
            f'task_id={self.task_id!r}, '
            f'user_id={self.user_id!r})')

class AssignedTask(Base):
  __tablename__ = 'assigned_tasks'

  assignment_id = Column(Integer, primary_key=True, autoincrement=True)
  task_id = Column(String(255), ForeignKey('tasks.task_id'), nullable=False)
  user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
  assignment_type = Column(sqla.Enum(schema.AssignmentType), nullable=False)

  task = relationship("Task", back_populates="assigned_tasks")
  user = relationship("User", back_populates="assigned_tasks")

  def __repr__(self) -> str:
    return (f'AssignedTask('
            f'assignment_id={self.assignment_id!r}, '
            f'task_id={self.task_id!r}, '
            f'user_id={self.user_id!r}, '
            f'assignment_type={self.assignment_type!r})')