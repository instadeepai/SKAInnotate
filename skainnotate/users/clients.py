from skainnotate.users.annotator import AnnotatorRepository
from skainnotate.users.reviewer import ReviewerRepository

class Client(AnnotatorRepository, ReviewerRepository):
  def __init__(self, session) -> None:
    super().__init__(session)
    super(AnnotatorRepository, self).__init__(session)