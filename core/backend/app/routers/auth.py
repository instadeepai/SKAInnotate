import os
import logging
from fastapi import APIRouter, Depends, Request, HTTPException, status, FastAPI
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from requests_oauthlib import OAuth2Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from dotenv import load_dotenv
from jose import JWTError, jwt
from datetime import datetime, timedelta

from app.dependencies import get_current_user, create_access_token, set_user_role, get_current_role
from app.schema import UserRole
from app.crud import get_user_by_email_and_role
from app.database import get_db

# Load environment variables from .env file
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
templates = Jinja2Templates(directory="/app/frontend/public")
router.mount("/static", StaticFiles(directory="/app/frontend/public"), name="static")

# OAuth 2.0 configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/oauth2callback")
AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Allow OAuth2 transport in an insecure environment
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

# Initialize OAuth2 session
oauth = OAuth2Session(GOOGLE_CLIENT_ID, redirect_uri=REDIRECT_URI, scope=["openid", "email", "profile"])

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
  """Redirect root path to the login page."""
  logger.info("Redirecting to the login page.")
  return RedirectResponse(url='/login')

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
  """Render the login page."""
  logger.info("Rendering the login page.")
  return templates.TemplateResponse("login.html", {"request": request})

@router.get("/authorize")
async def authorize(request: Request):
  """Start the OAuth 2.0 authorization flow."""
  authorization_url, state = oauth.authorization_url(AUTHORIZATION_URL, access_type="offline", prompt="select_account")
  logger.info(f"Generated authorization URL: {authorization_url}")

  # Set the state parameter in a cookie
  response = RedirectResponse(authorization_url)
  response.set_cookie("state", state, httponly=True, secure=True)
  logger.info("Redirecting to the authorization URL.")
  return response

@router.get("/oauth2callback")
async def oauth2callback(request: Request):
  """Handle the OAuth 2.0 callback and fetch user information."""
  state = request.cookies.get("state")
  if not state:
      logger.warning("Invalid state parameter.")
      raise HTTPException(status_code=400, detail="Invalid state parameter.")

  try:
      token = oauth.fetch_token(TOKEN_URL, client_secret=GOOGLE_CLIENT_SECRET, authorization_response=str(request.url))
      logger.info("Token fetched successfully.")
  except Exception as e:
      logger.error(f"Error fetching token: {e}")
      raise HTTPException(status_code=400, detail=f"Error fetching token: {e}")

  try:
      idinfo = id_token.verify_oauth2_token(token["id_token"], google_requests.Request(), GOOGLE_CLIENT_ID)
      logger.info("ID token verified successfully.")
  except Exception as e:
      logger.error(f"Error verifying ID token: {e}")
      raise HTTPException(status_code=500, detail=f"Error verifying ID token: {e}")

  # Get user's Google Account info
  user_info = {
      'userid': idinfo['sub'],
      'email': idinfo.get('email'),
      'name': idinfo.get('name'),
      'picture': idinfo.get('picture')
  }
  
  access_token = create_access_token(data={"user_info": user_info})
  response = RedirectResponse(request.url_for('select_user_role'))
  response.set_cookie("access_token", access_token, httponly=True, secure=True)

  logger.info(f"User info fetched: {user_info}")
  logger.info("Redirecting to the select user role page.")
  return response

@router.get("/role", response_class=HTMLResponse)
async def select_user_role(request: Request, user_info: dict = Depends(get_current_user)):
  """Render the page for selecting a user role."""
  logger.info("Rendering the role selection page.")
  return templates.TemplateResponse("roles.html", {"request": request, "user_info": user_info})

@router.post("/verify/{role}", response_class=JSONResponse)
async def verify_role(request: Request, role: UserRole, db: Session = Depends(get_db), user_info: dict = Depends(get_current_user)):
  """Verify the user role and respond with success or failure."""
  selected_role = role.name
  user_email = user_info.get("email")

  user = get_user_by_email_and_role(db, user_email, selected_role)
  if not user:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not assigned to user")

  response = JSONResponse(content={"message": "Role verification successful", "user_info": user_info})
  response.set_cookie("current_role", selected_role, httponly=True, secure=True)
  access_token = create_access_token(data={"user_info": user_info, "current_role": selected_role})
  response.set_cookie("access_token", access_token, httponly=True, secure=True)

  logger.info(f"Role '{selected_role}' verified for user '{user_email}'.")
  return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
  if exc.status_code == status.HTTP_401_UNAUTHORIZED:
      return RedirectResponse(url='/login')
  return JSONResponse(
      status_code=exc.status_code,
      content={"detail": exc.detail},
  )

# Add the router to the app
app.include_router(router)
