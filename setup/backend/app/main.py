import os
from setup.backend.app.routers import local_deployments
import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from setup.backend.app.routers import cloud, index
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.mount("/static", StaticFiles(directory="setup/frontend/build/static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=os.urandom(24))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(index.router, tags=["index"])
app.include_router(cloud.router, tags=["cloud"])
app.include_router(local_deployments.router, tags=["local_deployments"])
if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=8000)
