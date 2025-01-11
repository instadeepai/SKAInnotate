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

CONTAINER_NAME="skainnotate_container"
IMAGE_NAME="skainnotate-image:latest"

#Stop and remove existing image
if [ "$(docker ps -a -q -f name=^/${CONTAINER_NAME}$)" ]; then
    echo "Stopping and removing existing container: ${CONTAINER_NAME}"
    docker stop "${CONTAINER_NAME}"
    docker rm "${CONTAINER_NAME}"
else
    echo ""
fi

# 3. Build the Docker image
echo "Building the Docker image..."
docker build -f Dockerfile.setup -t "${IMAGE_NAME}" .

# 4. Run the container in detached mode, mapping host:container ports
echo "Running the Docker container..."
docker run -d -p $PORT:8800 --name "${CONTAINER_NAME}" "${IMAGE_NAME}"

echo "----------------------------------------------------------"
echo "Container started on port $PORT."
echo "Use 'docker logs skainnotate_container' to view logs."
echo "Use 'docker exec -it skainnotate_container /bin/bash' to open a shell."
echo "When finished, run 'docker stop skainnotate_container' to stop the container."
echo "----------------------------------------------------------"
echo "Access the application at http://localhost:$PORT"
echo ""