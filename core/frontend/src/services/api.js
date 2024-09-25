import axios from 'axios';

const BASE_API_URL = process.env.REACT_APP_BASE_API_URL || '';

const getRequest = (url, params = {}) => axios.get(`${BASE_API_URL}${url}`, { params });

const postRequest = (url, data, headers = {}) => axios.post(`${BASE_API_URL}${url}`, data, { headers });

const putRequest = (url, data) => axios.put(`${BASE_API_URL}${url}`, data);

const deleteRequest = (url) => axios.delete(`${BASE_API_URL}${url}`);

// Initialization
export const init = () => getRequest(`/`);

// Project APIs
export const fetchProjects = () => getRequest(`/projects/`);
export const fetchProject = (projectId) => getRequest(`/projects/${projectId}`);
export const createProject = (projectData) => postRequest(`/projects/`, projectData);
export const updateProject = (projectId, projectData) => putRequest(`/projects/${projectId}`, projectData);
export const deleteProject = (projectId) => deleteRequest(`/projects/${projectId}`);

// Tasks APIs
export const fetchTasks = (projectId, userId, currentRole) => 
  getRequest(`/tasks/fetchall/imgUrl-and-labelStatus`, { project_id: projectId, user_id: userId, role: currentRole });

export const fetchTask = (projectId, userId, currentRole, taskId) => 
  getRequest(`/tasks/fetch/imgUrl-and-labelStatus`, { project_id: projectId, user_id: userId, role: currentRole, task_id: taskId });

export const assignTasks = (projectId) => getRequest(`/tasks/assign-tasks/auto`, { project_id: projectId });
export const deleteTask = (taskId) => deleteRequest(`/tasks/${taskId}`);

export const uploadTaskFromCSV = (projectId, formData) => 
  postRequest(`/projects/${projectId}/upload-tasks-from-csv`, formData, { 'Content-Type': 'multipart/form-data' });

// Users APIs
export const fetchUsers = () => getRequest(`/users/`);
export const fetchUser = (userId) => getRequest(`/users/${userId}`);
export const createUser = (newUser) => postRequest(`/users/`, newUser);
export const deleteUser = (userId) => deleteRequest(`/users/${userId}`);
export const fetchAssignedUsers = (taskId) => getRequest(`/tasks/${taskId}/assigned_users`);

// Role capabilities
export const fetchReviewers = () => getRequest(`/users/role/reviewer`);
export const fetchReviewersByTask = (taskId) => getRequest(`/tasks/${taskId}/reviewer`);

export const assignTaskToReviewer = (taskId, taskAssignData) => postRequest(`/tasks/${taskId}/assign`, taskAssignData);
export const unAssignTaskToReviewer = (taskId, taskUnAssignData) => postRequest(`/tasks/${taskId}/unassign`, taskUnAssignData);
export const assignRole = (userRole) => postRequest(`/users/assign-role`, userRole);
export const unAssignRole = (unAssignData) => postRequest(`/users/unassign-role`, unAssignData);

// Project Stats
export const fetchProjectStatistics = (projectId) => getRequest(`/projects/${projectId}/statistics`);

// Annotations APIs
export const fetchAnnotationByUserAndTaskID = (userId, taskId) => getRequest(`/tasks/${taskId}/user/${userId}/annotations`);
export const fetchReviewByUserAndTaskID = (userId, taskId) => getRequest(`/tasks/${taskId}/user/${userId}/reviews`);

export const createAnnotation = (annotationData) => postRequest(`/annotations/`, annotationData);
export const updateAnnotation = (annotationId, updatedAnnotation) => putRequest(`/annotations/${annotationId}`, updatedAnnotation);

export const createReview = (reviewData) => postRequest(`/reviews/`, reviewData);
export const updateReview = (reviewId, updatedReview) => putRequest(`/reviews/${reviewId}`, updatedReview);

// Authentication
export const verifyTokenCallback = (token) => postRequest(`/auth/callback`, token);

// Annotations Export
export const exportAnnotations = (projectId, format) => 
  axios.get(`${BASE_API_URL}/projects/${projectId}/export-annotations`, {
    params: { format },
    responseType: 'blob'
  });