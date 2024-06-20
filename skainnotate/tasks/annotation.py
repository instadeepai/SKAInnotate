import sqlalchemy as sqla
from sqlalchemy.orm import Session
from typing import List
from skainnotate.data.database import Annotation
from skainnotate.data.database import Example
from skainnotate.data.database import Annotator
from skainnotate.data.database import AssignedAnnotator
from skainnotate.utils.logger import logger

class AnnotationRepository:
  def __init__(self, session: Session):
    self.session = session

  def add_annotation(self, label: str, example_id: str, annotator_id: int) -> Annotation:
    # Implementation details for adding a new annotation
    existing_annotation = (
          self.session.query(Annotation)
          .filter_by(example_id=example_id, annotator_id=annotator_id)
          .first()
      )
    if existing_annotation:
      self.update_annotation(existing_annotation, label)
      logger.log_info(f"Update- example_id: {example_id} label: {label}")
    else:
      self.add_new_annotation(annotator_id=annotator_id, example_id=example_id, label=label)
    return 

  def add_new_annotation(self, annotator_id: int, example_id: str, label: str) -> Annotation:
    # Implementation details for updating an existing annotation
    new_annotation = Annotation(
            example_id=example_id,
            label=label,
            annotator_id=annotator_id
        )
    try:
      self.session.add(new_annotation)
      self.session.commit()
      logger.log_info(f"New- example_id: {example_id} label: {label}")
    except Exception as e:
      logger.log_exception(e, "Error adding new annotation:", e)
      self.session.rollback()
    return

  def update_annotation(self, annotation: Annotation, label: str):
    try:
      annotation.label = label
      self.session.commit()

    except Exception as e:
      logger.log_exception(e, "Error updating annotation:", e)
      self.session.rollback()

  def get_annotation_by_id(self, annotation_id: int) -> Annotation:
    return (self.session.query(Annotation).filter_by(annotation_id=annotation_id)
          .first())

  def get_annotations_for_example(self, example_id: str, annotator_id: int) -> List[Annotation]:
    # Implementation details for retrieving all annotations for a specific example
    return self.session.query(Annotation).filter_by(example_id=example_id, annotator_id=annotator_id).first()
  
  def delete_annotation(self, annotation_id: int) -> None:
    # Implementation details for deleting an annotation
    self.session.query(Annotation).filter(annotation_id == annotation_id).delete()
    self.session.commit()

  def get_tasks_assigned_to_annotator(self, annotator_id: int, annotator_username: str):
    annotator = (
      self.session.query(Annotator).filter(
        sqla.or_(Annotator.annotator_id==annotator_id, Annotator.username==annotator_username)
        )
    ).first()
    assigned_examples = []
    if annotator:
      assigned_examples = (
        self.session.query(Example)
          .join(AssignedAnnotator, Example.example_id == AssignedAnnotator.example_id)
          .join(Annotator, Annotator.annotator_id == AssignedAnnotator.annotator_id)
          .filter(Annotator.username == annotator.username)
          .all()
        )
    return assigned_examples
  
  def get_completed_annotations(self):
    return self.session.query(Annotation).all()

  def get_annotator(self, annotator_id, annotator_username):
    return (self.session.query(Annotator)
      .filter(sqla.or_(Annotator.annotator_id==annotator_id, Annotator.username==annotator_username))
      ).first()

class AnnotationWorkflow:
  def __init__(self, session: Session):
    self.session = session
    self.annotation_repo = AnnotationRepository(session)

  def add_annotation(self, label: str, example_id: str, annotator_id: int) -> Annotation:
    # Implementation details to add a new annotation
    self.annotation_repo.add_annotation(label, example_id, annotator_id)

  def get_annotation_by_id(self, annotation_id: int) -> Annotation:
    # Implementation details to retrieve an annotation by ID
    return self.annotation_repo.get_annotation_by_id(annotation_id)

  def get_annotations_for_example(self, example_id: str, annotator_id: int) -> List[Annotation]:
    # Implementation details to retrieve all annotations for a specific example
    return self.annotation_repo.get_annotations_for_example(example_id, annotator_id)

  def get_completed_annotations(self):
    return self.annotation_repo.get_completed_annotations()

  def delete_annotation(self, annotation_id: int) -> None:
    # Implementation details to delete an annotation
    self.annotation_repo.delete_annotation(annotation_id)
  
  def get_tasks_assigned_to_annotator(self, annotator_id: int, annotator_username):
    return self.annotation_repo.get_tasks_assigned_to_annotator(annotator_id, annotator_username)
  
  def track_progress(self, annotator_id: int): # -> ProgressReport:
    annotator = self.annotation_repo.get_annotator_by_id(annotator_id)
    progress_report = {}  # Replace with actual logic to calculate progress
    return progress_report
  
  def get_annotator(self, annotator_id=None, annotator_username=None):
    return self.annotation_repo.get_annotator(annotator_id, annotator_username)
