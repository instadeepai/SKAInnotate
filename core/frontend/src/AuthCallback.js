import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const AuthCallback = () => {
  const navigate = useNavigate();
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log("AuthCallback component rendered");

    const handleAuthCallback = async () => {
      const queryParams = new URLSearchParams(window.location.search);
      const code = queryParams.get('code');
      console.log("Received code:", code);
      
      if (code) {
        try {
          const response = await axios.post('http://localhost:8000/auth/callback', { code });
          console.log("Response from callback endpoint:", response);
          
          if (response.status === 200) {
            const { frontend_redirect_url } = response.data;
            console.log("Redirecting to:", frontend_redirect_url);
            navigate(frontend_redirect_url); // Redirect to the provided URL
          } else {
            setError('Unexpected response from authentication. Please try again.');
          }
        } catch (error) {
          console.error('Error during authentication callback:', error);
          setError('Authentication failed. Please try again.');
        }
      } else {
        setError('No code found in query parameters.');
      }
    };

    handleAuthCallback();
  }, [navigate]);

  return (
    <div>
      {error ? <p>{error}</p> : <p>Authenticating...</p>}
    </div>
  );
};

export default AuthCallback;
