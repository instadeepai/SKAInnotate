import os
import re
from skainnotate.utils.logger import logger

def validate_email(email):
  """ Validate email format. """
  if not re.match(r'^[\w\.-]+@[\w\.-]+$', email):
    raise ValueError("Invalid email format")

def validate_file_path(file_path):
  """ Validate file path exists and is accessible. """
  if not os.path.exists(file_path):
    raise FileNotFoundError(f"File not found at {file_path}")
  if not os.access(file_path, os.R_OK):
    raise PermissionError(f"Permission denied for {file_path}")

def validate_annotation_data(annotation):
  """ Validate annotation data format and content. """
  if 'label' not in annotation:
    raise ValueError("Annotation must have a 'label' field")
  if not isinstance(annotation['label'], str):
    raise TypeError("Annotation label must be a string")

def validate_project_configuration(config):
  """ Validate project configuration settings. """
  if 'max_annotators_per_example' in config:
    if not isinstance(config['max_annotators_per_example'], int):
        raise TypeError("Max annotators per example must be an integer")
