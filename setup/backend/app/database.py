from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator
from datetime import datetime

# Create the base class for declarative models
Base = declarative_base()

# Define the Deployment model
class Deployment(Base):
  __tablename__ = 'deployments'

  id = Column(Integer, primary_key=True, autoincrement=True)
  project_id = Column(String, nullable=False)
  instance_name = Column(String, nullable=False)
  deployment_status = Column(String, nullable=False)
  service_name = Column(String)
  service_url = Column(String)
  deployed_at = Column(DateTime, default=datetime.utcnow)

  def __repr__(self):
    return (f"<Deployment(project_id='{self.project_id}', " +
    "instance_name='{self.instance_name}', " +
    "status='{self.deployment_status}', " +
    "service_name='{self.service_name}', " +
    "url='{self.service_url}')>")

engine = create_engine('sqlite:///setup/deployments.db')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
