from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from skainnotate.data.database import Reviewer
from skainnotate.data.database import AssignedReviewer
from skainnotate.data.database import Example
from skainnotate.utils.logger import logger


class ReviewerRepository:
  def __init__(self, session: Session):
    self.session = session

  def add_reviewer(self, username: str, email: str = None) -> Reviewer:
    existing_reviewer = self.session.query(Reviewer).filter_by(username=username).first()

    if existing_reviewer is None:
      new_reviewer = Reviewer(username=username, email=email)
      try:
        self.session.add(new_reviewer)
        self.session.commit()
        logger.log_info(f"Added new reviewer '{username}'")
      except Exception as e:
        self.session.rollback()
        logger.log_exception(e, f"Error adding reviewer '{username}': {e}")
    else:
      logger.log_warning(f"Annotator with username '{username}' already exists")

  def remove_reviewer(self, reviewer_id: int) -> None:
    reviewer = self.session.query(Reviewer).get(reviewer_id)
    if reviewer:
      self.session.delete(reviewer)
      self.session.commit()

  def get_reviewer_by_id(self, reviewer_id: int) -> Reviewer:
    return self.session.query(Reviewer).get(reviewer_id)

  def get_reviewer_by_username(self, username: str) -> Reviewer:
    return self.session.query(Reviewer).filter_by(username=username).first()
  
  def list_reviewers(self):
    return self.session.query(Reviewer).all()
  
  def grant_reviewer_access(self, username):
    self.session.execute(text(f'GRANT SELECT ON ALL TABLES IN SCHEMA public TO {username};'))
    self.session.execute(text(f'GRANT INSERT, UPDATE on reviewers TO {username};'))
    self.session.execute(text(f'GRANT USAGE, SELECT ON SEQUENCE reviewers_reviewer_id_seq TO {username};'))
    self.session.commit()

class ReviewerService:
  def __init__(self, session):
    self.session = session
    self.reviewer_repo = ReviewerRepository(session)

  def get_tasks_assigned_to_reviewer(self, reviewer_id: int):
    reviewer = self.reviewer_repo.get_reviewer_by_id(reviewer_id)
    assigned_examples = (
      self._session.query(Example)
        .join(AssignedReviewer, Example.example_id == AssignedReviewer.example_id)
        .join(Reviewer, Reviewer.annotator_id == AssignedReviewer.annotator_id)
        .filter(Reviewer.username == reviewer.username)
        .all()
      )
    return assigned_examples

  def track_review_progress(self, reviewer_id: int):
    #TODO Implementation details to track review progress
    pass
  # Add more methods as needed for reviewer-related operations