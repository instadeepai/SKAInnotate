import os
import logging
from fastapi import APIRouter, Depends, Request, HTTPException, FastAPI
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from dotenv import load_dotenv

from app.dependencies import create_access_token
from app import schema
from app import crud
from app.database import get_db

load_dotenv()

# Configure logging
logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app and router
app = FastAPI()
router = APIRouter()

# OAuth 2.0 configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

@router.post("/callback")
async def auth_callback(token: dict, db: Session = Depends(get_db)):
  """Handle the OAuth 2.0 callback and fetch user information."""
  try:
    idinfo = id_token.verify_oauth2_token(token["token"], google_requests.Request(), GOOGLE_CLIENT_ID)
    logger.info("ID token verified successfully.")
  except Exception as e:
    logger.error(f"Error verifying ID token: {e}")
    raise HTTPException(status_code=400, detail=f"Error verifying ID token: {e}")

  user = crud.get_user_by_email(db, idinfo.get('email'))
  if not user:
    return JSONResponse(status_code=404, content={"message": "User not assigned any role in this project"})
  
  user_info = {
      'user_id': user.user_id,
      'email': user.email,
      'username': user.username,
      'roles': [role.role_name for role in user.roles]
  }
  create_access_token(data={"user_info": user_info})

  return JSONResponse(content={
      "user_info": user_info
  })

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
  return JSONResponse(
      status_code=exc.status_code,
      content={"detail": exc.detail},
  )

# Add the router to the app
app.include_router(router)
