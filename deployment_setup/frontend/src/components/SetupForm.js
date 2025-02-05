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
  Icon
} from 'semantic-ui-react';
import 'semantic-ui-css/semantic.min.css';

const SetupForm = () => {
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [serviceAccountFile, setServiceAccountFile] = useState(null);  // Store the selected service account file

  const InputField = ({ label, id, type = 'text', required = true, placeholder = '' }) => (
    <Form.Field required={required}>
      <label>{label}</label>
      <input type={type} id={id} name={id} placeholder={placeholder} />
    </Form.Field>
  );

  const handleFileChange = (event) => {
    event.preventDefault();
    const file = event.target.files[0];
    if (file && file.type === 'application/json' && file.name.endsWith('.json')) {
      setServiceAccountFile(file);
    } else {
      alertify.error('Please upload a valid JSON file for the service account.');
    }
  };

  const validateForm = (formValues) => {
    for (const key in formValues) {
      if (!formValues[key]) {
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

  const setupInfrastructure = async (event) => {
    console.log("Setup infra started!");
    event.preventDefault();

    if (loading) return;
    setLoading(true);
    setSuccess(false);

    const formData = new FormData(event.target);
    if (serviceAccountFile) {
      formData.append('service_account_file', serviceAccountFile);
    }
    const formValues = Object.fromEntries(formData.entries());

    // Validate form fields
    console.log("Service account file: ", formValues.service_account_file);
    console.log("Validating fields");
    if (!validateForm(formValues)) {
      setLoading(false);
      return;
    }

    console.log("Fields validation complete!");
    let service_url = '';
    let deployment_status = '';

    try {
      alertify.success('Application launch in progress...');

      const deployResponse = await deployApp({
        project_id: formValues.project_id,
        instance_name: formValues.instance_name,
        region: formValues.region,
        db_name: formValues.database_name,
        db_user: formValues.db_user,
        db_pass: formValues.db_pass,
        clientId: formValues.google_client_id,
        service_name: formValues.service_name,
        superuser_email: formValues.superuser_email,
        superuser_username: formValues.superuser_username,
        service_account_file: formValues.service_account_file,
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
          project_id: formValues.project_id,
          instance_name: formValues.instance_name,
          service_name: formValues.service_name,
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

      {/* <Form id="setup-form" onSubmit={setupInfrastructure} method="POST" encType="multipart/form-data" loading={loading} success={success}> */}
      <Form 
        id="setup-form" 
        onSubmit={setupInfrastructure} 
        method="POST" 
        encType="multipart/form-data" 
        loading={loading} 
        success={success}
        >
        <Header as="h3">Project Setup</Header>
        <InputField label="Project ID" id="project_id" placeholder="my-project-1" />

        <Divider />
        <Header as="h3">Cloud SQL Setup</Header>
        <p>
          For detailed instructions on setting up a Google Cloud SQL instance, please refer to the
          <a
            href="https://github.com/instadeepai/SKAInnotate?tab=readme-ov-file#database-setup"
            target="_blank"
            rel="noopener noreferrer"
          >
            &nbsp;Google SQL setup for SKAInnotate
          </a>.
        </p>
        <Grid columns={2} stackable>
          <Grid.Row>
            <Grid.Column>
              <InputField
                label="Instance Name"
                id="instance_name"
                className="field-margin"
                placeholder="my-db-instance"
              />
            </Grid.Column>
            <Grid.Column>
              <InputField
                label="Region"
                id="region"
                className="field-margin"
                placeholder="us-central1"
              />
            </Grid.Column>
          </Grid.Row>
          <Grid.Row>
            <Grid.Column>
              <InputField
                label="Database Schema Name"
                id="database_name"
                placeholder="my-database"
              />
            </Grid.Column>
            <Grid.Column>
              <InputField label="Database Username" id="db_user" placeholder="user1" />
            </Grid.Column>
          </Grid.Row>
          <Grid.Row>
            <Grid.Column>
              <InputField label="Database Password" id="db_pass" type="password" />
            </Grid.Column>
          </Grid.Row>
        </Grid>
        <Divider />
        <Header as="h3">Google Authentication Setup</Header>
          <p>
            For more information on setting up a Google Cloud OAuth 2.0 authentication, refer to the 
            <a href="https://github.com/instadeepai/SKAInnotate?tab=readme-ov-file#google-authentication-setup" 
              target="_blank" rel="noopener noreferrer"> Google OAuth for SKAInnotate</a>.
          </p>
        <InputField label="OAuth 2.0 Client ID" id="google_client_id" placeholder="123abc.apps.googleusercontent.com"/>
        <Divider />
        
        <Header as="h3">Admin Setup</Header>
        <InputField label="Username" id="superuser_username" placeholder="john" />
        <InputField
          label="Email Address"
          id="superuser_email"
          type="email"
          placeholder="johndoe@mail.com"
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
        <InputField label="Service Name" id="service_name" placeholder="my-annotation-app" />

        <Button color="blue" fluid type="submit" disabled={loading}>
          <Icon name="check circle" /> Launch
        </Button>
      </Form>
    </Segment>
  );
};

export default SetupForm;