import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse
from core.backend.app.database import init_db

router = APIRouter()

@router.on_event("startup")
def on_startup():
  init_db()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
  return FileResponse("core/frontend/build/index.html")

@router.get("/{full_path:path}")
async def serve_frontend(full_path: str):
  return FileResponse("core/frontend/build/index.html")