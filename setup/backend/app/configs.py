
import os
configs = {
  'CONTAINER_IMAGE_BACKEND':'us-central1-docker.pkg.dev/skai-project-388314/skai-repo/skainnotate-backend:latest',
  'CONTAINER_IMAGE_FRONTEND':'us-central1-docker.pkg.dev/skai-project-388314/skai-repo/skainnotate-frontend:latest'
}
def get_configs():
  return configs