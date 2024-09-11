import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Loader, Message, Icon, Button } from 'semantic-ui-react';
import { useUser } from '../UserContext';
import TaskImage from './TaskViews/TaskImage';
import TaskList from './TaskViews/TaskList';
import LabelSelector from './TaskViews/LabelSelector';
import NavigationButtons from './TaskViews/Navigation';
import FilterDropdown from './TaskViews/FilterDropdown';
import { createAnnotation,
        createReview,
        fetchAnnotationByUserAndTaskID,
        fetchReviewByUserAndTaskID,
        fetchProject,
        fetchTask,
        fetchTasks,
        updateAnnotation,
        updateReview } from '../services/api';
import '../assets/styles/AnnotationPage.css';

const AnnotationPage = () => {
  const { taskId, projectId } = useParams();
  const { user, role } = useUser();
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [label, setLabel] = useState('');
  const [tasks, setTasks] = useState([]);
  const [filter, setFilter] = useState('all');
  const [labelOptions, setLabelOptions] = useState([]);
  const navigate = useNavigate();


  useEffect(() => {
    if (role !== 'annotator' && role !== 'reviewer') {
      navigate(`/projects/${projectId}/tasks`);
    }
    const fetchAndSetTaskAndLabels = async () => {
      setLoading(true);
      try {
        const taskResponse = await fetchTask(projectId, user.user_info.user_id, role, taskId);
        setTask(taskResponse.data);

        if (role === 'annotator'){
          const labelResponse = await fetchAnnotationByUserAndTaskID(user.user_info.user_id, taskId);
          if (labelResponse.data){
          setLabel(labelResponse.data.label);
        }
        else{
          setLabel('');
        }}

        else {
          const labelResponse = await fetchReviewByUserAndTaskID(user.user_info.user_id, taskId);
          if (labelResponse.data){
          setLabel(labelResponse.data.label);
        }
        else{
          setLabel('');
        }
      }

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

const handleLabelChange = async (e, data) => {
  if (role === 'annotator') {
    submitAnnotation(data);
  } else {
    submitReview(data);
  }
};

const submitAnnotation = async (data) => {
  try {
    const annotationResponse = await fetchAnnotationByUserAndTaskID(user.user_info.user_id, task.task_id);
    if (annotationResponse.data) {
      const updatedAnnotation = {
        ...annotationResponse.data,
        label: data.value
      };
      await updateAnnotation(annotationResponse.data.annotation_id, updatedAnnotation);
    } else {
      await createAnnotation({
        label: data.value,
        task_id: task.task_id,
        user_id: user.user_info.user_id
      });
    }
    setLabel(data.value);
  } catch (error) {
    console.error("Failed to submit annotation:", error);
  }
};

const submitReview = async (data) => {
  try {
    const reviewResponse = await fetchReviewByUserAndTaskID(user.user_info.user_id, task.task_id);
    if (reviewResponse.data) {
      const updatedReview = {
        ...reviewResponse.data,
        label: data.value
      };
      await updateReview(reviewResponse.data.review_id, updatedReview);
    } else {
      await createReview({
        label: data.value,
        task_id: task.task_id,
        user_id: user.user_info.user_id
      });
    }
    setLabel(data.value);
  } catch (error) {
    console.error("Failed to submit review:", error);
  }
};


  const handleTaskClick = (taskId) => navigate(`/projects/${projectId}/tasks/${taskId}`);
  const handleFilterChange = (e, { value }) => setFilter(value);

  const handleNavigation = (direction) => async() => {
    const currentIndex = tasks.findIndex(t => t.task_id === taskId);
    const nextIndex = direction === 'next' ? currentIndex + 1 : currentIndex - 1;
    if (nextIndex >= 0 && nextIndex < tasks.length) {
      navigate(`/projects/${projectId}/tasks/${tasks[nextIndex].task_id}`);
    }
  };
  const calculateAnnotationFractions = (task) => {
  const { annotations } = task;
  const count = {};
  const totalAnnotations = annotations.length;

  // Count occurrences of each annotation
  annotations.forEach(annotation => {
    count[annotation] = (count[annotation] || 0) + 1;
  });

  // Calculate fractions
  const fractions = {};
  for (const annotation in count) {
    fractions[annotation] = count[annotation] / totalAnnotations;
  }

  return fractions;
};

  const handleNavigateToTasks = () => {
    navigate(`/projects/${projectId}/tasks`);
  };

  if (loading) return <Loader active>Loading Task...</Loader>;
  if (error) return <Message error content={error} />;

  const filteredTasks = tasks.filter(t => {
    if (filter === 'labeled') return t.completion_status;
    if (filter === 'reviewed') return t.completion_status;
    if (filter === 'unlabeled') return !t.completion_status;
    if (filter === 'unreviewed') return !t.completion_status;
    return true;
  });
  const header = role === 'annotator' ? 'Annotation': role === 'reviewer' ? 'Reviewer': 'Admin';
  const labelOptionsTitle = role === 'annotator' ? 'Label Options': role === 'reviewer' ? "Label Options (Annotators' Agreement Score)": 'Admin';
  const annotationAgreementScores = role === 'reviewer' ? calculateAnnotationFractions(task): {};

  return (
    <div className="annotation-container">
      <div className='annotation-page-container'>
        <div className='tasks-back-arrow'>
          <Button 
            icon="arrow left"
            primary
            onClick={() => handleNavigateToTasks()}
          />
        {/* <h1 className="tasks-page-title"><Icon name='tasks' /> Tasks </h1> */}
        <h2 className="annotation-page-title"><Icon name="tag" /> {header} Tasks</h2>
        </div>
      </div>
      
      <div className="annotation-main-content">
        <div className="image-container">
          <div className="task-id">Task ID: {task.task_id}</div>
          <TaskImage imageUrl={task.image_url} />
        </div>
      
        <div className="sidebar-container">
          <FilterDropdown role={role} filter={filter} onFilterChange={handleFilterChange} />
          <div className="panel-container">
            <TaskList tasks={filteredTasks} onSelectTask={handleTaskClick} />
          </div>
        </div>
      </div>

      <LabelSelector 
        labelOptionsTitle={labelOptionsTitle}
        labelOptions={labelOptions}
        currentLabel={label}
        onLabelChange={handleLabelChange}
        agreementScores={annotationAgreementScores} 
        />

      <NavigationButtons 
        onPrevious={handleNavigation('previous')} 
        onNext={handleNavigation('next')} 
        disablePrevious={tasks.findIndex(t => t.task_id === taskId) === 0}
        disableNext={tasks.findIndex(t => t.task_id === taskId) === tasks.length - 1}
      />
    </div>
  );
};

export default AnnotationPage;
