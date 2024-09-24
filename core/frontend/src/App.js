import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import axios from 'axios';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { UserProvider } from './UserContext';
import { FooterProvider } from './context/FooterContext';

import Login from './views/Login';
import TasksPage from './views/Tasks';
import UsersPage from './views/Users';
import ProjectsPage from './views/Projects';
import AnnotationPage from './views/Annotations';

import Header from './components/Header';
import Footer from './components/Footer';

import 'semantic-ui-css/semantic.min.css';
import './assets/styles/App.css';
import { init } from './services/api';

const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;

const AppRoutes = () => {
  const location = useLocation();
  const isLoginPage = location.pathname === '/';

  return (
    <>
      {!isLoginPage && <Header />}
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/projects/:projectId/tasks" element={<TasksPage />} />
        <Route path="/projects/:projectId/tasks/:taskId" element={<AnnotationPage />} />
        <Route path="/projects/:projectId/users" element={<UsersPage />} />
      </Routes>
      {!isLoginPage && <Footer />}
    </>
  );
};

function App() {
  useEffect(() => {
    init()
      .catch(error => {
        console.error('There was an error fetching data:', error);
      });
  }, []);

  return (
    <GoogleOAuthProvider clientId={clientId}>
      <UserProvider>
        <FooterProvider>
          <Router>
            <AppRoutes />
          </Router>
        </FooterProvider>
      </UserProvider>
    </GoogleOAuthProvider>
  );
}

export default App;