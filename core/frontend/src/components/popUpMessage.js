import React, { useState } from 'react';

const PopupMessage = () => {
  const [isOpen, setIsOpen] = useState(false);

  const togglePopup = () => setIsOpen(!isOpen);

  return (
    <div>
      <button onClick={togglePopup}>Toggle Popup</button>
      {isOpen && (
        <div style={{ position: 'absolute', top: '20%', left: '50%', transform: 'translate(-50%, -50%)', background: 'white', padding: '20px', zIndex: 1000, boxShadow: '0px 0px 15px rgba(0,0,0,0.5)' }}>
          <h4>Popup Message</h4>
          <p>This is a simple popup!</p>
          <button onClick={togglePopup}>Close</button>
        </div>
      )}
    </div>
  );
};

export default PopupMessage;