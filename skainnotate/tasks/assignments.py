from typing import List
import pandas as pd
from collections import Counter
from data.database import Annotator
from data.database import Example

LABEL_KEY = 'label'
USERNAME_KEY = 'username'
EXAMPLE_ID_KEY = 'example_id'
REQUIRES_REVIEW_KEY = 'review_required'

# Round-robin algorithm
def round_robin_algorithm(examples: List[Example],
                          annotators: List[Annotator], 
                          max_annotators_per_example: int):
  num_annotators = len(annotators)
  num_examples = len(examples)
  example_annotator_map = {}

  for i in range(num_examples):
    example = examples[i]
    for j in range(max_annotators_per_example):
      annotator = annotators[(i * max_annotators_per_example + j) % num_annotators]
      example_annotator_map[example] = annotator
  return example_annotator_map

def weighted_round_robin_algorithm(examples: List[Example],
                                  annotators: List[Annotator]):
  num_annotators = len(annotators)
  num_examples = len(examples)
  example_annotator_map = {}

  # Calculate annotator workload (for example, number of current tasks)
  annotator_workload = {annotator: len(annotator.assigned_examples) for annotator in annotators}
  # Sort annotators by workload (ascending, fewer tasks first)
  sorted_annotators = sorted(annotators, key=lambda x: annotator_workload[x])
  # Initialize index for annotator assignment
  annotator_index = 0

  for i in range(num_examples):
    example = examples[i]
    # Get the annotator with the least workload
    annotator = sorted_annotators[annotator_index]
    # Assign annotator to example
    example_annotator_map[example] = annotator
    # Update annotator's workload
    annotator_workload[annotator] += 1
    # Move to the next annotator in a round-robin manner
    annotator_index = (annotator_index + 1) % num_annotators

  return example_annotator_map

# Compute Agreements
def compute_agreements(annotations):
  """
  Compute agreements for tasks annotations from different annotators.
  
  :param annotations: Dictionary mapping Example IDs to lists of annotations.
  :return: Agreement scores for each task.
  """
  agreements = {}
  for example_id, annotation_list in annotations.items():
      agreements[example_id] = calculate_majority_agreement(annotation_list)
  return agreements

def calculate_majority_agreement(annotation_list: list):
  """
  Calculate agreement for a given list of annotations using majority agreement.
  Identifies ties if two or more annotations have the same highest frequency.
  
  :param annotation_list: List of annotations for a specific task.
  :return: Tuple containing agreement score and a list of annotations with the highest frequency.
  """
  if not annotation_list:
      return [], []
  annotation_counts = Counter(annotation_list)
  max_count = max(annotation_counts.values())
  most_common_annotations = [annotation for annotation, count in annotation_counts.items() if count == max_count]

  # agreement score = ratio of the most common count to the total annotations
  agreement_scores = list(round(value / len(annotation_list), 2) 
                    for value in annotation_counts.values())

  return agreement_scores, most_common_annotations

def concat_annotations(df):
  # Concatenate annotator usernames and annotations
  usernames = ', '.join(df[USERNAME_KEY].unique())
  annotations = ', '.join(df[LABEL_KEY])
  
  agreement_scores, most_common_labels = calculate_majority_agreement(
                                          list(df[LABEL_KEY]))
  final_label = (most_common_labels[0] 
                 if len(most_common_labels)==1 
                 else REQUIRES_REVIEW_KEY)
  
  return pd.Series({
      'annotators': usernames,
      'annotations': annotations,
      'agreement_scores': agreement_scores,
      'final_label': final_label
  })

def aggregate_results(result_df):
  concatenated_df = (result_df
                    .groupby(EXAMPLE_ID_KEY)
                    .apply(concat_annotations)
                    .reset_index()
  )
  return concatenated_df

def assign_review_tasks():
  pass