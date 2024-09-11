import React, { createContext, useContext, useState } from 'react';

const FooterContext = createContext();
export const FooterProvider = ({ children }) => {
  const [logsMessage, setLogsMessage] = useState("");

  return (
    <FooterContext.Provider value={{ logsMessage, setLogsMessage }}>
      {children}
    </FooterContext.Provider>
  );
};
export const useFooter = () => useContext(FooterContext);