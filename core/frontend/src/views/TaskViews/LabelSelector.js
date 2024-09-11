import React from 'react';
import { Radio } from 'semantic-ui-react';

const LabelSelector = ({
  labelOptionsTitle,
  labelOptions,
  currentLabel,
  onLabelChange,
  agreementScores = {} // Default to an empty object if not provided
}) => (
  <div className="label-options">
    <h3>{labelOptionsTitle}</h3>
    <div className="labels-container">
      {labelOptions.map(option => {
        // Get the score from agreementScores or default to 0 if not found
        const score = agreementScores[option.text] || 0.00;
        // Show the score in the label only if it's greater than 0
        const label = score > 0
          ? `${option.text} (${score})`
          : option.text;

        return (
          <Radio
            key={option.value}
            label={label}
            value={option.value}
            checked={currentLabel === option.value}
            onChange={(e, { value }) => onLabelChange(e, { value })}
          />
        );
      })}
    </div>
  </div>
);

export default LabelSelector;
