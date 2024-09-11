import axios from 'axios'

// const BASE_API_URL = 'http://127.0.0.1:8000';
const BASE_API_URL = process.env.REACT_APP_BASE_API_URL;

export const init = () => {
  return axios.get(`${BASE_API_URL}/`);
}
// Project APIs
export const fetchProjects = () => {
  return axios.get(`${BASE_API_URL}/projects/`);
};
export const fetchProject = (projectId) => {
  return axios.get(`${BASE_API_URL}/projects/${projectId}`);
};
export const createProject = async (projectData) => {
  return axios.post(`${BASE_API_URL}/projects/`, projectData)
}
export const updateProject = async (projectId, projectData) => {
  return axios.put(`${BASE_API_URL}/projects/${projectId}`, projectData)
}
export const deleteProject = async(projectId) => {
  return axios.delete(`${BASE_API_URL}/projects/${projectId}`)
}

// Tasks APIs
export const fetchTasks = async(projectId, userId, currentRole) => {
  return axios.get(`${BASE_API_URL}/tasks/fetchall/imgUrl-and-labelStatus?project_id=${projectId}&user_id=${userId}&role=${currentRole}`)
}

export const fetchTask = async(projectId, userId, currentRole, taskId) => {
  return axios.get(`${BASE_API_URL}/tasks/fetch/imgUrl-and-labelStatus?project_id=${projectId}&user_id=${userId}&role=${currentRole}&task_id=${taskId}`)
}

export const assignTasks = async(projectId) => {
  return axios.get(`${BASE_API_URL}/tasks/assign-tasks/auto?project_id=${projectId}`)
}

export const deleteTask = async(taskId) => {
  return
  // return axios.delete(`${BASE_API_URL}/tasks/${taskId}`);
};

export const UploadTaskFromCSV = async (projectId, formData) => {
  return axios.post(`${BASE_API_URL}/projects/${projectId}/upload-tasks-from-csv`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
    });
};

// Users APIs
export const fetchUsers = async() => {
  return axios.get(`${BASE_API_URL}/users/`);
};

export const fetchUser = async(userId) => {
  return axios.get(`${BASE_API_URL}/users/${userId}`);
};

export const createUser = async(newUser) => {
  return axios.post(`${BASE_API_URL}/users/`, newUser)
}

export const deleteUser = async(userId) => {
  return axios.delete(`${BASE_API_URL}/users/${userId}`);
};
export const fetchAssignedUsers = async(taskId) => {
  return axios.get(`${BASE_API_URL}/tasks/${taskId}/assigned_users`);
};
// axios.get(`/api/tasks/${task.task_id}/users`)
// Role capabilities
export const fetchReviewers = async() => {
  return axios.get(`${BASE_API_URL}/users/role/reviewer`);
};
export const fetchReviewersbyTask = async(taskId) => {
  return axios.get(`${BASE_API_URL}/tasks/${taskId}/reviewer`);
};

export const assignTaskToReviewer = async(taskId, taskAssignData) => {
  return axios.post(`${BASE_API_URL}/tasks/${taskId}/assign`, taskAssignData);
}
export const unAssignTaskToReviewer = async(taskId, taskUnAssignData) => {
  return axios.post(`${BASE_API_URL}/tasks/${taskId}/unassign`, taskUnAssignData);
}
export const assignRole = async(userRole) => {
  return axios.post(`${BASE_API_URL}/users/assign-role`, userRole)
};

export const unAssignRole = async(unAssignData) => {
  return axios.post(`${BASE_API_URL}/users/unassign-role`, unAssignData)
};

// Project Stats
export const fetchProjectStatistics = async(projectId) => {
  return axios.get(`${BASE_API_URL}/projects/${projectId}/statistics`)
}

// Annotations APIs
export const fetchAnnotationByUserAndTaskID = async(userId, taskId) => {
  return axios.get(`${BASE_API_URL}/tasks/${taskId}/user/${userId}/annotations`);
};

export const fetchReviewByUserAndTaskID = async(userId, taskId) => {
  return await axios.get(`${BASE_API_URL}/tasks/${taskId}/user/${userId}/reviews`);
};
export const createAnnotation = async(annotationData) => {
  return axios.post(`${BASE_API_URL}/annotations/`, annotationData)
};

export const updateAnnotation = async(annotationId, updatedAnnotation) => {
  return axios.put(`${BASE_API_URL}/annotations/${annotationId}`, updatedAnnotation)
};

export const createReview = async(reviewData) => {
  return axios.post(`${BASE_API_URL}/reviews/`, reviewData)
};

export const updateReview = async(reviewId, updatedReview) => {
  return axios.put(`${BASE_API_URL}/reviews/${reviewId}`, updatedReview)
};

export const verify_token_callback = (token) => {
  return axios.post(`${BASE_API_URL}/auth/callback`, token)
}

export const exportAnnotations = (projectId, format) => {
  return axios.get(`${BASE_API_URL}/projects/${projectId}/export-annotations?format=${format}`, {
      responseType: 'blob'}
  )};
