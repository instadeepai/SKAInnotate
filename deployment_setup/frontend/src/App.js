import './App.css';
import AppTabs from './components/AppTabs';
import { Divider } from 'semantic-ui-react';

import 'semantic-ui-css/semantic.min.css';

function App() {
  return (
    <div className="App">
      <h1>SKAInnotate Dashboard</h1>
      <Divider />
        <div className='tab-container'>
          <AppTabs />
        </div>
    </div>
  );
}

export default App;
