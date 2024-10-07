#!/bin/bash

# Checking for all required dependencies
command -v git >/dev/null 2>&1 || { echo "Git is required. Please install Git."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js is required. Please install Node.js."; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "npm is required. Please install npm."; exit 1; }
command -v pip >/dev/null 2>&1 || { echo "pip is required. Please install pip."; exit 1; }
command -v uvicorn >/dev/null 2>&1 || { echo "Installing Uvicorn..."; pip install uvicorn || { echo "Failed to install Uvicorn."; exit 1; }; }

cd setup/frontend || { echo "Failed to navigate to frontend directory"; exit 1; }

echo "Installing and building npm packages and files..."
npm install || { echo "npm install failed"; exit 1; }
npm run build || { echo "npm run build failed"; exit 1; }

cd ../..

# Start the FastAPI server
PORT=${1:-8800}
echo "Starting the FastAPI server on port $PORT..."
gunicorn setup.backend.app.main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:"$PORT" &

sleep 2

OS=${2:-linux}

if [[ "$OS" == "macos" ]]; then
    open "http://localhost:$PORT"
else
    command -v xdg-open >/dev/null 2>&1 || { echo "xdg-open is required to open the browser automatically."; exit 1; }
    xdg-open "http://localhost:$PORT"
fi

echo "Setup complete! Access the application at http://localhost:$PORT"
