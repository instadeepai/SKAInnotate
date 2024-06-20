import os
import re
from google.cloud import storage
from pathlib import Path
from skainnotate.utils.logger import logger

def split_gcs_path(path: str):
  if path.startswith("gs://"):
    path = path.split('gs://')[-1]
    bucket_name, *bucket_prefix, filename = path.split('/')
    bucket_prefix = '/'.join(bucket_prefix)
  return bucket_name, bucket_prefix, filename

def list_files_from_gcs(bucket_path):
  """Lists all the blobs in the bucket."""
  if bucket_path.startswith('gs://'):
    bucket_name, bucket_prefix, _ = split_gcs_path(bucket_path)

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

def download_images_from_gcs(assigned_tasks: list, output_path: str
  ) -> None:
    logger.log_info("Downloading new examples")
    for task in assigned_tasks:
      bucket_name, bucket_prefix, image_filename = split_gcs_path(task.image)
      if not os.path.exists(output_path):
        os.makedirs(output_path)

      client = storage.Client()
      bucket = client.bucket(bucket_name)

      blob = bucket.blob(os.path.join(bucket_prefix, image_filename))
      image_basepath = "_".join([str(task.example_id), image_filename])
      image_filepath = os.path.join(output_path, image_basepath)
      try:
        blob.download_to_filename(image_filepath)
      except Exception as e:
        logger.log_exception(e, f"Error downloading image: {e}")
    logger.log_info("Done!")