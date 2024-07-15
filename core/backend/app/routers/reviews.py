from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import app.crud as crud
import app.schema as schemas
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Review)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
  return crud.create_review(db=db, review=review)

@router.get("/{review_id}", response_model=schemas.Review)
def read_review(review_id: int, db: Session = Depends(get_db)):
  db_review = crud.get_review(db=db, review_id=review_id)
  if db_review is None:
    raise HTTPException(status_code=404, detail="Review not found")
  return db_review

@router.get("/", response_model=List[schemas.Review])
def read_reviews(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
  reviews = crud.get_reviews(db=db, skip=skip, limit=limit)
  return reviews

@router.put("/{review_id}", response_model=schemas.Review)
def update_review(review_id: int, review: schemas.ReviewUpdate, db: Session = Depends(get_db)):
  db_review = crud.update_review(db=db, review_id=review_id, review_update=review)
  if db_review is None:
    raise HTTPException(status_code=404, detail="Review not found")
  return db_review

@router.delete("/{review_id}", response_model=schemas.Review)
def delete_review(review_id: int, db: Session = Depends(get_db)):
  db_review = crud.delete_review(db=db, review_id=review_id)
  if db_review is None:
    raise HTTPException(status_code=404, detail="Review not found")
  return db_review