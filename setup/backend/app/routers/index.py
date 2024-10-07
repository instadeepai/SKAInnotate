from fastapi import APIRouter
from starlette.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi import Request

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
  return FileResponse("setup/frontend/build/index.html")