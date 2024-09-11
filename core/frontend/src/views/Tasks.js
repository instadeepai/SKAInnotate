import React, { useEffect, useState } from 'react';
import { Loader, Message, Button, Icon, Dropdown, Sidebar, Segment } from 'semantic-ui-react';
import { useParams, useNavigate } from 'react-router-dom';
import { useUser } from '../UserContext';
import ProjectStats from "../components/projectStatistics";
import { fetchTasks, UploadTaskFromCSV, assignTasks, fetchReviewers, fetchReviewersbyTask, exportAnnotations, deleteTask, assignTaskToReviewer, unAssignTaskToReviewer } from '../services/api';
import AnnotatorTasksList from './AnnotatorTasks';
import AdminTasksList from './AdminTasks';
import { saveAs } from 'file-saver';
import 'semantic-ui-css/semantic.min.css';
import '../assets/styles/Tasks.css'

const TasksPage = () => {
  const { projectId } = useParams();
  const { user, role } = useUser();
  const [tasks, setTasks] = useState([]);
  const [filteredTasks, setFilteredTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [csvModalOpen, setCsvModalOpen] = useState(false);
  const [csvFile, setCsvFile] = useState(null);
  const [success, setSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [visible, setVisible] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [reviewers, setReviewers] = useState([]);
  const [selectedReviewer, setSelectedReviewer] = useState([]);
  const [assignedReviewers, setAssignedReviewers] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        await fetchAndSetTasks();
        await fetchAndSetReviewers();
      } catch (error) {
        console.error('Error fetching data:', error);
        setError('Failed to fetch data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [projectId, user.user_info.user_id, role]);

    const fetchAndSetTasks = async () => {
      try {
        const response = await fetchTasks(projectId, user.user_info.user_id, role);
        setTasks(response.data);
        setFilteredTasks(response.data);
      } catch (error) {
        setError('Failed to fetch tasks');
      } finally {
        setLoading(false);
      }
    };

  const fetchAndSetReviewers = async () => {
    try {
      const response = await fetchReviewers();
      setReviewers(response.data.map(reviewer => ({
        key: reviewer.user_id,
        text: reviewer.username,
        value: reviewer.user_id
      })));
    } catch (error) {
      console.error('Failed to fetch reviewers:', error);
      setError('Failed to fetch reviewers');
    }
  };

  const handleFilterChange = (completionStatus) => {
    setFilteredTasks(tasks.filter(task => task.completion_status === completionStatus));
  };

  const handleAssignTasksToAnnotators = async () => {
    try {
      await assignTasks(projectId);
      
      setSuccessMessage('Tasks (Re)assigned successfully');
      setSuccess(true);
      setTimeout(() => setSuccess(false), 5000);
      
    } catch (error) {
      setError('Failed to assign tasks');
    }
    // navigate(0);
  };

  const handleAssignReviewer = async (task, reviewerId) => {
    if (reviewerId) {
      // const taskAssignData = ;
      try {
        await assignTaskToReviewer(task.task_id, {user_id: reviewerId,
        assignment_type: 'review'
      });
        setSuccessMessage('Reviewer assigned successfully');
        // setSuccess(true);
        setTimeout(() => setSuccess(false), 3000);
      } catch (error) {
        console.error('Failed to assign reviewer:', error);
      }
    } else {
        await unAssignTaskToReviewer(task.task_id, {assignment_type: 'review'});
    }
  };

  const handleDeleteTask = async (task) => {
    try {
      await deleteTask(task.task_id);
      setTasks(prevTasks => prevTasks.filter(t => t.task_id !== task.task_id));
      setSuccessMessage('Task deleted successfully');
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (error) {
      setError('Failed to delete task');
    }
  };

  const handleRowClick = (taskId) => {
    navigate(`/projects/${projectId}/tasks/${taskId}`);
  };

  const handleCsvFileChange = (e) => {
    setCsvFile(e.target.files[0]);
  };

  const handleCsvSubmit = async () => {
    if (!csvFile) return;

    const formData = new FormData();
    formData.append('file', csvFile);
    try {
      await UploadTaskFromCSV(projectId, formData);
      const response = await fetchTasks(projectId, user.user_info.user_id, role);
      setTasks(response.data);
      setFilteredTasks(response.data);
      setCsvModalOpen(false);
      setSuccessMessage('Tasks updated successfully from CSV');
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (error) {
      setError('Failed to update tasks from CSV');
    }
  };

  const handleExport = async (format) => {
    try {
      const response = await exportAnnotations(projectId, format);
      saveAs(response.data, `annotations.${format}`);
    } catch (error) {
      alert('Failed to export annotations');
    }
  };

  const exportOptions = [
    { key: 'csv', text: 'Export to CSV', value: 'csv' },
    { key: 'json', text: 'Export to JSON', value: 'json' },
  ];

  const filterOptions = [
    { key: 'all', text: 'All Tasks', value: 'all' },
    { key: 'completed', text: 'Completed', value: true },
    { key: 'uncompleted', text: 'Uncompleted', value: false }
  ];

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = tasks.slice(indexOfFirstItem, indexOfLastItem);

  const handlePaginationChange = (e, { activePage }) => setCurrentPage(activePage);
  const totalPages = Math.ceil(filteredTasks.length / itemsPerPage);

   const handleNavigateToProjects = () => {
    navigate(`/projects`);
  };

  if (loading) return <Loader active>Loading Tasks...</Loader>;
  if (error) return <Message error>{error}</Message>;
  const handleNavigateToUsers = () => {
    navigate(`/projects/${projectId}/users`);
  };
  return (
    <div className="tasks-page">
      <div className='taskspage-container'>
        <div className='tasks-back-arrow'>
          <Button 
            primary
            icon="arrow left"
            onClick={() => handleNavigateToProjects()}
          />
        <h1 className="tasks-page-title"><Icon name='tasks' /> Tasks </h1>
        </div>
        
        {success && <Message success>{successMessage}</Message>}
        {role === 'admin' && (
          <div className="export-buttons">
            {/* <Dropdown
              text="Filter"
              icon="filter"
              labeled
              button
              className="icon"
            >
              <Dropdown.Menu>
                {filterOptions.map(option => (
                  <Dropdown.Item
                    key={option.key}
                    text={option.text}
                    onClick={() => handleFilterChange(option.value)}
                  />
                ))}
              </Dropdown.Menu>
            </Dropdown> */}

            <Button 
              icon="upload"
              onClick={() => setCsvModalOpen(true)}
              aria-label="Open modal to update tasks from CSV"
              className="icon-button"
              content="Upload"
            />

            <Button 
              icon="tasks"
              onClick={handleAssignTasksToAnnotators}
              aria-label="Assign tasks to selected users"
              className="icon-button"
              content="Assign"
            />

            <Dropdown
              text="Export Data"
              icon="download"
              labeled
              button
              className="icon"
            >
              <Dropdown.Menu>
                {exportOptions.map(option => (
                  <Dropdown.Item
                    key={option.key}
                    text={option.text}
                    onClick={() => handleExport(option.value)}
                  />
                ))}
              </Dropdown.Menu>
            </Dropdown>
            <Button 
              icon="users"
              onClick={() => handleNavigateToUsers()}
              aria-label="open users page"
              className="icon-button"
              content="Users"
            />
            <Button 
              icon="chart bar" 
              onClick={() => setVisible(!visible)} 
              content="Stats"
              aria-label="Toggle statistics panel"
            />
          </div>
        )}
      </div>
      
      <Sidebar.Pushable as={Segment}>
        <Sidebar className='sidebar-container'
          as={Segment}
          animation='overlay'
          icon='labeled'
          onHide={() => setVisible(false)}
          vertical
          visible={visible}
          width='wide'
          direction='right'
        >
          <ProjectStats projectId={projectId} />
          {/* Statistics and other information can be dynamically loaded here */}
        </Sidebar>
        <Sidebar.Pusher>
          {role === 'admin' ?
            <AdminTasksList
              currentPage={currentPage}
              onPaginationChange={handlePaginationChange}
              currentItems={currentItems}
              totalPages={totalPages}
              onCsvFileChange={handleCsvFileChange}
              onCsvSubmit={handleCsvSubmit}
              setCsvModalOpen={setCsvModalOpen}
              csvModalOpen={csvModalOpen}
              onAssignToReviewer={handleAssignReviewer}
              onDelete={handleDeleteTask}
              reviewers={reviewers}
            /> :
            <AnnotatorTasksList
              tasks={filteredTasks}
              onRowClick={handleRowClick}
              onCsvFileChange={handleCsvFileChange}
              onCsvSubmit={handleCsvSubmit}
              setCsvModalOpen={setCsvModalOpen}
              csvModalOpen={csvModalOpen}
            />
          }
        </Sidebar.Pusher>
      </Sidebar.Pushable>
    </div>
  );
};

export default TasksPage;