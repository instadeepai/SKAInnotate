import axios from 'axios';

const BASE_API_URL = process.env.REACT_APP_API_URL || '';

export const init = async () => {
  try {
    const response = await axios.get(`${BASE_API_URL}/`);
    return response.data;
  } catch (error) {
    console.error('Error in init:', error);
    throw error;
  }
};

// Project APIs
export const setProject = async (setProjectData) => {
  try {
    const response = await axios.post(`${BASE_API_URL}/setup-project`, setProjectData);
    return response.data;
  } catch (error) {
    console.error('Error in setProject:', error);
    throw error;
  }
};

export const createSQLInstance = async (sqlInstanceData) => {
  try {
    const response = await axios.post(`${BASE_API_URL}/setup-gcp-sql`, sqlInstanceData);
    return response.data;
  } catch (error) {
    console.error('Error in createSQLInstance:', error);
    throw error;
  }
};

// export const createProject = async (projectData) => {
//   try {
//     const response = await axios.post(`${BASE_API_URL}/projects/`, projectData);
//     return response.data;
//   } catch (error) {
//     console.error('Error in createProject:', error);
//     throw error;
//   }
// }

export const deployApp = async (configData) => {
  try {
    const response = await axios.post(`${BASE_API_URL}/deploy`, configData);
    return response.data;
  } catch (error) {
    console.error('Error in deployApp:', error);
    throw error;
  }
};
