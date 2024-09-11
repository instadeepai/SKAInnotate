import { List } from 'semantic-ui-react'

const TaskList = ({ tasks, onSelectTask, filter }) => {
  const filteredTasks = tasks.filter(task => {
    if (filter === 'labeled') return task.label;
    if (filter === 'unlabeled') return !task.label;
    return true;
  });

  return (
    <List>
      {filteredTasks.map(task => (
        <List.Item key={task.task_id} onClick={() => onSelectTask(task.task_id)} style={{ cursor: 'pointer' }}>
          Task ID: {task.task_id}
        </List.Item>
      ))}
    </List>
  );
};

export default TaskList;
