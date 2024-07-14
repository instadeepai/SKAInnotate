# Create a service account and give necessary roles
gcloud iam service-accounts create my-service-account --display-name "My Service Account"

# Assign roles to the service account
gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member="serviceAccount:my-service-account@[PROJECT_ID].iam.gserviceaccount.com" \
  --role="roles/editor"

gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member="serviceAccount:my-service-account@[PROJECT_ID].iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountAdmin"

gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member="serviceAccount:my-service-account@[PROJECT_ID].iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member="serviceAccount:my-service-account@[PROJECT_ID].iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member="serviceAccount:my-service-account@[PROJECT_ID].iam.gserviceaccount.com" \
  --role="roles/cloudsql.admin"

gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member="serviceAccount:my-service-account@[PROJECT_ID].iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member="serviceAccount:my-service-account@[PROJECT_ID].iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"