from typing import List
from sqlalchemy.orm import Session
from skainnotate.data.database import Review
from skainnotate.data.database import Example
from skainnotate.data.database import Reviewer
from skainnotate.data.database import AssignedReviewer
from skainnotate.utils.logger import logger

class ReviewRepository:
  def __init__(self, session: Session):
    self.session = session

  def add_review(self, label: str, example_id: str, reviewer_id: int) -> Review:
    # Implementation details for adding a new review
    existing_review = (
          self.session.query(Review)
          .filter_by(example_id=example_id, review_id=reviewer_id)
          .first()
      )
    if existing_review:
      self.update_review(existing_review, label)
      logger.log_info(f"Update- example_id: {example_id} label: {label}")
    else:
      self.add_new_review(reviewer_id=reviewer_id, example_id=example_id, label=label)
    return 

  def add_new_review(self, reviewer_id: int, example_id: str, label: str) -> Review:
    # Implementation details for updating an existing review
    new_review = Review(
            example_id=example_id,
            label=label,
            reviewer_id=reviewer_id
        )
    try:
      self.session.add(new_review)
      self.session.commit()
      logger.log_info(f"New- example_id: {example_id} label: {label}")
    except Exception as e:
      logger.log_exception(e, "Error adding new review:")
      self.session.rollback()
    return

  def update_review(self, review: Review, label: str):
    try:
      review.label = label
      self.session.commit()

    except Exception as e:
      logger.log_exception(e, "Error updating review:", e)
      self.session.rollback()

  def get_review_by_id(self, review_id: int) -> Review:
    return (self.session.query(Review).filter_by(review_id=review_id)
          .first())

  def get_reviews_for_example(self, example_id: str) -> List[Review]:
    # Implementation details for retrieving all reviews for a specific example
    return self.session.query(Review).filter_by(example_id=example_id).all()
  
  def delete_review(self, review_id: int) -> None:
    # Implementation details for deleting an review
    self.session.query(Review).filter(review_id == review_id).delete()
    self.session.commit()

    # def get_completed_reviews(self):
    #   return self.review_repo.get_completed_reviews()
  
  def get_tasks_assigned_to_reviewer(self, reviewer_id: int):
    reviewer = self.session.query(Reviewer).filter(Reviewer.reviewer_id==reviewer_id).first()

    assigned_examples = []
    if reviewer:
      assigned_examples = (
        self.session.query(Example)
          .join(AssignedReviewer, Example.example_id == AssignedReviewer.example_id)
          .join(Reviewer, Reviewer.reviewer_id == AssignedReviewer.reviewer_id)
          .filter(Reviewer.username == reviewer.username)
          .all()
        )
    return assigned_examples

class ReviewWorkflow:
  def __init__(self, session: Session):
    self.session = session
    self.review_repo = ReviewRepository(session)

  def add_review(self, label: str, example_id: str, review_id: int) -> Review:
    # Implementation details to add a new review
    self.review_repo.add_review(label, example_id, review_id)

  def get_review_by_id(self, review_id: int) -> Review:
    # Implementation details to retrieve an review by ID
    return self.review_repo.get_review_by_id(review_id)

  def get_reviews_for_example(self, example_id: str) -> List[Review]:
    # Implementation details to retrieve all reviews for a specific example
    return self.review_repo.get_reviews_for_example(example_id)

  def get_completed_reviews(self):
    return self.review_repo.get_completed_reviews()

  def delete_review(self, review_id: int) -> None:
    # Implementation details to delete an review
    self.review_repo.delete_review(review_id)
  
  def get_tasks_assigned_to_reviewer(self, reviewer_id: int):
    return self.review_repo.get_tasks_assigned_to_reviewer(reviewer_id)
  
  def track_progress(self, reviewer_id: int): # -> ProgressReport:
    reviewer = self.review_repo.get_reviewer_by_id(reviewer_id)
    progress_report = {}  # Replace with actual logic to calculate progress
    return progress_report
