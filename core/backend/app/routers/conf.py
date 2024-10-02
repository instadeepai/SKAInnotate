import os
from fastapi import APIRouter
from starlette.responses import FileResponse

router = APIRouter()

@router.get("/api-url")
async def get_api_url():
  return {
    "apiUrl": os.getenv("BASE_API_URL")
  }