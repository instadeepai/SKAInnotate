import React, { useState, useEffect } from 'react';
import { Table, Icon, Image, Modal, Form, Button, Popup, Dropdown, Pagination } from 'semantic-ui-react';
import { fetchAssignedUsers } from '../services/api';

const AdminTasksList = ({
  currentPage,
  onPaginationChange,
  currentItems,
  totalPages,
  onCsvFileChange,
  onCsvSubmit,
  setCsvModalOpen,
  csvModalOpen,
  onAssignToReviewer,
  onDelete,
  reviewers
}) => {
  const [tasksWithUsers, setTasksWithUsers] = useState([]);

  useEffect(() => {
    const fetchTaskUsers = async () => {
      try {
        // Fetch data for each task
        const tasksWithUsersPromises = currentItems.map(async (task) => {
          const { data } = await fetchAssignedUsers(task.task_id);
          return { ...task, ...data };
        });

        const tasksWithUsers = await Promise.all(tasksWithUsersPromises);
        setTasksWithUsers(tasksWithUsers);
      } catch (error) {
        console.error("Error fetching task users:", error);
      }
    };

    fetchTaskUsers();
  }, [currentItems]);

  const getMajorityLabel = (annotations) => {
    const count = annotations.reduce((acc, label) => {
      acc[label] = (acc[label] || 0) + 1;
      return acc;
    }, {});

    const counts = Object.values(count);
    const maxCount = Math.max(...counts);
    const majorityLabels = Object.keys(count).filter(label => count[label] === maxCount);

    return majorityLabels.length === 1 ? majorityLabels[0] : "";
  };

  const getReviewerCount = (task) => {
    return task.assigned_reviewers ? task.assigned_reviewers.length : 0;
  };

  const getAnnotatorCount = (task) => {
    return task.assigned_annotators ? task.assigned_annotators.length : 0;
  };

  const getActiveReviewerId = (task) => {
    return task.assigned_reviewers[0]?.user_id || null;
  };

  const FinalAnnotationCell = ({ annotations, reviews }) => {
    const majorityLabel = getMajorityLabel(annotations);
    const finalLabel = reviews.length > 0 ? reviews[0] : majorityLabel;

    return <div>{finalLabel}</div>;
  };

  return (
    <div className='tasks-content'>
      <Table striped className="tasks-table">
        <Table.Header>
          <Table.Row>
            <Table.HeaderCell>ID</Table.HeaderCell>
            <Table.HeaderCell>Image</Table.HeaderCell>
            <Table.HeaderCell>
              Assignments
              <Popup
                trigger={<Icon name='info circle' style={{ marginLeft: '5px' }} />}
                content="Count of users assigned to task (Annotators, Reviewers)"
                position='top center'
                size='small'
                inverted
              />
            </Table.HeaderCell>
            <Table.HeaderCell>Annotations</Table.HeaderCell>
            <Table.HeaderCell>Reviews</Table.HeaderCell>
            <Table.HeaderCell>
              Final Annotation
              <Popup
                trigger={<Icon name='info circle' style={{ marginLeft: '5px' }} />}
                content="This column shows the majority agreed annotation or reviewer's annotation"
                position='top center'
                size='small'
                inverted
              />
            </Table.HeaderCell>
            <Table.HeaderCell>Review Actions</Table.HeaderCell>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {tasksWithUsers.map(task => (
            <Table.Row key={task.task_id}>
              <Table.Cell>{task.task_id}</Table.Cell>
              <Table.Cell>
                <Image src={task.image_url} size="small" />
              </Table.Cell>
              <Table.Cell>
                {getAnnotatorCount(task)}, {getReviewerCount(task)}
              </Table.Cell>
              <Table.Cell>
                {task.annotations?.map((annotation, index) => (
                  <div key={index}>{annotation}</div>
                ))}
              </Table.Cell>
              <Table.Cell>
                {task.reviews?.map((review, index) => (
                  <div key={index}>{review}</div>
                ))}
              </Table.Cell>
              <Table.Cell>
                <FinalAnnotationCell
                  annotations={task.annotations || []}
                  reviews={task.reviews || []}
                />
              </Table.Cell>
              <Table.Cell>
                <Popup
                  content='Assign reviewer'
                  trigger={
                    <Dropdown
                      header='Select Reviewer'
                      icon='add'
                      button
                      className='icon'
                    >
                      <Dropdown.Menu>
                        <Dropdown.Header content='Select Reviewer' />
                        {reviewers.map(option => (
                          <Dropdown.Item
                            key={option.value}
                            text={option.text}
                            value={option.value}
                            selected={option.key === getActiveReviewerId(task)}
                            onClick={() => onAssignToReviewer(task, option.value)}
                          />
                        ))}
                          <Dropdown.Item
                            key="none"
                            text="None"
                            value=""
                            onClick={() => onAssignToReviewer(task, null)}
                        />
                      </Dropdown.Menu>
                    </Dropdown>
                  }
                  size='small'
                  inverted
                />

                <Popup
                  content='Delete task'
                  trigger={<Button icon='trash' onClick={() => onDelete(task)} />}
                  size='small'
                  inverted
                />
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table>

      <Pagination
        activePage={currentPage}
        onPageChange={onPaginationChange}
        totalPages={totalPages}
        ellipsisItem={null}
        firstItem={null}
        lastItem={null}
        siblingRange={1}
        boundaryRange={0}
      />

      <Modal open={csvModalOpen} onClose={() => setCsvModalOpen(false)}>
        <Modal.Header>Update Tasks from CSV</Modal.Header>
        <Modal.Content>
          <Form>
            <Form.Input
              label="CSV File"
              type="file"
              accept=".csv"
              onChange={onCsvFileChange}
            />
          </Form>
        </Modal.Content>
        <Modal.Actions>
          <Button onClick={() => setCsvModalOpen(false)}>Cancel</Button>
          <Button primary onClick={onCsvSubmit}>Update</Button>
        </Modal.Actions>
      </Modal>
    </div>
  );
};

export default AdminTasksList;