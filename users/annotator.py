from typing import List
from utils.logger import logger
from data.database import Annotator
from data.database import AssignedAnnotator
from data.database import Example
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from utils.database_helper import run_within_session


class AnnotatorRepository:
  def __init__(self, session: Session):
    self.session = session

  def add_annotator(self, username: str, email: str = None) -> Annotator:
    existing_annotator = self.session.query(Annotator).filter_by(username=username).first()
    if existing_annotator is None:
      new_annotator = Annotator(username=username, email=email)
      try:
        self.session.add(new_annotator)
        self.session.commit()
        logger.log_info(f"Added new annotator '{username}'")
      except Exception as e:
        self.session.rollback()
        logger.log_exception(e, f"Error adding annotator '{username}': {e}")
    else:
      logger.log_warning(f"Annotator with username '{username}' already exists")

  def remove_annotator(self, annotator_id: int) -> None:
    annotator = self.session.query(Annotator).get(annotator_id)
    if annotator:
      self.session.delete(annotator)
      self.session.commit()

  def get_annotator_by_id(self, annotator_id: int) -> Annotator:
    return self.session.query(Annotator).get(annotator_id)

  def get_annotator_by_username(self, username: str) -> Annotator:
    return self.session.query(Annotator).filter_by(username=username).first()
  
  def list_annotators(self):
    return self.session.query(Annotator).all()
  
  def grant_annotator_access(self, username):
    self.session.execute(text(f'GRANT SELECT ON ALL TABLES IN SCHEMA public TO {username};'))
    self.session.execute(text(f'GRANT INSERT, UPDATE on annotations TO {username};'))
    self.session.execute(text(f'GRANT USAGE, SELECT ON SEQUENCE annotations_annotation_id_seq TO {username};'))
    self.session.commit()


class AnnotatorService:
  def __init__(self, session: Session):
    self.session = session
    self.annotator_repo = AnnotatorRepository(session)