from fastapi import APIRouter

router = APIRouter()

@router.get("/reviews/")
async def read_reviews():
    return {"reviews": "Here are your reviews"}
