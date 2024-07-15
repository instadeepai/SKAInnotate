#!/usr/bin/env bash

# Checking if all arguments are provided
if [ "$#" -ne 5 ]; then
  echo "Usage: $0 <service_name> <image> <region> <sql_instance_connection_name> <env_vars_file>"
  exit 1
fi

# Set variables from arguments
SERVICE_NAME=$1
IMAGE=$2
REGION=$3
SQL_INSTANCE_CONNECTION_NAME=$4
ENV_VARS_FILE=$5

# Example usage: 
# """
# ./deploy.sh \
#     my-service \
#     {REGION}-docker.pkg.dev/{PROJECT_ID}/{REPO_NAME}/{IMAGE_NAME}:{TAG} \
#     {REGION} \
#     {PROJECT_ID}:{REGION}:{INSTANCE_NAME} \
#     {SERVICE_ACCOUNT_PATH} \
#     {ENV_VAR_FILE}
# """

# Deploy the image to Cloud Run
gcloud run deploy ${SERVICE_NAME} \
  --image=${IMAGE} \
  --platform=managed \
  --region=${REGION} \
  --allow-unauthenticated \
  --add-cloudsql-instances=${SQL_INSTANCE_CONNECTION_NAME} \
  --env-vars-file=${ENV_VARS_FILE}