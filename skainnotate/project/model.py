import re
from skainnotate.data.database import ProjectConfigurations
from skainnotate.utils.database_helper import run_within_session
from skainnotate.utils.logger import logger

class ProjectRepository:
  def __init__(self, session) -> None:
    self.session = session
    self.configs = None

  # @run_within_session
  def get_project_configs(self):
    configs = (self.session.query(ProjectConfigurations).first())
    if configs is None:
      configs = ProjectConfigurations()
      self.session.add(configs)
      self.session.commit()
    return configs

  def get_project_title(self):
    project_configs = self.get_project_configs()
    if project_configs and project_configs.project_title:
      return project_configs.project_title
    else:
      logger.log_info("Project Title not set")

  @run_within_session
  def set_project_title(self, project_title):
    project_configs = self.get_project_configs()
    project_configs.project_title = project_title

  def get_bucket_name(self):
    project_configs = self.get_project_configs()
    if project_configs and project_configs.bucket_name:
      return project_configs.bucket_name
    else:
      logger.log_info("Bucket name not set")
  
  @run_within_session
  def set_bucket_name(self, bucket_name):
    project_configs = self.get_project_configs()
    project_configs.bucket_name = bucket_name

  def get_bucket_prefix(self):
    project_configs = self.get_project_configs()
    if project_configs and project_configs.bucket_prefix:
      return project_configs.bucket_prefix
    else:
      logger.log_info("Bucket prefix not set")
  
  @run_within_session
  def set_bucket_prefix(self, bucket_prefix):
    project_configs = self.get_project_configs()
    project_configs.bucket_prefix = bucket_prefix

  def get_labels(self):
    project_configs = self.get_project_configs()
    if project_configs and project_configs.comma_separated_labels:
      return project_configs.comma_separated_labels.split(",")
    else:
      logger.log_info("Labels not set")
  

  @run_within_session
  def set_labels(self, labels):
    project_configs = self.get_project_configs()
    project_configs.comma_separated_labels = labels

  def get_max_annotators_per_example(self):
    project_configs = self.get_project_configs()
    if project_configs and project_configs.max_annotators_per_example:
      return project_configs.max_annotators_per_example
    else:
      logger.log_info("Max annotators per example value not set")

  @run_within_session
  def set_max_annotators_per_example(self, max_annotators_per_example):
    project_configs = self.get_project_configs()
    project_configs.max_annotators_per_example = max_annotators_per_example

  def get_completion_deadline(self):
    project_configs = self.get_project_configs()
    if project_configs and project_configs.completion_deadline:
      return project_configs.completion_deadline
    else:
      logger.log_info("Completion deadline not set")

  @run_within_session
  def set_completion_deadline(self, completion_deadline):
    project_configs = self.get_project_configs()
    project_configs.completion_deadline = completion_deadline


class ProjectConfigs:
  _instance = None

  def __new__(cls, session):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
      cls._instance.project_repo = ProjectRepository(session)
    return cls._instance

  @property
  def project_title(self):
    return self.project_repo.project_title

  @project_title.setter
  def project_title(self, project_title):
    self.project_repo.set_project_title(project_title)

  @property
  def bucket_name(self):
    return self.project_repo.get_bucket_name()
  
  @bucket_name.setter
  def bucket_name(self, bucket_name):
    self.project_repo.set_bucket_name(bucket_name)

  @property
  def bucket_prefix(self):
    return self.project_repo.get_bucket_prefix()

  @bucket_prefix.setter
  def bucket_prefix(self, bucket_prefix):
    self.project_repo.set_bucket_prefix(bucket_prefix)

  @property
  def labels(self):
    return self.project_repo.get_labels()
  
  @labels.setter
  def labels(self, labels):
    def process_labels(labels):
      return ','.join([re.sub('\s+',' ', label).strip(' ') for label in labels])
    labels = process_labels(labels)
    self.project_repo.set_labels(labels)

  @property
  def max_annotators_per_example(self):
    return self.project_repo.get_max_annotators_per_example()

  @max_annotators_per_example.setter
  def max_annotators_per_example(self, max_annotators_per_example):
    self.project_repo.set_max_annotators_per_example(max_annotators_per_example)

  @property
  def completion_deadline(self):
    return self.project_repo.get_completion_deadline()

  @completion_deadline.setter
  def completion_deadline(self, completion_deadline):
    self.project_repo.set_completion_deadline(completion_deadline)

  def get_project_configs(self):
    return self.project_repo.get_project_configs()