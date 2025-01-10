from fastapi import APIRouter, Depends, HTTPException
from deployment_setup.backend.app import schema, database
from deployment_setup.backend.app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/deployments", response_model=schema.DeploymentResponse)
def add_deployment(deployment: schema.DeploymentCreate, db: Session = Depends(get_db)):
  new_deployment = database.Deployment(
    project_id=deployment.project_id,
    instance_name=deployment.instance_name,
    deployment_status=deployment.deployment_status,
    service_name=deployment.service_name,
    service_url=deployment.service_url
  )
  db.add(new_deployment)
  db.commit()
  db.refresh(new_deployment)
  return new_deployment

@router.get("/deployments", response_model=list[schema.DeploymentResponse])
def get_deployments(db: Session = Depends(get_db)):
  deployments = db.query(database.Deployment).all()
  return deployments

@router.delete("/deployments/{deployment_id}")
def delete_deployment(deployment_id: int, db: Session = Depends(get_db)):
  deployment = db.query(database.Deployment).filter_by(id=deployment_id).first()
  if deployment is None:
    raise HTTPException(status_code=404, detail="Deployment not found")
  db.delete(deployment)
  db.commit()
  return {"message": f"Deployment {deployment_id} deleted successfully"}