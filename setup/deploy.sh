#!/usr/bin/env bash

# Checking if all arguments are provided
if [ "$#" -ne 6 ]; then
  echo "Usage: $0 <service_name> <image> <region> <sql_instance_connection_name> <env_vars>"
  exit 1
fi

# Set variables from arguments
SERVICE_NAME=$1
PROJECT_ID=$2
IMAGE=$3
REGION=$4
SQL_INSTANCE_CONNECTION_NAME=$5
ENV_VARS=$6

# Example usage: 
# """
# ./deploy.sh \
#     my-service \
#     {REGION}-docker.pkg.dev/{PROJECT_ID}/{REPO_NAME}/{IMAGE_NAME}:{TAG} \
#     {REGION} \
#     {PROJECT_ID}:{REGION}:{INSTANCE_NAME} \
#     {ENV_VARS}
# """

# Deploy the image to Cloud Run
gcloud run deploy ${SERVICE_NAME} \
  --image=${IMAGE} \
  --project=${PROJECT_ID} \
  --platform=managed \
  --region=${REGION} \
  --allow-unauthenticated \
  --add-cloudsql-instances=${SQL_INSTANCE_CONNECTION_NAME} \
  --set-env-vars=${ENV_VARS}