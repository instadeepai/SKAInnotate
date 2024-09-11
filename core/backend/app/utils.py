from collections import Counter
from typing import List, Optional, Any

def get_final_annotation(annotations: List[str], review: Optional[str]) -> Any:
  if review is not None:
    return review

  if annotations:
    annotation_counts = Counter(annotations)
    max_count = max(annotation_counts.values())
    majority_annotations = [annotation for annotation, count in annotation_counts.items() if count == max_count]

    if len(majority_annotations) > 1:
      return None
    return majority_annotations[0]
  
  return None