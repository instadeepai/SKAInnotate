import React, { useEffect, useState } from 'react';
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
import { init, fetchClientId, fetchBaseUrl } from './services/api';

// Function to fetch the base API URL
const fetchBaseApiUrl = async () => {
  try {
    const response = await fetchBaseUrl(); // Adjust the endpoint based on your FastAPI setup
    return response.data.apiUrl;
  } catch (error) {
    console.error('Error fetching base API URL:', error);
    throw error; // Rethrow to handle in the component
  }
};

const AppRoutes = ({ baseApiUrl }) => {
  const location = useLocation();
  const isLoginPage = location.pathname === '/';

  return (
    <>
      {!isLoginPage && <Header />}
      <Routes>
        <Route path="/" element={<Login baseApiUrl={baseApiUrl} />} />
        <Route path="/projects" element={<ProjectsPage baseApiUrl={baseApiUrl} />} />
        <Route path="/projects/:projectId/tasks" element={<TasksPage baseApiUrl={baseApiUrl} />} />
        <Route path="/projects/:projectId/tasks/:taskId" element={<AnnotationPage baseApiUrl={baseApiUrl} />} />
        <Route path="/projects/:projectId/users" element={<UsersPage baseApiUrl={baseApiUrl} />} />
      </Routes>
      {!isLoginPage && <Footer />}
    </>
  );
};

function App() {
  const [clientId, setClientId] = useState('');
  const [baseApiUrl, setBaseApiUrl] = useState(''); // State to hold the base API URL

  useEffect(() => {
    const getClientId = async () => {
      try {
        const response = await fetchClientId();
        setClientId(response.data.clientId);
      } catch (error) {
        console.error('There was an error fetching the client ID:', error);
      }
    };

    const loadBaseApiUrl = async () => {
      try {
        const apiUrlResponse = await fetchBaseApiUrl();
        setBaseApiUrl(apiUrlResponse.data.apiUrl);
      } catch (error) {
        console.error('Failed to load base API URL:', error);
      }
    };

    getClientId();
    loadBaseApiUrl(); // Call the function to load the URL

    init().catch(error => {
      console.error('There was an error fetching data:', error);
    });
  }, []);

  return (
    <GoogleOAuthProvider clientId={clientId}>
      <UserProvider>
        <FooterProvider>
          <Router>
            <AppRoutes baseApiUrl={baseApiUrl} /> {/* Pass the baseApiUrl to your routes */}
          </Router>
        </FooterProvider>
      </UserProvider>
    </GoogleOAuthProvider>
  );
}

export default App;

// import React, { useEffect, useState } from 'react';
// import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
// import axios from 'axios';
// import { GoogleOAuthProvider } from '@react-oauth/google';
// import { UserProvider } from './UserContext';
// import { FooterProvider } from './context/FooterContext';

// import Login from './views/Login';
// import TasksPage from './views/Tasks';
// import UsersPage from './views/Users';
// import ProjectsPage from './views/Projects';
// import AnnotationPage from './views/Annotations';

// import Header from './components/Header';
// import Footer from './components/Footer';

// import 'semantic-ui-css/semantic.min.css';
// import './assets/styles/App.css';
// import { init, fetchClientId } from './services/api';

// const AppRoutes = () => {
//   const location = useLocation();
//   const isLoginPage = location.pathname === '/';

//   return (
//     <>
//       {!isLoginPage && <Header />}
//       <Routes>
//         <Route path="/" element={<Login />} />
//         <Route path="/projects" element={<ProjectsPage />} />
//         <Route path="/projects/:projectId/tasks" element={<TasksPage />} />
//         <Route path="/projects/:projectId/tasks/:taskId" element={<AnnotationPage />} />
//         <Route path="/projects/:projectId/users" element={<UsersPage />} />
//       </Routes>
//       {!isLoginPage && <Footer />}
//     </>
//   );
// };

// function App() {
//   const [clientId, setClientId] = useState('');

//   useEffect(() => {
//     const getClientId = async () => {
//       try {
//         const response = await fetchClientId(); // Fetch the client ID from the backend
//         setClientId(response.data.clientId);
//       } catch (error) {
//         console.error('There was an error fetching the client ID:', error);
//       }
//     };

//     getClientId();

//     init().catch(error => {
//       console.error('There was an error fetching data:', error);
//     });
//   }, []);

//   return (
//     <GoogleOAuthProvider clientId={clientId}>
//       <UserProvider>
//         <FooterProvider>
//           <Router>
//             <AppRoutes baseApiUrl={baseApiUrl}/>
//           </Router>
//         </FooterProvider>
//       </UserProvider>
//     </GoogleOAuthProvider>
//   );
// }
// export default App;

// import React, { useEffect } from 'react';
// import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
// import axios from 'axios';
// import { GoogleOAuthProvider } from '@react-oauth/google';
// import { UserProvider } from './UserContext';
// import { FooterProvider } from './context/FooterContext';

// import Login from './views/Login';
// import TasksPage from './views/Tasks';
// import UsersPage from './views/Users';
// import ProjectsPage from './views/Projects';
// import AnnotationPage from './views/Annotations';

// import Header from './components/Header';
// import Footer from './components/Footer';

// import 'semantic-ui-css/semantic.min.css';
// import './assets/styles/App.css';
// import { init } from './services/api';

// const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;

// const AppRoutes = () => {
//   const location = useLocation();
//   const isLoginPage = location.pathname === '/';

//   return (
//     <>
//       {!isLoginPage && <Header />}
//       <Routes>
//         <Route path="/" element={<Login />} />
//         <Route path="/projects" element={<ProjectsPage />} />
//         <Route path="/projects/:projectId/tasks" element={<TasksPage />} />
//         <Route path="/projects/:projectId/tasks/:taskId" element={<AnnotationPage />} />
//         <Route path="/projects/:projectId/users" element={<UsersPage />} />
//       </Routes>
//       {!isLoginPage && <Footer />}
//     </>
//   );
// };

// function App() {
//   useEffect(() => {
//     init()
//       .catch(error => {
//         console.error('There was an error fetching data:', error);
//       });
//   }, []);

//   return (
//     <GoogleOAuthProvider clientId={clientId}>
//       <UserProvider>
//         <FooterProvider>
//           <Router>
//             <AppRoutes />
//           </Router>
//         </FooterProvider>
//       </UserProvider>
//     </GoogleOAuthProvider>
//   );
// }

// export default App;