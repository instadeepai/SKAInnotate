from users.annotator import AnnotatorRepository
from users.reviewer import ReviewerRepository

class Client(AnnotatorRepository, ReviewerRepository):
  def __init__(self, session) -> None:
    super().__init__(session)
    super(AnnotatorRepository, self).__init__(session)