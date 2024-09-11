import { Button } from "semantic-ui-react";

const NavigationButtons = ({ onPrevious, onNext, disablePrevious, disableNext }) => (
  <div className="navigation-buttons">
    <Button onClick={onPrevious} disabled={disablePrevious}>Previous</Button>
    <Button onClick={onNext} disabled={disableNext}>Next</Button>
  </div>
);
export default NavigationButtons;