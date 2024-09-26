import React, { useState } from 'react';
import '../SetupForm.css';
import { setProject, createSQLInstance, deployApp } from '../services/api';
import { Segment, Button, Form, Message, Header, Divider, Grid, Icon } from 'semantic-ui-react';
import 'semantic-ui-css/semantic.min.css';

const SetupForm = () => {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  // Reusable input field component
  const InputField = ({ label, id, type = 'text', required = true, placeholder = '' }) => (
    <Form.Field required={required}>
      <label>{label}</label>
      <input type={type} id={id} name={id} placeholder = {placeholder}/>
    </Form.Field>
  );

  // Form submission handler
  const setupInfrastructure = async (event) => {
    event.preventDefault();
    setLoading(true);
    setSuccess(false);
    setMessage(''); 

    const formData = new FormData(event.target);
    const formValues = Object.fromEntries(formData.entries());

try {
  setMessage('Application launch in progress...');

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
  });

  // Check if 'service_name' is provided in the response
  if (deployResponse && deployResponse.service_url) {
    const service_url = deployResponse.service_url;
    setMessage(`App launched successfully at ${service_url}!`);
    setSuccess(true);
  } else {
    setMessage("Application unable to launch");
  }
  } catch (error) {
  setMessage(`Error launching application: ${error.message}`);
  } finally {
  setLoading(false);
  }
}


  return (
    <Segment padded="very" className="setup-segment">
      <Header as="h2" textAlign="center">
        <Icon name="rocket" />
          Let's Launch Your SKAInnotate Journey!
      </Header>

      <Form id="setup-form" onSubmit={setupInfrastructure} loading={loading} success={success}>
        
        <Header as="h3">Project Setup</Header>
        <InputField label="Project ID" id="project_id" placeholder="my-project-1"/>

        <Divider />

        <Header as="h3">Cloud SQL Setup</Header>
        <p>
          For detailed instructions on setting up a Google Cloud SQL instance, please refer to the 
          <a href="https://github.com/instadeepai/SKAInnotate?tab=readme-ov-file#database-setup" target="_blank" rel="noopener noreferrer"> Google SQL setup for SKAInnotate</a>.
        </p>
        <Grid columns={2} stackable>
          <Grid.Row>
            <Grid.Column>
              <InputField label="Instance Name" id="instance_name" className="field-margin" placeholder="my-db-instance"/>
            </Grid.Column>
            <Grid.Column>
              <InputField label="Region" id="region" className="field-margin" placeholder="us-central1"/>
            </Grid.Column>
          </Grid.Row>
          <Grid.Row>
            <Grid.Column>
              <InputField label="Database Schema Name" id="database_name" placeholder="my-database"/>
            </Grid.Column>
            <Grid.Column>
              <InputField label="Database Username" id="db_user"  placeholder="user1"/>
            </Grid.Column>
          </Grid.Row>
          <Grid.Row>
            <Grid.Column>
              <InputField label="Database Password" id="db_pass" type="password"/>
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
        <InputField label="Username" id="superuser_username" placeholder="john"/>
        <InputField label="Email Address" id="superuser_email" type="email" placeholder="johndoe@mail.com"/>

        <Divider />

        <Header as="h3">Cloud Run Setup</Header>
        <InputField label="Service Name" id="service_name" placeholder="my-annotation-app"/>

        <Button color="blue" fluid type="submit">
          <Icon name="check circle" /> Launch
        </Button>
      </Form>

      {message && (
        <Message
          success={success}
          error={!success}
          content={message}
          style={{ marginTop: '20px' }}
        />
      )}
    </Segment>
  );
};

export default SetupForm;
