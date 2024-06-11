import os
import re
from google.cloud import storage
from pathlib import Path
from utils.logger import logger

def split_gcs_path(gcs_path: str):
  # Define the regex pattern
  pattern_with_prefix = r'^gs://([a-zA-Z0-9_-]+)/(.+)$'
  pattern_without_prefix = r'^gs://([a-zA-Z0-9_-]+)$'

  # Match the pattern against the filepath
  match_with_prefix = re.match(pattern_with_prefix, gcs_path)
  match_without_prefix = re.match(pattern_without_prefix, gcs_path)
  bucket_prefix = ''

  if match_with_prefix:
    bucket_name = match_with_prefix.group(1)
    bucket_prefix = match_with_prefix.group(2)

  elif match_without_prefix:
    bucket_name = match_without_prefix.group(1)
      
  else:
    logger.log_warning("No match found for the pattern.")
  return bucket_name, bucket_prefix

def list_files_from_gcs(bucket_path):
  """Lists all the blobs in the bucket."""
  if bucket_path.startswith('gs://'):
    bucket_name, bucket_prefix = split_gcs_path(bucket_path)

  storage_client = storage.Client()

  # Note: Client.list_blobs requires at least package version 1.17.0.
  blobs = storage_client.list_blobs(bucket_name, prefix=bucket_prefix)

  # Note: The call returns a response only when the iterator is consumed.
  files = []
  for blob in blobs:
    files.append(f'gs://{bucket_name}/{blob.name}')
  return files

def list_files_with_extensions(directory, extensions):
  """
  List files in a directory ending with any extension from a list of extensions.
  
  Args:
  - directory (str): Path to the directory to search for files.
  - extensions (list of str): List of extensions (without '.') to filter files.
  
  Returns:
  - list: List of file names with specified extensions in the directory.
  """

  if directory.startswith('gs://'):
    files = list_files_from_gcs(directory)
  # Validate directory exists
  else:
    try:
      files = os.listdir(directory)
    except FileNotFoundError as fnferror:
      logger.log_exception(fnferror, f"Directory '{directory}' does not exist.")

  filtered_files = [
    file for file in files 
    if any(file.endswith(ext)
      for ext in extensions)]
  
  return filtered_files

def download_csv_from_bucket(
    bucket_name: str, bucket_prefix: str, csv_filename: str, path: Path
    ) -> Path:
  # path = 'metadata.csv' #use temp file if not provided
  client = storage.Client()
  bucket = client.bucket(bucket_name=bucket_name)
  blob = bucket.blob(os.path.join(bucket_prefix, csv_filename))
  blob.download_to_filename(path)

  return path