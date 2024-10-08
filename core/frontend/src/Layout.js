import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import { useUser } from './UserContext';

const Layout = () => {
  const { user } = useUser();

  return (
    <>
      {user && <Header />}
      <div className="content">
        <Outlet /> {/* render the matched child route components */}
      </div>
    </>
  );
};

export default Layout;
