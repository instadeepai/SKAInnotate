#!/usr/bin/env bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 6 ]; then
  echo "Usage: $0 <project_id> <region> <service_name> <image_name> <repo_name> <tag>"
  exit 1
fi

# Set variables from arguments
PROJECT_ID=$1
REGION=$2
SERVICE_NAME=$3
IMAGE_NAME=$4
REPO_NAME=$5
TAG=$6

# Example usage: 
"""
./deploy.sh 
    my-gcp-project 
    us-central1 
    my-test-service 
    skainnotate-image 
    skai-repo latest

"""

# Deploy the image to Cloud Run
gcloud run deploy ${SERVICE_NAME} \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${TAG} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --port 8080 \
  --add-cloudsql-instances INSTANCE_CONNECTION_NAME

echo "Deployment completed successfully!"

