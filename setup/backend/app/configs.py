
import os
configs = {
  'CONTAINER_IMAGE_BACKEND':'us-central1-docker.pkg.dev/skai-project-388314/skai-repo/skainnotate-backend:v8',
  'CONTAINER_IMAGE_FRONTEND':'us-central1-docker.pkg.dev/skai-project-388314/skai-repo/skainnotate-frontend:v8'
}
def get_configs():
  return configs