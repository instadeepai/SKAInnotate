from typing import List
import datetime
import reprlib
import sqlalchemy as sqla
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import ENUM

Base = declarative_base()

class ProjectConfigurations(Base):
  __tablename__ = 'project_configurations'

  project_id = Column(Integer, primary_key=True, autoincrement=True)
  project_title = Column(String(255))
  bucket_name = Column(String(255))
  bucket_prefix = Column(String(255))
  comma_separated_labels = Column(String(255))
  max_annotators_per_example = Column(Integer)
  completion_deadline = Column(TIMESTAMP, default=datetime.datetime.now(datetime.UTC))
  created_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.UTC))

  def __repr__(self) -> str:
    return (f'ProjectConfigurations('
            f'project_title={self.project_title!r}, '
            f'bucket_name={self.bucket_name!r}, '
            f'bucket_prefix={self.bucket_prefix!r}, '
            f'comma_separated_labels={self.comma_separated_labels!r}, '
            f'max_annotation_per_example={self.max_annotators_per_example!r}, '
            f'completion_deadline={self.completion_deadline!r}, '
            f'created_at={self.created_at!r})')


class Example(Base):
  __tablename__ = 'examples'

  example_id = Column(String(255), primary_key=True, nullable=False)
  image = Column(String(255), nullable=False)
  annotation_status = Column(String(255), 
                             ENUM('complete', 'incomplete', 'under_review',
                                  name='annotation_status_enum'), 
                             default='incomplete')

  annotations = relationship("Annotation", back_populates="example")
  reviews = relationship("Review", back_populates="example")

  assigned_annotators = relationship("AssignedAnnotator", back_populates="example")
  assigned_reviewers = relationship("AssignedReviewer", back_populates="example")

  def __repr__(self) -> str:
    return (f'Example('
            f'example_id={self.example_id!r}, '
            f'image={self.image!r}, '
            f'annotations={reprlib.repr(self.annotations)})')
  

class Annotator(Base):
  __tablename__ = 'annotators'

  annotator_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
  username = Column(String(255))
  email = Column(String(255), nullable=True)

  annotations = relationship("Annotation", back_populates="annotator")
  assigned_annotators = relationship("AssignedAnnotator", back_populates="annotator")

  def __repr__(self) -> str:
    return (f'Annotator('
            f'annotator_id={self.annotator_id!r}, '
            f'username={self.username!r}, '
            f'email={self.email!r})')

class Reviewer(Base):
  __tablename__ = 'reviewers'

  reviewer_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
  username = Column(String(255))
  email = Column(String(255), nullable=True)

  reviews = relationship("Review", back_populates="reviewer")
  assigned_reviewers = relationship("AssignedReviewer", back_populates="reviewer")

  def __repr__(self) -> str:
    return (f'Reviewer('
            f'reviewer_id={self.reviewer_id!r}, '
            f'username={self.username!r}, '
            f'email={self.email!r})')


class Review(Base):
  __tablename__ = 'reviews'

  review_id = Column(Integer, primary_key=True, autoincrement=True)
  label = Column(String(60), nullable=False)
  example_id = Column(String(255), ForeignKey('examples.example_id'), nullable=False)
  example = relationship("Example", back_populates='reviews')

  reviewer_id = Column(Integer, ForeignKey('reviewers.reviewer_id'), nullable=False)
  reviewer = relationship("Reviewer", back_populates='reviews')

  def __repr__(self) -> str:
    return (f'Review('
            f'label={self.label!r}, '
            f'reviewer={reprlib.repr(self.reviewer)})')
  

class Annotation(Base):
  __tablename__ = 'annotations'

  annotation_id = Column(Integer, primary_key=True, autoincrement=True)
  label = Column(String(60), nullable=False)
  example_id = Column(String(255), ForeignKey('examples.example_id'), nullable=False)
  example = relationship("Example", back_populates='annotations')

  annotator_id = Column(Integer, ForeignKey('annotators.annotator_id'), nullable=False)
  annotator = relationship("Annotator", back_populates='annotations')

  def __repr__(self) -> str:
    return (f'Annotation('
            f'label={self.label!r}, '
            f'annotator={reprlib.repr(self.annotator)})')


class AssignedAnnotator(Base):
  __tablename__ = 'assigned_annotators'

  assignment_id = Column(Integer, primary_key=True, autoincrement=True)
  example_id = Column(String(255), ForeignKey('examples.example_id'), nullable=False)
  annotator_id = Column(Integer, ForeignKey('annotators.annotator_id'), nullable=False)

  example = relationship("Example", back_populates="assigned_annotators")
  annotator = relationship("Annotator", back_populates="assigned_annotators")

  def __repr__(self) -> str:
    return (f'AssignedAnnotator('
            f'assignment_id={self.assignment_id!r}, '
            f'example_id={self.example_id!r}, '
            f'annotator_id={self.annotator_id})')
  

class AssignedReviewer(Base):
  __tablename__ = 'assigned_reviewers'

  review_assignment_id = Column(Integer, primary_key=True, autoincrement=True)
  example_id = Column(String(255), ForeignKey('examples.example_id'), nullable=False)
  reviewer_id = Column(Integer, ForeignKey('reviewers.reviewer_id'), nullable=False)

  example = relationship("Example", back_populates="assigned_reviewers")
  reviewer = relationship("Reviewer", back_populates="assigned_reviewers")

  def __repr__(self) -> str:
    return (f'AssignedReviewer('
            f'review_assignment_id={self.review_assignment_id!r}, '
            f'example_id={self.example_id!r}, '
            f'reviewer_id={self.reviewer_id})')
