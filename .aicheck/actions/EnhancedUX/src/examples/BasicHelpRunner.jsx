import React from 'react';
import ReactDOM from 'react-dom';
import BasicHelpDemo from './BasicHelpDemo';

/**
 * Simple runner for the BasicHelpDemo
 */
const BasicHelpRunner = () => {
  return (
    <div>
      <BasicHelpDemo />
    </div>
  );
};

// Render the demo when this script is loaded
const rootElement = document.getElementById('root');
if (rootElement) {
  ReactDOM.render(<BasicHelpRunner />, rootElement);
}

export default BasicHelpRunner;
