#!/usr/bin/env bash

# Set variables
PROJECT_ID="skai-project-388314"
REGION="us-central1"
SERVICE_NAME="skainnotate-service"
IMAGE_NAME="skainnotate-image"
REPO_NAME="skai-repo"
TAG="latest"

# Build the Docker image
# docker build --platform linux/amd64 --no-cache --progress=plain -t ${IMAGE_NAME}:${TAG} .

# # Tag the Docker image
# docker tag ${IMAGE_NAME}:${TAG} ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${TAG}

# # Push the Docker image to Google Artifact Registry
# docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${TAG}

# Deploy the image to Cloud Run
gcloud run deploy ${SERVICE_NAME} \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${TAG} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --port 8080 \
  --add-cloudsql-instances INSTANCE_CONNECTION_NAME

echo "Deployment completed successfully!"
