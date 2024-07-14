#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# Variables
IMAGE_NAME="skainnotate-image"
TAG="latest"
GCP_PROJECT_ID="skai-project-388314"
GCP_REPO="skai-repo"
GCP_REGION="us-central1"
FULL_IMAGE_NAME="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GCP_REPO}/${IMAGE_NAME}:${TAG}"

function check_command() {
  command -v "$1" >/dev/null 2>&1 || { echo >&2 "Error: $1 is not installed."; exit 1; }
}

check_command "docker"

# Build and push Docker image
docker build --platform linux/amd64 --no-cache --progress=plain -t "${IMAGE_NAME}:${TAG}" .
docker tag "${IMAGE_NAME}:${TAG}" "${FULL_IMAGE_NAME}"
docker push "${FULL_IMAGE_NAME}"
echo "Docker image ${FULL_IMAGE_NAME} built and pushed successfully."