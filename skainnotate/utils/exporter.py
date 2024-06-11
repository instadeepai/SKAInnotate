import json
import pandas as pd
from typing import List
from data.database import Annotation, Example

def export_annotations_to_csv(annotations: List[Annotation], filename: str):
    """
    Export annotations to a CSV file.
    
    :param annotations: List of Annotation objects.
    :param filename: Name of the CSV file to export to.
    """
    # Prepare data for export
    data = {
        'example_id': [annotation.example_id for annotation in annotations],
        'annotator_id': [annotation.annotator_id for annotation in annotations],
        'label': [annotation.label for annotation in annotations]
        # Add more fields as needed
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Export to CSV
    df.to_csv(filename, index=False)
    print(f"Annotations exported to {filename}")

def export_examples_to_json(examples: List[Example], filename: str):
    """
    Export examples to a JSON file.
    
    :param examples: List of Example objects.
    :param filename: Name of the JSON file to export to.
    """
    # Prepare data for export
    data = [{
        'example_id': example.example_id,
        'image': example.image,
        'annotation_status': example.annotation_status,
        # Add more fields as needed
    } for example in examples]
    
    # Export to JSON
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Examples exported to {filename}")