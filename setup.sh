#!/bin/bash

# Checking for all required dependencies
command -v git >/dev/null 2>&1 || { echo "Git is required. Please install Git."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js is required. Please install Node.js."; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "npm is required. Please install npm."; exit 1; }
command -v uvicorn >/dev/null 2>&1 || { echo "Installing Uvicorn..."; pip install uvicorn; }

echo "Cloning the repository..."
git clone https://github.com/instadeepai/SKAInnotate.git

echo "Navigating to the frontend directory..."
cd SKAInnotate/setup/frontend || { echo "Failed to navigate to frontend directory"; exit 1; }

echo "Installing and building npm packages and files..."
npm install
npm run build

cd ../..

# Start the FastAPI server
PORT=${1:-8800}
echo "Starting the FastAPI server on port $PORT..."
uvicorn setup.backend.app.main:app --reload --port "$PORT" &

sleep 2

OS=${2:-linux}

if [[ "$OS" == "macos" ]]; then
    open "http://localhost:$PORT"
else
    xdg-open "http://localhost:$PORT"
fi

echo "Setup complete! Access the application at http://localhost:$PORT"
