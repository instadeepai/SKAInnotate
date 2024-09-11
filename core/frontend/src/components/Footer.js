import React, { useState, useEffect } from 'react';
import { useFooter } from '../context/FooterContext'; // Import the custom hook
import '../assets/styles/Footer.css';

const Footer = () => {
  const { logsMessage, setLogsMessage } = useFooter(); // Use the context
  const [isToggled, setIsToggled] = useState(false);
  const [showLogs, setShowLogs] = useState(false);

  const handleToggle = () => {
    setIsToggled(!isToggled);
    setShowLogs(true);
  };

  useEffect(() => {
    if (showLogs) {
      const timer = setTimeout(() => {
        setShowLogs(false);
      }, 7000); 

      return () => clearTimeout(timer);
    }
  }, [showLogs]);

  return (
    <div className="footer">
      <p>&copy; 2024 SKAInnotate. All rights reserved.</p>
     
      {/* {isToggled && showLogs && (
        <div className="activity-info">{logsMessage}</div>
      )}
      <button className="toggle-button" onClick={handleToggle}>
        {isToggled ? 'show logs: On' : 'show logs: Off'}
      </button> */}
    </div>
  );
};

export default Footer;
