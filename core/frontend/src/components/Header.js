import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Dropdown, Icon, List, Loader, Message, Button } from 'semantic-ui-react';
import { useUser } from '../UserContext';
import '../assets/styles/Header.css';

const Header = () => {
  const { user, role, loading, error, setRole, logout } = useUser();
  const navigate = useNavigate();

  useEffect(() => {
    if (user && user.role) {
      setRole(user.role);
    }
  }, [user, setRole]);

  const handleRoleChange = (role) => {
    setRole(role);
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  if (loading) {
    return <Loader active>Loading User Information...</Loader>;
  }

  if (error) {
    return <Message error>{error}</Message>;
  }

  return (
    <div className="header-container">
      <div className="header-menu">
        {/* <Dropdown icon="sidebar" floating button className="icon">
          <Dropdown.Menu>
            <Dropdown.Item as={Link} to="/projects" text="Projects" />
            <Dropdown.Item as={Link} to="/users" text="Users" />
          </Dropdown.Menu>
        </Dropdown> */}
        <h1 className="app-name">SKAInnotate</h1>
        <div className="user-info">
          <Dropdown
            text={role || 'Select Role'}
            icon='angle down'
            floating
            labeled
            button
            className="role-dropdown"
          >
            <Dropdown.Menu>
              {user && user.user_info.roles.map((role) => (
                <Dropdown.Item
                  key={role}
                  text={role}
                  style={{ color: 'black' }}
                  onClick={() => handleRoleChange(role)}
                />
              ))}
            </Dropdown.Menu>
          </Dropdown>

          <div className="user-icon-container">
            <Icon name="user" size="large" style={{ cursor: 'pointer' }} />
            <div className="user-dropdown">
              <List>
                <List.Item>
                  <List.Header>Username:</List.Header>
                  <List.Description>{user.user_info.username}</List.Description>
                </List.Item>
                <List.Item>
                  <List.Header>Email:</List.Header>
                  <List.Description>{user.user_info.email}</List.Description>
                </List.Item>
                <List.Item>
                  <Button onClick={handleLogout} color="red">
                    Logout
                  </Button>
                </List.Item>
              </List>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Header;
