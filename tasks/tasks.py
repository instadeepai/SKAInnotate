import pandas as pd
from data.database import Annotator
from data.database import Annotation
from data.database import AssignedAnnotator
from data.database import Example
from tasks.assignments import round_robin_algorithm
from data.data_handlers import list_files_with_extensions
from utils.logger import logger

IMAGE_PATH_KEY = 'image_path'
USERNAME_KEY = 'username'
EXAMPLE_ID_KEY = 'example_id'

class TaskManagerRepository:
  def __init__(self, session):
    self.session = session

  def assign_tasks_to_annotators(self, max_annotators_per_example, return_assignments=False):
    session = self.session()
    assignments = []

    # Query annotators and tasks
    annotators = session.query(Annotator).all()
    examples = session.query(Example).all()
    # num_annotators = len(annotators)
    # num_examples = len(examples)
    example_annotator_map = round_robin_algorithm(examples, annotators, max_annotators_per_example)

    assignments = self.add_annotator_task_assignments(example_annotator_map)

    if return_assignments:
      return assignments

  def add_annotator_task_assignments(self, example_annotator_map: dict):
    assignments = []
    for example, annotator in example_annotator_map.items():
      assignments.append(
          AssignedAnnotator(annotator_id=annotator.annotator_id,
            example_id=example.example_id)
            )
    self.session.add_all(assignments)
    self.session.commit()
    return assignments

  def assign_tasks_to_reviewers(self):
    pass

  def fetch_tasks(self, bucket_name, bucket_prefix, csv_filename=None):
    metadata_file = self.download_csv_from_bucket(bucket_name, bucket_prefix, csv_filename)
    # if csv_filename:
    #   self._add_tasks_from_csv(session, metadata_file)

  def _add_tasks_from_gcs(self, gcs_path: str, file_extensions: list):
    '''
    Adding Tasks from CSV metadata
    Args:
      csv_path: path to CSV file with metadata
    Return:
      None
    '''

    files = list_files_with_extensions(gcs_path, file_extensions)
    id_path_tuples = [(id, file) for id, file in enumerate(files)]
    df = pd.DataFrame(id_path_tuples, columns=[EXAMPLE_ID_KEY, IMAGE_PATH_KEY])
    return self._add_tasks_from_dataframe(df)
  
  def _add_tasks_from_folder(self, data_path: str, file_extensions: list):
    '''
    Adding Tasks from CSV metadata
    Args:
      csv_path: path to CSV file with metadata
    Return:
      None
    '''

    files = list_files_with_extensions(data_path, file_extensions)
    id_path_tuples = [(id, file) for id, file in enumerate(files)]
    df = pd.DataFrame(id_path_tuples, columns=[EXAMPLE_ID_KEY, IMAGE_PATH_KEY])
    return self._add_tasks_from_dataframe(df)
    
  def _add_tasks_from_csv(self, csv_path: str, column_map: dict):
    '''
    Adding Tasks from CSV metadata
    Args:
      csv_path: path to CSV file with metadata
    Return:
      None
    '''
    example_id_col_name = column_map.get(EXAMPLE_ID_KEY) or EXAMPLE_ID_KEY
    image_path_col_name = column_map.get(IMAGE_PATH_KEY) or IMAGE_PATH_KEY
    df = pd.read_csv(csv_path)[[example_id_col_name, image_path_col_name]]
    df.columns=[EXAMPLE_ID_KEY, IMAGE_PATH_KEY]
    return self._add_tasks_from_dataframe(df)

  def _add_tasks_from_dataframe(self, tasks_df: pd.DataFrame) -> None:

    for _, row in tasks_df.iterrows():
      example_id = row[EXAMPLE_ID_KEY]
      existing_task = (self.session.query(Example)
                      .filter_by(example_id=str(example_id))
                      .first())

      if existing_task is None:
        task = Example(example_id=example_id, image=row[IMAGE_PATH_KEY])
        self.session.add(task)
        self.session.commit()
      else:
        logger.log_info(f"Task with example_id '{example_id}' already exists. Skipping.")
    logger.log_info("\n")

  def _list_tasks(self, limit):
    results = self.session.query(Example).all()
    limit = limit or len(results)
    return results[:limit]
  
  def show_assignments(self, limit):
    assigned_annotators = self.session.query(AssignedAnnotator).all()

    limit = limit or len(assigned_annotators)
    for assigned_annotator in assigned_annotators[:limit]:
      logger.log_info(f'Example ID: {assigned_annotator.example_id}, assigned to Annotator: {assigned_annotator.annotator.username}')

  def get_task_assignments(self):
    results = self.session.query(
      Example.example_id, Example.image, Example.annotation_status,
      Annotator.username, Annotator.email
    ).join(AssignedAnnotator, AssignedAnnotator.example_id==Example.example_id
    ).join(Annotator, Annotator.annotator_id==AssignedAnnotator.annotator_id)
    return results.all()
  
  def get_annotated_tasks(self, filters=None):
    # Define the select statement with joins
    """
    Filters are used to select the columns needed. It could be a list, set or dictionary
    If dictionary, it should have the column name and a label
    """
    session = self.session()
    return (session.query(Example.example_id.label("EXAMPLE ID"),
          Annotation.label.label("LABEL"),
          Annotator.username.label("ANNOTATOR USERNAME"))
          .join(Annotation, Example.example_id == Annotation.example_id)
          .join(Annotator, Annotation.annotator_id == Annotator.annotator_id)
          .order_by(Annotator.annotator_id)).all()

class TaskManager:
  def __init__(self, session) -> None:
    self.session = session
    self.task_manager_repo = TaskManagerRepository(session)

  def list_tasks(self, limit=None):
    return self.task_manager_repo._list_tasks(limit)
  
  def add_tasks_from_csv(self, csv_path, column_map: dict = {}):
    self.task_manager_repo._add_tasks_from_csv(csv_path, column_map)

  def add_tasks_from_folder(self, csv_path, file_extensions: list = []):
    self.task_manager_repo._add_tasks_from_folder(csv_path, file_extensions)

  def add_tasks_from_gcs(self, gcs_path, file_extensions: list = []):
    self.task_manager_repo._add_tasks_from_gcs(gcs_path, file_extensions)

  def assign_tasks_to_annotators(self, max_annotators_per_example, return_assignments=False):
    return self.task_manager_repo.assign_tasks_to_annotators(max_annotators_per_example, return_assignments)
  
  def assign_tasks_to_reviewers(self):
    self.task_manager_repo.assign_tasks_to_reviewers()

  def get_task_assignments(self):
    return self.task_manager_repo.get_task_assignments()
  
  def get_annotated_tasks(self):
    return self.task_manager_repo.get_annotated_tasks()
