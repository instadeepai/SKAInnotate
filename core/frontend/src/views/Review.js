import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import { Loader, Message, Icon } from 'semantic-ui-react';
import { useUser } from '../UserContext';
import TaskImage from './TaskViews/TaskImage';
import TaskList from './TaskViews/TaskList';
import LabelSelector from './TaskViews/LabelSelector';
import NavigationButtons from './TaskViews/Navigation';
import FilterDropdown from './TaskViews/FilterDropdown';
import { fetchProject, fetchTask, fetchTasks } from '../services/api';
import '../assets/styles/AnnotationPage.css';

const ReviewerPage = () => {
  const { taskId, projectId } = useParams();
  const { user, role } = useUser();
  const navigate = useNavigate();
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [label, setLabel] = useState('');
  const [tasks, setTasks] = useState([]);
  const [filter, setFilter] = useState('all');
  const [labelOptions, setLabelOptions] = useState([]);

  useEffect(() => {
    const fetchAndSetTaskAndLabels = async () => {
      setLoading(true);
      try {
        const taskResponse = await fetchTask(projectId, user.user_info.user_id, role, taskId);
        setTask(taskResponse.data);
        setLabel(taskResponse.data.label || '');

        const projectResponse = await fetchProject(projectId);
        const labels = projectResponse.data.labels.replace(/['"]/g, "").split(',').map((label, index) => ({
          key: `label${index + 1}`,
          text: label.trim(),
          value: label.trim(),
        }));
        setLabelOptions(labels);
      } catch (error) {
        setError('Failed to fetch task or project label options');
      } finally {
        setLoading(false);
      }
    };

    if (projectId && taskId && user) {
      fetchAndSetTaskAndLabels();
    }
  }, [taskId, projectId, user, role]);

  useEffect(() => {
    if (task) {
      const fetchAndSetTasks = async () => {
        try {
          const response = await fetchTasks(projectId, user.user_info.user_id, role);
          setTasks(response.data);
        } catch (error) {
          setError('Failed to fetch tasks');
        }
      };

      fetchAndSetTasks();
    }
  }, [task, projectId, user.user_info.user_id, role]);

  const handleLabelChange = (e, { value }) => setLabel(value);
  const handleTaskClick = (taskId) => navigate(`/projects/${projectId}/tasks/${taskId}/review`);
  const handleFilterChange = (e, { value }) => setFilter(value);

  const handleNavigation = (direction) => () => {
    const currentIndex = tasks.findIndex(t => t.task_id === taskId);
    const nextIndex = direction === 'next' ? currentIndex + 1 : currentIndex - 1;
    if (nextIndex >= 0 && nextIndex < tasks.length) {
      navigate(`/projects/${projectId}/tasks/${tasks[nextIndex].task_id}/review`);
    }
  };

  if (loading) return <Loader active>Loading Task...</Loader>;
  if (error) return <Message error content={error} />;

  const filteredTasks = tasks.filter(t => {
    if (filter === 'reviewed') return t.label;
    if (filter === 'unreviewed') return !t.label;
    return true;
  });

  return (
    <div className="annotation-container">
      <h2 className="page-title"><Icon name="tag" /> Review Tasks</h2>
      <div className="annotation-main-content">
        <div className="image-container">
          <div className="task-id">Task ID: {task.task_id}</div>
          <TaskImage imageUrl={task.image_url} />
        </div>
      
        <div className="sidebar-container">
          <FilterDropdown filter={filter} onFilterChange={handleFilterChange} />
          <div className="panel-container">
            <TaskList tasks={filteredTasks} onSelectTask={handleTaskClick} />
          </div>
        </div>
      </div>
      <LabelSelector labelOptions={labelOptions} currentLabel={label} onLabelChange={handleLabelChange} />
      <NavigationButtons 
        onPrevious={handleNavigation('previous')} 
        onNext={handleNavigation('next')} 
        disablePrevious={tasks.findIndex(t => t.task_id === taskId) === 0}
        disableNext={tasks.findIndex(t => t.task_id === taskId) === tasks.length - 1}
      />
    </div>
  );
};

export default ReviewerPage;
