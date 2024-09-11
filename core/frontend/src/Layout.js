import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header'; // Assume Header component is already created
import { useUser } from './UserContext'; // Assume useUser is a hook that provides user info

const Layout = () => {
  const { user } = useUser();

  return (
    <>
      {user && <Header />}
      <div className="content">
        <Outlet /> {/* This will render the matched child route components */}
      </div>
    </>
  );
};

export default Layout;
