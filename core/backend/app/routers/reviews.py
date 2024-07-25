from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import app.crud as crud
import app.schema as schema
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=schema.Review)
def create_review(review: schema.ReviewCreate, db: Session = Depends(get_db)):
  return crud.create_review(db=db, label=review.label, task_id=review.task_id, reviewer_id=review.user_id)

@router.get("/{review_id}", response_model=schema.Review)
def read_review(review_id: int, db: Session = Depends(get_db)):
  db_review = crud.get_review(db=db, review_id=review_id)
  if db_review is None:
    raise HTTPException(status_code=404, detail="Review not found")
  return db_review

@router.get("/", response_model=List[schema.Review])
def read_reviews(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
  reviews = crud.get_reviews(db=db, skip=skip, limit=limit)
  return reviews

@router.put("/{review_id}", response_model=schema.Review)
def update_review(review_id: int, review: schema.ReviewUpdate, db: Session = Depends(get_db)):
  db_review = crud.update_review(db=db, review_id=review_id, review_update=review)
  if db_review is None:
    raise HTTPException(status_code=404, detail="Review not found")
  return db_review

@router.delete("/{review_id}", response_model=schema.Review)
def delete_review(review_id: int, db: Session = Depends(get_db)):
  db_review = crud.delete_review(db=db, review_id=review_id)
  if db_review is None:
    raise HTTPException(status_code=404, detail="Review not found")
  return db_review
