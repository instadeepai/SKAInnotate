import React, { useState, useEffect } from 'react';
import { Segment, Header, Divider, Button, Icon } from 'semantic-ui-react';
import { deleteDeployment, getDeployments } from '../services/api';
import alertify from 'alertifyjs';
import 'alertifyjs/build/css/alertify.min.css';  // Import the CSS for Alertify

import '../PastDeployments.css';

const PastDeployments = () => {
  const [deployments, setDeployments] = useState([]);
  const [loading, setLoading] = useState(true); // Added loading state for feedback

  useEffect(() => {
    const fetchDeployments = async () => {
      try {
        const fetchedDeployments = await getDeployments();
        setDeployments(fetchedDeployments);
      } catch (error) {
        console.error('Error fetching deployments:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchDeployments();
  }, []);

const handleDelete = (deployment) => {
  // Show confirmation dialog before deleting

  alertify.confirm(
    'Remove Deployment', 
    `Are you sure you want to remove the deployment "${deployment.service_name}"?`, 
    async function() {
      try {
        await deleteDeployment(deployment.id);
        setDeployments(deployments.filter(d => d.id !== deployment.id));
        alertify.success(`Deployment "${deployment.project_id}" deleted successfully`);
      } catch (error) {
        console.error(`Error deleting deployment ${deployment.id}:`, error);
        alertify.error('Error deleting the deployment');
      }
    },
    function() {
      alertify.error('canceled');
    }
  );
};


  return (
    <Segment className="past-deployments-container">
      <Header as="h2" textAlign="center">
        Past Deployments
      </Header>

      <Divider />

      {loading ? (
        <p>Loading deployments...</p> // Display loading message while data is being fetched
      ) : deployments.length === 0 ? (
        <p>No deployments to show at this time.</p>
      ) : (
        <div>
          {deployments.map(deployment => (
            <div key={deployment.id} className="deployment-item">
              <div className="delete-button-container">
                <Button
                  color="red"
                  icon
                  size="small"
                  aria-label={`Delete deployment ${deployment.project_id}`} // Improved accessibility
                  onClick={() => handleDelete(deployment)}
                >
                  <Icon name="trash" />
                </Button>
              </div>
              <p><strong>Service Name:</strong> {deployment.service_name}</p>
              <p><strong>Project ID:</strong> {deployment.project_id}</p>
              <p><strong>Instance Name:</strong> {deployment.instance_name}</p>
              <p>
                <strong>Deployment Status:</strong>{" "}
                <span className={`deployment-status ${deployment.deployment_status.toLowerCase()}`}>
                  {deployment.deployment_status}
                </span>
              </p>
              <p>
                <strong>Service URL:</strong>{" "}
                <a href={deployment.service_url} target="_blank" rel="noopener noreferrer">
                  {deployment.service_url}
                </a>
              </p>
              <Divider className="deployment-divider" />
            </div>
          ))}
        </div>
      )}
    </Segment>
  );
};

export default PastDeployments;
