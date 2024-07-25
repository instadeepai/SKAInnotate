import os
import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from jose import JWTError, jwt
from app.routers import (auth, 
                      users, 
                      tasks, 
                      annotations, 
                      reviews,
                      welcome,
                      projects,
                      views
                      )

app = FastAPI()
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.add_middleware(SessionMiddleware, secret_key=os.urandom(24))

app.include_router(views.router)
app.include_router(welcome.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(tasks.router, tags=["tasks"])
app.include_router(annotations.router, tags=["annotations"])
app.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])

if __name__ == "__main__":
  uvicorn.run(app, os.environ.get("HOST", "0.0.0.0"), port=int(os.environ.get("PORT", 8000)))