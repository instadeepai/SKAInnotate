#!/usr/bin/env bash
set -e

# 1. Check if Docker is installed
if ! command -v docker &>/dev/null; then
  echo "Error: Docker is required but not installed. Please install Docker first."
  exit 1
fi

# 2. Get desired port from the first argument, default to 8800 if not provided
PORT="${1:-8800}"

echo "Using port: $PORT"

# 3. Build the Docker image
echo "Building the Docker image..."
docker build -f Dockerfile.setup -t skainnotate_app .

# 4. Run the container in detached mode, mapping host:container ports
echo "Running the Docker container..."
docker run -d -p $PORT:8800 --name skainnotate_container skainnotate_app

echo "----------------------------------------------------------"
echo "Container started on port $PORT."
echo "Use 'docker logs skainnotate_container' to view logs."
echo "Use 'docker exec -it skainnotate_container /bin/bash' to open a shell."
echo "When finished, run 'docker stop skainnotate_container' to stop the container."
echo "----------------------------------------------------------"
echo "Access the application at http://localhost:$PORT"
echo ""
