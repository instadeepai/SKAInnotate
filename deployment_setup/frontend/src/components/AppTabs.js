import React from 'react';
import { TabPane, MenuItem, Label, Tab } from 'semantic-ui-react';
import SetupForm from './SetupForm'; // Import your SetupForm component
import PastDeployments from './PastDeployments'
import '../AppTabs.css'
// Placeholder component for Past Deployments

const panes = [
  {
    menuItem: { key: 'setup', icon: 'rocket', content: 'New Setup' },
    render: () => (
      <TabPane className="tab-pane">
        <SetupForm />
      </TabPane>
    ),
  },
  {
    menuItem: { key: 'deployments', icon: 'history', content: 'Past Deployments' },
    render: () => (
    <TabPane className="tab-pane">
        <PastDeployments />
    </TabPane>
    ),
  },
];

const AppTabs = () => <Tab panes={panes} />;

export default AppTabs;
