import React, { useEffect, useState, useReducer } from 'react';
import { Button, Icon } from 'semantic-ui-react';
import { createProject, updateProject, deleteProject, fetchProjects, UploadTaskFromCSV } from '../services/api';
import ProjectGrid from '../components/ProjectGrid';
import CreateProjectModal from '../components/CreateProjectModal';
import RoleSelectionModal from '../components/RoleSelectionModal';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../UserContext'; // Import the useUser hook
import 'semantic-ui-css/semantic.min.css';
import '../assets/styles/ProjectsPage.css';

function modalReducer(state, action) {
  switch (action.type) {
    case 'OPEN_MODAL':
      return { ...state, open: true };
    case 'CLOSE_MODAL':
      return { ...state, open: false };
    default:
      throw new Error('Unhandled action');
  }
}

const ProjectsPage = () => {
  const { user, role } = useUser();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [newProject, setNewProject] = useState({
    project_title: '',
    project_description: '',
    max_annotators_per_task: '',
    completion_deadline: '',
    labels: '',
  });
  const [csvFile, setCsvFile] = useState(null);
  const navigate = useNavigate();
  const [modalState, dispatchModal] = useReducer(modalReducer, { open: false });

  useEffect(() => {
    fetchAndSetProjects();
    }, []);

  const fetchAndSetProjects = async () => {
    setLoading(true);
    try {
      const response = await fetchProjects();
      setProjects(response.data);
      sessionStorage.setItem('projects', JSON.stringify(response.data));
    } catch (error) {
      setError('Failed to fetch projects');
    } finally {
      setLoading(false);
    }
  };

  const handleProjectClick = (projectId) => {
    if (role === 'select role' || !role) {
      dispatchModal({ type: 'OPEN_MODAL' });
    } else {
      navigate(`/projects/${projectId}/tasks`);
    }    
  };

  const handleChange = (e, { name, value }) => setNewProject({ ...newProject, [name]: value });
  const handleTaskFileChange = (e) => setCsvFile(e.target.files[0]);

  const handleSubmit = async () => {
  const project_data = {
    project_title: newProject.project_title,
    project_description: newProject.project_description,
    max_annotators_per_task: parseInt(newProject.max_annotators_per_task),
    completion_deadline: new Date(newProject.completion_deadline).toISOString(),
    labels: newProject.labels,
  };

  let projectResponse;

  try {
    if (newProject.project_id) {
      projectResponse = await updateProject(newProject.project_id, project_data);
    } else {
      projectResponse = await createProject(project_data);
    }

    if (csvFile) {
      const formData = new FormData();
      formData.append('file', csvFile);
      await UploadTaskFromCSV(projectResponse.data.project_id, formData);
    }

    fetchAndSetProjects(); // Refetch projects after creating or updating one
  } catch (error) {
    setError(newProject.project_id ? 'Failed to update project' : 'Failed to create project');
  } finally {
    setModalOpen(false); // Ensure modal is closed after the operation
  }
};


  const handleDelete = async (projectId) => {
    try {
      await deleteProject(projectId);
      fetchAndSetProjects(); // Refetch projects after deleting one
    } catch (error) {
      setError('Failed to delete project');
    }
  };

  const handleEditClick = (project) => {
    setNewProject({
      project_id: project.project_id,
      project_title: project.project_title,
      project_description: project.project_description,
      max_annotators_per_task: project.max_annotators_per_task.toString(), // Convert number to string for the form input
      completion_deadline: new Date(project.completion_deadline).toISOString().split('T')[0], // Format date for input
      labels: project.labels,
    });
    setModalOpen(true); // Open the modal for editing
  };

    const handleCreateProject = () => {
    setNewProject({
      project_title: '',
      project_description: '',
      max_annotators_per_task: '',
      completion_deadline: '',
      labels: '',
    });
    setModalOpen(true); // Open the modal for editing
  };

  return (
    <div className="projects-page">
      <div className='projects-page-header'>
        <h1><Icon name='clipboard list' /> Projects</h1>
        {role === 'admin' && (
          <Button
          primary
          icon="add"
          onClick={handleCreateProject}
          content="Create New Project"
          />
        )}
      </div>
      <ProjectGrid
        projects={projects}
        onProjectClick={handleProjectClick}
        onEditClick={handleEditClick}
        onDelete={handleDelete}
      />
      <CreateProjectModal
        newProject={newProject}
        onChange={handleChange}
        onSubmit={handleSubmit}
        onTaskFileChange={handleTaskFileChange}
        modalOpen={modalOpen}
        setModalOpen={setModalOpen}
      />
      <RoleSelectionModal
        dispatchModal={dispatchModal}
        modalState={modalState}
      />
    </div>
  );
};

export default ProjectsPage;