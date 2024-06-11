import functools

def run_within_session(func):
  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    Session = args[0].session # Retrieve instance session
    with Session() as session:
      session.begin()
      try:
        result = func(*args, **kwargs)
        session.commit()
        return result
      except:
        session.rollback()
        raise
  return wrapper