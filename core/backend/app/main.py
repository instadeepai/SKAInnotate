import os
import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from core.backend.app import utils
from core.backend.app.routers import (auth, 
                      users, 
                      tasks, 
                      annotations, 
                      reviews,
                      welcome,
                      projects
                      )
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="core/frontend/build/static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=os.urandom(24))

app.include_router(welcome.router)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(annotations.router, prefix="/api/annotations", tags=["annotations"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])

if __name__ == "__main__":
  uvicorn.run(app, os.environ.get("HOST", "0.0.0.0"), port=int(os.environ.get("PORT", 8000)))