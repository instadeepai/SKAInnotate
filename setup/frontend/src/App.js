import React, { useState } from 'react';
import './App.css';
import SetupForm from './components/SetupForm'; // Import the SetupForm component
import 'semantic-ui-css/semantic.min.css';

function App() {
  return (
    <div className="App">
      <SetupForm />
    </div>
  );
}

export default App;
