import React, { useState } from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { Button, Segment, Header, Icon, Grid, Message, Divider } from 'semantic-ui-react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../UserContext';
import { verifyTokenCallback } from '../services/api';
import '../assets/styles/Login.css';
import PopupMessage from '../components/popUpMessage';

const Login = () => {
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const { user, setUser, role } = useUser();

  const responseMessage = async (response) => {
    try {
      console.log("Authentication step: Response credentials: ", response.credential);
      const backendResponse = await verifyTokenCallback({ token: response.credential });
      if (backendResponse.status === 200) {
        let user_info = backendResponse.data;
        setUser(user_info);
        console.log("Authentication Successful: Redirecting to projects Page");
        
        if (!role) {
          PopupMessage();
        } else {
          navigate('/projects');
        }
      } else {
        setError('Unexpected response from authentication. Please try again.');
      }
    } catch (error) {
      console.error('Error during authentication callback:', error);
      setError('Authentication failed. Please try again.');
    }
  };

  const errorMessage = (error) => {
    console.error('Google login error:', error);
    setError('Failed to authenticate with Google. Please try again.');
  };

  return (
    <div className="login-container">
      <Segment placeholder className="login-segment">
        <Header as="h2" icon textAlign="center">
          <Icon name="users" />
          Welcome to SKAInnotate
          <Header.Subheader>
            Sign in to get started.
          </Header.Subheader>
        </Header>

        {error && <Message error content={error} />}

        <Divider horizontal>Sign In</Divider>

        <div className="google-auth">
          <GoogleLogin onSuccess={responseMessage} onError={errorMessage} />
        </div>
      </Segment>
    </div>
  );
};

export default Login;