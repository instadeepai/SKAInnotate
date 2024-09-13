import React from 'react';
import {Grid, Card, Dropdown} from 'semantic-ui-react';

const ProjectCard = ({projects, onProjectClick, onEditClick, onDelete}) => {

  if (!projects || projects.length === 0) {
    return <div>No projects available.</div>;
  }

  return (
    <Grid container stackable columns={4} className="projects-container">
      {projects.map(project => (
        <Grid.Column key={project.project_id} onClick={() => onProjectClick(project.project_id)}>
          <Card
            header={`Title: ${project.project_title}`}
            meta={`Project ID: ${project.project_id}`}
            description={`Description: ${project.project_description}`}
            extra={
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>Created on: {new Date(project.created_at).toLocaleDateString()}</span>
                <Dropdown icon="ellipsis horizontal" pointing="top right">
                  <Dropdown.Menu>
                    <Dropdown.Item text='Edit' onClick={() => onEditClick(project)} />
                    <Dropdown.Item text='Delete' onClick={() => onDelete(project.project_id)} />
                  </Dropdown.Menu>
                </Dropdown>
              </div>
            }
            className="project-card"
          />
        </Grid.Column>
      ))}
      </Grid>
  );
}

export default ProjectCard;