// import React, { useEffect, useState } from 'react';
// import axios from 'axios';
// import { useParams, useNavigate } from 'react-router-dom';
// import { Button, Image, Loader, Message, Radio, Dropdown, List } from 'semantic-ui-react';
// import { useUser } from '../UserContext'; // Ensure this is the correct path
// import '../assets/styles/AnnotationPage.css';
// import { fetchProject, fetchTasks } from '../services/api';

// const AnnotationPage = () => {
//   const { taskId, projectId } = useParams();
//   const { user, role } = useUser(); // Access the user information from context
//   const navigate = useNavigate();
//   const [task, setTask] = useState(null);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);
//   const [label, setLabel] = useState('');
//   const [tasks, setTasks] = useState([]);
//   const [filter, setFilter] = useState('all');
//   const [labelOptions, setLabelOptions] = useState([]);

//   useEffect(() => {
//     const fetchTask = async () => {
//       try {
//         const response = await fetchTasks(projectId, user.user_info.user_id, role, taskId);
//         setTask(response.data);
//         setLabel(response.data.label || '');
//       } catch (error) {
//         setError('Failed to fetch task');
//       } finally {
//         setLoading(false);
//       }
//     };

//     if (taskId && projectId && user && role) {
//       fetchTask();
//     }
//   }, [taskId, projectId, user.user_info.user_id, role]);

//   useEffect(() => {
//     const fetchandSetTasks = async () => {
//       try {
//         const response = await fetchTasks(projectId, user.user_info.user_id, role);
//         setTasks(response.data);
//       } catch (error) {
//         setError('Failed to fetch tasks');
//       }
//     };

//     if (task) {
//       fetchandSetTasks();
//     }
//   }, [task, projectId, user.user_info.user_id, role]);

//   useEffect(() => {
//     const fetchLabelOptions = async () => {
//       try {
//         const response = await fetchProject(projectId);
//         const labels = response.data.labels.replace(/['"]/g, "").split(',').map((label, index) => ({
//           key: `label${index + 1}`,
//           text: label.trim(),
//           value: label.trim(),
//         }));
//         setLabelOptions(labels);
//       } catch (error) {
//         setError('Failed to fetch label options');
//       }
//     };

//     if (projectId) {
//       fetchLabelOptions();
//     }
//   }, [projectId]);

//   const handleLabelChange = (e, { value }) => {
//     setLabel(value);
//   };

//   const handleNext = () => {
//     const currentIndex = tasks.findIndex(t => t.task_id === taskId);
//     if (currentIndex < tasks.length - 1) {
//       navigate(`/projects/${projectId}/tasks/${tasks[currentIndex + 1].task_id}`);
//     }
//   };

//   const handlePrevious = () => {
//     const currentIndex = tasks.findIndex(t => t.task_id === taskId);
//     if (currentIndex > 0) {
//       navigate(`/projects/${projectId}/tasks/${tasks[currentIndex - 1].task_id}`);
//     }
//   };

//   const handleFilterChange = (e, { value }) => {
//     setFilter(value);
//   };

//   const handleTaskClick = (taskId) => {
//     navigate(`/projects/${projectId}/tasks/${taskId}`);
//   };

//   if (loading) {
//     return <Loader active>Loading Task...</Loader>;
//   }

//   if (error) {
//     return <Message error>{error}</Message>;
//   }

//   const filteredTasks = tasks.filter(t => {
//     if (filter === 'labeled') return t.label;
//     if (filter === 'unlabeled') return !t.label;
//     return true;
//   });

//   return (
//     <div className="annotation-container">
//       <div className="annotation-main-content">
//         <div className="image-container">
//           <div className="task-id">Task ID: {task.task_id}</div>
//           <Image src={task.image_url} size="large" centered />
//         </div>

//         <div className="sidebar-container">
//           <div className="filter-dropdown">
//             <span className="filter-text">Filter Tasks</span>
//             <Dropdown
//               placeholder="Filter Tasks"
//               fluid
//               selection
//               options={[
//                 { key: 'all', text: 'All', value: 'all' },
//                 { key: 'labeled', text: 'Labeled', value: 'labeled' },
//                 { key: 'unlabeled', text: 'Unlabeled', value: 'unlabeled' },
//               ]}
//               value={filter}
//               onChange={handleFilterChange}
//             />
//           </div>
//           <div className="panel-container">
//             <List>
//               {filteredTasks.map(task => (
//                 <List.Item key={task.task_id} onClick={() => handleTaskClick(task.task_id)} style={{ cursor: 'pointer' }}>
//                   Task ID: {task.task_id}
//                 </List.Item>
//               ))}
//             </List>
//           </div>
//         </div>
//       </div>

//       <div className="label-options">
//         <h3>Label Options</h3>
//         <div className="labels-container">
//           {labelOptions.map(option => (
//             <div key={option.value} className="label-option">
//               <Radio
//                 label={option.text}
//                 value={option.value}
//                 checked={label === option.value}
//                 onChange={handleLabelChange}
//               />
//             </div>
//           ))}
//         </div>
//       </div>

//       <div className="navigation-buttons">
//         <Button onClick={handlePrevious} disabled={tasks.findIndex(t => t.task_id === taskId) === 0}>Previous</Button>
//         <Button onClick={handleNext} disabled={tasks.findIndex(t => t.task_id === taskId) === tasks.length - 1}>Next</Button>
//       </div>
//     </div>
//   );
// };

// export default AnnotationPage;
