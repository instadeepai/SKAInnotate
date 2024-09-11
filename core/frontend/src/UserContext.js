import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

export const UserContext = createContext({
  user: null,
  setUser: () => {},
  role: 'select role',
  setRole: () => {},
  logout: () => {}
});

export const UserProvider = ({ children }) => {

  const [user, setUser] = useState(() => {
    try {
      const savedUserInfo = sessionStorage.getItem('userInfo');
      return savedUserInfo ? JSON.parse(savedUserInfo) : null;
    } catch (err) {
      console.error('Failed to retrieve user info from sessionStorage:', err);
      return null;
    }
  });

  const [role, setRole] = useState(() => sessionStorage.getItem('userRole') || 'select role');

  useEffect(() => {
    try {
      if (user) {
        sessionStorage.setItem('userInfo', JSON.stringify(user));
      } else {
        sessionStorage.removeItem('userInfo');
      }
    } catch (err) {
      console.error('Failed to set user info in sessionStorage:', err);
    }
  }, [user]);

  useEffect(() => {
    try {
      sessionStorage.setItem('userRole', role);
    } catch (err) {
      console.error('Failed to set user role in sessionStorage:', err);
    }
  }, [role]);

  const handleSetUser = useCallback((user) => {
    setUser(user);
  }, []);

  const handleSetRole = useCallback((role) => {
    setRole(role);
    sessionStorage.setItem('userRole', role);
  }, []);

  const logout = () => {
    setUser(null);
    setRole('select role');
  };

  return (
    <UserContext.Provider value={{ user, setUser: handleSetUser, role, setRole: handleSetRole, logout }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => useContext(UserContext);