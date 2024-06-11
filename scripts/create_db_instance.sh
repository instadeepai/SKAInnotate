#/bin/bash

database_version=$(gcloud sql instances describe "$instance_name" --format="value(databaseVersion)")

if [[ $database_version == POSTGRES* ]]; then
  echo "Found existing Postgres Cloud SQL Instance!"
else
  echo "Creating new Cloud SQL instance..."
  gcloud sql instances create "$instance_name" \
    --database-version=POSTGRES_15 \
    --region="$region" \
    --cpu=1 \
    --memory=4GB \
    --root-password="$root_password" \
    --database-flags=cloudsql.iam_authentication=On
fi