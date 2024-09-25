from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse
from core.backend.app.database import init_db

router = APIRouter()
# templates = Jinja2Templates(directory="core/frontend/build")

@router.on_event("startup")
def on_startup():
  init_db()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
  return #FileResponse("core/frontend/build/index.html")