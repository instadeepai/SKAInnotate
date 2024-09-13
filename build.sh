#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# Check for the required argument
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <full-docker-image-path>"
  exit 1
fi

# Variables
FULL_IMAGE_NAME=$1

function check_command() {
  command -v "$1" >/dev/null 2>&1 || { echo >&2 "Error: $1 is not installed."; exit 1; }
}

check_command "docker"

# Build and push Docker image
docker build --platform linux/amd64 --no-cache --progress=plain -t "${FULL_IMAGE_NAME}" .
docker push "${FULL_IMAGE_NAME}"
echo "Docker image ${FULL_IMAGE_NAME} built and pushed successfully."