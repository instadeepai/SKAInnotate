import React from 'react';
import { Modal, Form, Button } from "semantic-ui-react"

const CreateProjectModal = ({newProject, onChange, onSubmit, onTaskFileChange, modalOpen, setModalOpen}) => {
  return (
  <Modal open={modalOpen} onClose={() => setModalOpen(false)}>
    <Modal.Header>{newProject.project_id ? 'Edit Project' : 'Create a New Project'}</Modal.Header>
    <Modal.Content>
      <Form>
        <Form.Input
          label="Project Title"
          name="project_title"
          value={newProject.project_title}
          onChange={onChange}
          required
        />
        <Form.TextArea
          label="Description"
          name="project_description"
          value={newProject.project_description}
          onChange={onChange}
          required
        />
        <Form.Input
          label="Max Annotators per Task"
          name="max_annotators_per_task"
          value={newProject.max_annotators_per_task}
          onChange={onChange}
          type="number"
          required
        />
        <Form.Input
          label="Completion Deadline"
          name="completion_deadline"
          value={newProject.completion_deadline}
          onChange={onChange}
          type="date"
          required
        />
        <Form.Input
          label="Labels (comma separated)"
          name="labels"
          value={newProject.labels}
          onChange={onChange}
          required
        />
        <Form.Input
          label="Task File"
          type="file"
          onChange={onTaskFileChange}
        />
      </Form>
    </Modal.Content>
    <Modal.Actions>
      <Button onClick={() => setModalOpen(false)}>Cancel</Button>
      <Button primary onClick={onSubmit}>{newProject.project_id ? 'Save' : 'Create'}</Button>
    </Modal.Actions>
  </Modal>
  )
}
export default CreateProjectModal;