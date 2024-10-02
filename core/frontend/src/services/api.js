import axios from 'axios';

const BASE_API_URL = process.env.REACT_APP_BASE_API_URL || '';

const getRequest = (url, params = {}) => axios.get(`${BASE_API_URL}${url}`, { params });
const postRequest = (url, data, headers = {}) => axios.post(`${BASE_API_URL}${url}`, data, { headers });
const putRequest = (url, data) => axios.put(`${BASE_API_URL}${url}`, data);
const deleteRequest = (url) => axios.delete(`${BASE_API_URL}${url}`);

// Initialization
export const init = () => getRequest(`/`);

// Project APIs
export const fetchProjects = () => getRequest(`/api/projects/`);
export const fetchProject = (projectId) => getRequest(`/api/projects/${projectId}`);
export const createProject = (projectData) => postRequest(`/api/projects/`, projectData);
export const updateProject = (projectId, projectData) => putRequest(`/api/projects/${projectId}`, projectData);
export const deleteProject = (projectId) => deleteRequest(`/api/projects/${projectId}`);

// Tasks APIs
export const fetchTasks = (projectId, userId, currentRole) => 
  getRequest(`/api/tasks/fetchall/imgUrl-and-labelStatus`, { project_id: projectId, user_id: userId, role: currentRole });

export const fetchTask = (projectId, userId, currentRole, taskId) => 
  getRequest(`/api/tasks/fetch/imgUrl-and-labelStatus`, { project_id: projectId, user_id: userId, role: currentRole, task_id: taskId });

export const assignTasks = (projectId) => getRequest(`/api/tasks/assign-tasks/auto`, { project_id: projectId });
export const deleteTask = (taskId) => deleteRequest(`/api/tasks/${taskId}`);

export const uploadTaskFromCSV = (projectId, formData) => 
  postRequest(`/api/projects/${projectId}/upload-tasks-from-csv`, formData, { 'Content-Type': 'multipart/form-data' });

// Users APIs
export const fetchUsers = () => getRequest(`/api/users/`);
export const fetchUser = (userId) => getRequest(`/api/users/${userId}`);
export const createUser = (newUser) => postRequest(`/api/users/`, newUser);
export const deleteUser = (userId) => deleteRequest(`/api/users/${userId}`);
export const fetchAssignedUsers = (taskId) => getRequest(`/api/tasks/${taskId}/assigned_users`);

// Role capabilities
export const fetchReviewers = () => getRequest(`/api/users/role/reviewer`);
export const fetchReviewersByTask = (taskId) => getRequest(`/api/tasks/${taskId}/reviewer`);

export const assignTaskToReviewer = (taskId, taskAssignData) => postRequest(`/api/tasks/${taskId}/assign`, taskAssignData);
export const unAssignTaskToReviewer = (taskId, taskUnAssignData) => postRequest(`/api/tasks/${taskId}/unassign`, taskUnAssignData);
export const assignRole = (userRole) => postRequest(`/api/users/assign-role`, userRole);
export const unAssignRole = (unAssignData) => postRequest(`/api/users/unassign-role`, unAssignData);

// Project Stats
export const fetchProjectStatistics = (projectId) => getRequest(`/api/projects/${projectId}/statistics`);

// Annotations APIs
export const fetchAnnotationByUserAndTaskID = (userId, taskId) => getRequest(`/api/tasks/${taskId}/user/${userId}/annotations`);
export const fetchReviewByUserAndTaskID = (userId, taskId) => getRequest(`/api/tasks/${taskId}/user/${userId}/reviews`);

export const createAnnotation = (annotationData) => postRequest(`/api/annotations/`, annotationData);
export const updateAnnotation = (annotationId, updatedAnnotation) => putRequest(`/api/annotations/${annotationId}`, updatedAnnotation);

export const createReview = (reviewData) => postRequest(`/api/reviews/`, reviewData);
export const updateReview = (reviewId, updatedReview) => putRequest(`/api/reviews/${reviewId}`, updatedReview);

// Authentication
export const verifyTokenCallback = (token) => postRequest(`/api/auth/callback`, token);
export const fetchClientId = () => getRequest(`/api/auth/client-id`);
export const fetchBaseUrl = () => getRequest(`/api/api-url`);

// Annotations Export
export const exportAnnotations = (projectId, format) => 
  axios.get(`${BASE_API_URL}/api/projects/${projectId}/export-annotations`, {
    params: { format },
    responseType: 'blob'
  });