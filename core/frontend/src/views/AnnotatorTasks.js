import React, { useState } from 'react';
import { Table, Image, Checkbox, Modal, Form, Button, Pagination } from 'semantic-ui-react';

const AnnotatorTasksList = ({ tasks, onRowClick, onCsvFileChange, onCsvSubmit, setCsvModalOpen, csvModalOpen }) => {
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 10;  // Adjust as needed

    // Calculate the tasks to be shown on the current page
    const indexOfLastTask = currentPage * itemsPerPage;
    const indexOfFirstTask = indexOfLastTask - itemsPerPage;
    const currentTasks = tasks.slice(indexOfFirstTask, indexOfLastTask);

    // Change page handler
    const handlePaginationChange = (e, { activePage }) => setCurrentPage(activePage);

    return (
        <div className='tasks-content'>
            <Table striped className="tasks-table">
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell>ID</Table.HeaderCell>
                        <Table.HeaderCell>Image</Table.HeaderCell>
                        <Table.HeaderCell>Completion Status</Table.HeaderCell>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {currentTasks.map(task => (
                        <Table.Row key={task.task_id} onClick={() => onRowClick(task.task_id)} style={{ cursor: 'pointer' }}>
                            <Table.Cell>{task.task_id}</Table.Cell>
                            <Table.Cell>
                                <Image src={task.image_url} size="small" />
                            </Table.Cell>
                            <Table.Cell>
                                <Checkbox checked={task.completion_status} readOnly />
                            </Table.Cell>
                        </Table.Row>
                    ))}
                </Table.Body>
            </Table>

            <Pagination
                activePage={currentPage}
                totalPages={Math.ceil(tasks.length / itemsPerPage)}
                onPageChange={handlePaginationChange}
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

export default AnnotatorTasksList;

// import { Table, Image, Checkbox, Modal, Form, Button } from "semantic-ui-react";

// export const AnnotatorTasksList = ({tasks, onRowClick, onCsvFileChange, onCsvSubmit, setCsvModalOpen, csvModalOpen}) => {
//     return (
//     <div className='tasks-content'>
//         <Table celled className="tasks-table">
//         <Table.Header>
//             <Table.Row>
//             <Table.HeaderCell>ID</Table.HeaderCell>
//             <Table.HeaderCell>Image</Table.HeaderCell>
//             <Table.HeaderCell>Completion Status</Table.HeaderCell>
//             </Table.Row>
//         </Table.Header>
//         <Table.Body>
//             {tasks.map(task => (
//             <Table.Row key={task.task_id} onClick={() => onRowClick(task.task_id)} style={{ cursor: 'pointer' }}>
//                 <Table.Cell>{task.task_id}</Table.Cell>
//                 <Table.Cell>
//                 <Image src={task.image_url} size="small" />
//                 </Table.Cell>
//                 <Table.Cell>
//                 <Checkbox checked={task.completion_status} readOnly />
//                 </Table.Cell>
//             </Table.Row>
//             ))}
//         </Table.Body>
//         </Table>

//         <Modal open={csvModalOpen} onClose={() => setCsvModalOpen(false)}>
//         <Modal.Header>Update Tasks from CSV</Modal.Header>
//         <Modal.Content>
//             <Form>
//             <Form.Input
//                 label="CSV File"
//                 type="file"
//                 accept=".csv"
//                 onChange={onCsvFileChange}
//             />
//             </Form>
//         </Modal.Content>
//         <Modal.Actions>
//             <Button onClick={() => setCsvModalOpen(false)}>Cancel</Button>
//             <Button primary onClick={onCsvSubmit}>Update</Button>
//         </Modal.Actions>
//         </Modal>
//     </div>
//     );
// };

// export default AnnotatorTasksList