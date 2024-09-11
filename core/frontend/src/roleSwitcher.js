import React, { useContext } from 'react';
import { UserContext } from './UserContext';

const RoleSwitcher = () => {
  const { setRole } = useContext(UserContext);

  const handleRoleChange = (newRole) => {
    setRole(newRole);
  };

  return (
    <div>
      <button onClick={() => handleRoleChange('admin')}>Switch to Admin</button>
      <button onClick={() => handleRoleChange('annotator')}>Switch to Annotator</button>
      <button onClick={() => handleRoleChange('reviewer')}>Switch to Reviewer</button>
    </div>
  );
};

export default RoleSwitcher;
