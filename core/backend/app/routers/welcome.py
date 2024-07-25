from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.database import init_db

router = APIRouter()

@router.on_event("startup")
def on_startup():
  init_db()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
  return RedirectResponse(url='/login')