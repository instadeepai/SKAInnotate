import React, { useState, useEffect } from 'react';
import { Table, Button, Loader, Message, Dropdown, Modal, Form, Icon, Popup } from 'semantic-ui-react';
import { useUser } from '../UserContext';
import { useFooter } from '../context/FooterContext';
import { fetchUsers, createUser, deleteUser, unAssignRole, assignRole } from '../services/api';
import '../assets/styles/Users.css';
import 'semantic-ui-css/semantic.min.css';
import { useNavigate, useParams } from 'react-router-dom';

const roleOptions = [
  { key: 'admin', text: 'Admin', value: 'admin' },
  { key: 'annotator', text: 'Annotator', value: 'annotator' },
  { key: 'reviewer', text: 'Reviewer', value: 'reviewer' },
];

const UsersPage = () => {
  const [users, setUsers] = useState([]);
  const { projectId } = useParams();
  const { setLogsMessage } = useFooter();
  const { user, role } = useUser();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [roleModalOpen, setRoleModalOpen] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [newUser, setNewUser] = useState({ username: '', email: '' });
  const [selectedRole, setSelectedRole] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    if (role !== 'admin') {
      navigate(`/projects/${projectId}/tasks`);
    } else {
      fetchAndSetUsers();
    }
  }, [role, projectId, navigate]);

  const fetchAndSetUsers = async () => {
    try {
      const response = await fetchUsers();
      setUsers(response.data);
    } catch (error) {
      setError('Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  const handleAssignRole = (userId) => {
    setSelectedUserId(userId);
    setRoleModalOpen(true);
  };

  const handleUpdateMessage = (message) => {
    setLogsMessage(message);
  };

  const handleRemoveUser = async (userId) => {
    try {
      await deleteUser(userId);
      setUsers(prevUsers => prevUsers.filter(user => user.user_id !== userId));
    } catch (error) {
      setError('Failed to remove user');
      handleUpdateMessage('Failed to remove user');
    }
  };

  const handleUnassignRole = async (userId, roleName) => {
    try {
      await unAssignRole({user_id: userId, role: roleName });
      const response = await fetchUsers();
      setUsers(response.data);
    } catch (error) {
      setError(`Failed to unassign role ${roleName}`);
    }
  };

  const handleChange = (e, { name, value }) => {
    setNewUser({ ...newUser, [name]: value });
  };

  const handleRoleChange = (e, { value }) => {
    setSelectedRole(value);
  };

  const handleSubmit = async () => {
    try {
      await createUser(newUser);
      setModalOpen(false);
      const response = await fetchUsers();
      setUsers(response.data);
      handleUpdateMessage('User Added successfully!');
    } catch (error) {
      setError('Failed to create user');
    }
  };

  const handleAssignRoleSubmit = async () => {
    const userRole = {user_id: selectedUserId, role: selectedRole }
    try {
      await assignRole(userRole);
      setRoleModalOpen(false);
      const response = await fetchUsers();
      setUsers(response.data);
      handleUpdateMessage(`User successfully assigned role: ${role}!`);
    } catch (error) {
      setError('Failed to assign role');
      handleUpdateMessage('User Added successfully!');
    }
  };

  const handleNavigateToTasks = () => {
    navigate(`/projects/${projectId}/tasks`);
  };

  if (loading) {
    return <Loader active>Loading Users...</Loader>;
  }

  if (error) {
    return <Message error>{error}</Message>;
  }

  return (
    <div className="users-page">
      <div className="userpage-buttons">
        <div className='left-head'>
        <Button 
          primary
          icon="arrow left"
          onClick={() => handleNavigateToTasks()}
        />
        <h1 className="users-page-title"><Icon name='users' /> Users</h1>
        </div>
        {role === 'admin' && (
          <Button 
            primary
            icon="user plus"
            onClick={() => setModalOpen(true)}
            content="Add New User"
         />
        )}
      </div>
      <div className='table-container'>
        <Table striped>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell>ID</Table.HeaderCell>
              <Table.HeaderCell>Username</Table.HeaderCell>
              <Table.HeaderCell>Email</Table.HeaderCell>
              <Table.HeaderCell>Roles</Table.HeaderCell>
              <Table.HeaderCell>Actions</Table.HeaderCell>
            </Table.Row>
          </Table.Header>

          <Table.Body>
            {users.map(user => (
              <Table.Row key={user.user_id}>
                <Table.Cell>{user.user_id}</Table.Cell>
                <Table.Cell>{user.username}</Table.Cell>
                <Table.Cell>{user.email}</Table.Cell>
                <Table.Cell>
                  {user.roles && user.roles.map(role => (
                    <Dropdown key={role.role_id} text={role.role_name} className="assigned-role-dropdown">
                      <Dropdown.Menu>
                        <Dropdown.Item key={role.role_id} onClick={() => handleUnassignRole(user.user_id, role.role_name)}>
                          Unassign {role.role_name}
                        </Dropdown.Item>
                      </Dropdown.Menu>
                    </Dropdown>
                  ))}
                </Table.Cell>
                <Table.Cell>
                 <Popup
                  content='Assign role'
                  trigger={<Button icon='key' onClick={() => handleAssignRole(user.user_id)}/>}
                  size='small'
                  inverted
                />
                <Popup
                  content='Delete user'
                  trigger={<Button icon='trash' onClick={() => handleRemoveUser(user.user_id)}/>}
                  size='small'
                  inverted
                />
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </div>
      <Modal open={modalOpen} onClose={() => setModalOpen(false)}>
        <Modal.Header>Add User</Modal.Header>
        <Modal.Content>
          <Form>
            <Form.Input
              label="Username"
              name="username"
              value={newUser.username}
              onChange={handleChange}
              required
            />
            <Form.Input
              label="Email"
              name="email"
              value={newUser.email}
              onChange={handleChange}
              type="email"
              required
            />
          </Form>
        </Modal.Content>
        <Modal.Actions>
          <Button onClick={() => setModalOpen(false)}>Cancel</Button>
          <Button primary onClick={handleSubmit}>Add User</Button>
        </Modal.Actions>
      </Modal>

      <Modal open={roleModalOpen} onClose={() => setRoleModalOpen(false)}>
        <Modal.Header>Assign Role</Modal.Header>
        <Modal.Content>
          <Dropdown
            placeholder="Select Role"
            fluid
            selection
            options={roleOptions}
            value={selectedRole}
            onChange={handleRoleChange}
          />
        </Modal.Content>
        <Modal.Actions>
          <Button onClick={() => setRoleModalOpen(false)}>Cancel</Button>
          <Button primary onClick={handleAssignRoleSubmit}>Assign Role</Button>
        </Modal.Actions>
      </Modal>
    </div>
  );
};

export default UsersPage;


// itsdangerous, python-jose, pip install SQLAlchemy, pip install psycopg2