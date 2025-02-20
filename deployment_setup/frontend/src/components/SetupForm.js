import React, { useState } from 'react';
import '../SetupForm.css';
import alertify from 'alertifyjs';
import {
  setProject,
  createSQLInstance,
  deployApp,
  addDeployment,
} from '../services/api';
import {
  Segment,
  Button,
  Form,
  Header,
  Divider,
  Grid,
  Icon,
} from 'semantic-ui-react';
import 'semantic-ui-css/semantic.min.css';

const SetupForm = () => {
  // State for submission and file upload
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [serviceAccountFile, setServiceAccountFile] = useState(null);

  // Controlled state for text fields
  const [formData, setFormData] = useState({
    project_id: '',
    instance_name: '',
    region: '',
    database_name: '',
    db_user: '',
    db_pass: '',
    google_client_id: '',
    superuser_username: '',
    superuser_email: '',
    service_name: '',
  });

  // Semantic UI’s Form.Input onChange returns (event, data)
  const handleInputChange = (e, { name, value }) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // File input handler (native input)
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/json' && file.name.endsWith('.json')) {
      setServiceAccountFile(file);
    } else {
      alertify.error('Please upload a valid JSON file for the service account.');
    }
  };

  // Validate all fields have a value
  const validateForm = () => {
    for (const key in formData) {
      if (!formData[key]) {
        alertify.error('Please fill all required fields.');
        return false;
      }
    }
    if (!serviceAccountFile) {
      alertify.error('Please upload a service account file.');
      return false;
    }
    return true;
  };

  // Submission handler combining text fields and file upload
  const setupInfrastructure = async (event) => {
    event.preventDefault();
    if (loading) return;
    setLoading(true);
    setSuccess(false);

    if (!validateForm()) {
      setLoading(false);
      return;
    }

    let service_url = '';
    let deployment_status = '';

    try {
      alertify.success('Application launch in progress...');
      const deployResponse = await deployApp({
        project_id: formData.project_id,
        instance_name: formData.instance_name,
        region: formData.region,
        db_name: formData.database_name,
        db_user: formData.db_user,
        db_pass: formData.db_pass,
        clientId: formData.google_client_id,
        service_name: formData.service_name,
        superuser_email: formData.superuser_email,
        superuser_username: formData.superuser_username,
        service_account_file: serviceAccountFile,
      });
      if (deployResponse && deployResponse.service_url) {
        service_url = deployResponse.service_url;
        deployment_status = 'Success';
        alertify.success(`App launched successfully at ${service_url}!`);
        setSuccess(true);
      } else {
        deployment_status = 'Failed';
      }
    } catch (error) {
      alertify.error(`Error launching application: ${error?.message || 'Unknown error'}`);
      deployment_status = 'Failed';
    } finally {
      try {
        await addDeployment({
          project_id: formData.project_id,
          instance_name: formData.instance_name,
          service_name: formData.service_name,
          service_url,
          deployment_status,
        });
      } catch (error) {
        console.error('Error adding deployment:', error);
      }
      setLoading(false);
    }
  };

  return (
    <Segment className="setup-segment">
      <Header as="h2" textAlign="center">
        Let's Launch Your SKAInnotate Journey!
      </Header>

      <Form
        id="setup-form"
        onSubmit={setupInfrastructure}
        method="POST"
        encType="multipart/form-data"
        loading={loading}
        success={success}
      >
        <Header as="h3">Project Setup</Header>
        <Form.Input
          label="Project ID"
          name="project_id"
          placeholder="my-project-1"
          value={formData.project_id}
          onChange={handleInputChange}
          required
        />

        <Divider />
        <Header as="h3">Cloud SQL Setup</Header>
        <p>
          For detailed instructions on setting up a Google Cloud SQL instance, please refer to the{' '}
          <a
            href="https://github.com/instadeepai/SKAInnotate?tab=readme-ov-file#database-setup"
            target="_blank"
            rel="noopener noreferrer"
          >
            Google SQL setup for SKAInnotate
          </a>.
        </p>
        <Grid columns={2} stackable>
          <Grid.Row>
            <Grid.Column>
              <Form.Input
                label="Instance Name"
                name="instance_name"
                placeholder="my-db-instance"
                value={formData.instance_name}
                onChange={handleInputChange}
                required
              />
            </Grid.Column>
            <Grid.Column>
              <Form.Input
                label="Region"
                name="region"
                placeholder="us-central1"
                value={formData.region}
                onChange={handleInputChange}
                required
              />
            </Grid.Column>
          </Grid.Row>
          <Grid.Row>
            <Grid.Column>
              <Form.Input
                label="Database Schema Name"
                name="database_name"
                placeholder="my-database"
                value={formData.database_name}
                onChange={handleInputChange}
                required
              />
            </Grid.Column>
            <Grid.Column>
              <Form.Input
                label="Database Username"
                name="db_user"
                placeholder="user1"
                value={formData.db_user}
                onChange={handleInputChange}
                required
              />
            </Grid.Column>
          </Grid.Row>
          <Grid.Row>
            <Grid.Column>
              <Form.Input
                label="Database Password"
                name="db_pass"
                type="password"
                value={formData.db_pass}
                onChange={handleInputChange}
                required
              />
            </Grid.Column>
          </Grid.Row>
        </Grid>

        <Divider />
        <Header as="h3">Google Authentication Setup</Header>
        <p>
          For more information on setting up a Google Cloud OAuth 2.0 authentication, refer to the{' '}
          <a
            href="https://github.com/instadeepai/SKAInnotate?tab=readme-ov-file#google-authentication-setup"
            target="_blank"
            rel="noopener noreferrer"
          >
            Google OAuth for SKAInnotate
          </a>.
        </p>
        <Form.Input
          label="OAuth 2.0 Client ID"
          name="google_client_id"
          placeholder="123abc.apps.googleusercontent.com"
          value={formData.google_client_id}
          onChange={handleInputChange}
          required
        />

        <Divider />
        <Header as="h3">Admin Setup</Header>
        <Form.Input
          label="Username"
          name="superuser_username"
          placeholder="john"
          value={formData.superuser_username}
          onChange={handleInputChange}
          required
        />
        <Form.Input
          label="Email Address"
          name="superuser_email"
          type="email"
          placeholder="johndoe@mail.com"
          value={formData.superuser_email}
          onChange={handleInputChange}
          required
        />

        <Divider />
        <Header as="h3">Service Account Setup</Header>
        <Form.Field required>
          <label>Service Account JSON File</label>
          <input
            id="service_account_file"
            name="service_account_file"
            type="file"
            accept="application/json"
            onChange={handleFileChange}
          />
        </Form.Field>

        <Divider />
        <Header as="h3">Cloud Run Setup</Header>
        <Form.Input
          label="Service Name"
          name="service_name"
          placeholder="my-annotation-app"
          value={formData.service_name}
          onChange={handleInputChange}
          required
        />

        <Button color="blue" fluid type="submit" disabled={loading}>
          <Icon name="check circle" /> Launch
        </Button>
      </Form>
    </Segment>
  );
};

export default SetupForm;
