import sqlalchemy as sqla
from sqlalchemy import exc
from sqlalchemy.orm import sessionmaker, scoped_session
from google.cloud.sql.connector import Connector
from utils.logger import logger
from data.database import Base

class DatabaseManager:
  def __init__(
    self,
    username: str,
    password: str,
    db_name: str,
    instance_connection_name: str,
    **kwargs: dict
  ):
    """
    Initializes the DatabaseManager instance.

    Args:
      username (str): Username for database connection.
      password (str): Password for database connection.
      db_name (str): Name of the database.
      instance_connection_name (str): Instance connection name for the database.
      kwargs (dict): Additional keyword arguments.
    """
    self.username = username
    self.password = password
    self.db_name = db_name
    self.instance_connection_name = instance_connection_name

    self.kwargs = kwargs
    self._engine = None
    self._session = None

  def setup(self):
    """
    Sets up the database connection and initializes necessary resources.
    """
    connector = Connector()

    def getconn():
        conn = connector.connect(
          self.instance_connection_name,
          "pg8000",
          user=self.username,
          password=self.password,
          db=self.db_name
        )
        return conn

    self._engine = sqla.create_engine(
      "postgresql+pg8000://",
      creator=getconn,
    )

    Base.metadata.bind = self._engine
    try:
      Base.metadata.create_all(self._engine)
    except exc.ProgrammingError as e:
      logger.log_error(f"Error creating Database: {e}")
      raise

    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)
    self._session = scoped_session(session_factory)

    Base.query = self._session.query_property()

  def get_session(self):
    """
    Returns the current session.

    Returns:
        sqlalchemy.orm.Session: The current session object.
    """
    return self._session

  def get_engine(self):
    """
    Returns the database engine.

    Returns:
        sqlalchemy.engine.Engine: The database engine object.
    """
    return self._engine

  def rollback_session(self):
    """
    Rolls back the current session.
    """
    session = self._session()
    session.rollback()

  def close_session(self):
    """
    Closes the current session.
    """
    self._session.close()
