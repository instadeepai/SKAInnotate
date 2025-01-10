import os
import typer
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from deployment_setup.backend.app.routers import cloud, index
from deployment_setup.backend.app.routers import local_deployments

app = FastAPI()
app.mount("/static", StaticFiles(directory="deployment_setup/frontend/build/static"), name="static")
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

cli = typer.Typer(help="SKAInnotate Command Line Interface")

@cli.command()
def run(port: int = 8000):
    """
    Start the SKAInnotate server.
    """
    typer.echo(f"Starting SKAInnotate server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)

@cli.command()
def checks():
    """
    Run SKAInnotate health checks.
    """
    # Implement your checks here
    typer.echo("Running SKAInnotate checks...")
    # Example: Check database connection, configurations, etc.

def run_app():
    cli()

if __name__ == "__main__":
    run_app()
