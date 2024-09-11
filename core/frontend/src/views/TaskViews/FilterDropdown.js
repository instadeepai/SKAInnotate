import React from 'react';
import { Dropdown } from 'semantic-ui-react';

const FilterDropdown = ({ role, filter, onFilterChange }) => {
  let options = [];

  if (role === 'annotator') {
    options = [
      { key: 'all', text: 'All', value: 'all' },
      { key: 'labeled', text: 'Labeled', value: 'labeled' },
      { key: 'unlabeled', text: 'Unlabeled', value: 'unlabeled' },
    ];
  } else if (role === 'reviewer') {
    options = [
      { key: 'all', text: 'All', value: 'all' },
      { key: 'reviewed', text: 'Reviewed', value: 'reviewed' },
      { key: 'unreviewed', text: 'Unreviewed', value: 'unreviewed' },
    ];
  } else {
    options = [
      { key: 'all', text: 'All', value: 'all' },
      { key: 'completed', text: 'Completed', value: 'completed' },
      { key: 'uncompleted', text: 'Uncompleted', value: 'completed' },
    ];
  }

  return (
    <div className="filter-dropdown">
      <span className="filter-text">Filter Tasks</span>
      <Dropdown
        placeholder="Filter Tasks"
        selection
        options={options}
        value={filter}
        onChange={onFilterChange}
      />
    </div>
  );
};

export default FilterDropdown;
