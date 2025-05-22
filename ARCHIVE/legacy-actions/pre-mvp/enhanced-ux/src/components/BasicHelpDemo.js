import React from 'react';
import ContextualHelp from './ContextualHelp';

const BasicHelpDemo = () => {
  const containerStyle = {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  };

  const sectionStyle = {
    marginBottom: '30px',
    padding: '15px',
    border: '1px solid #ddd',
    borderRadius: '5px',
  };

  const buttonStyle = {
    padding: '8px 15px',
    backgroundColor: '#4a90e2',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    margin: '5px',
  };

  const headingStyle = {
    borderBottom: '1px solid #eee',
    paddingBottom: '10px',
    marginTop: '0',
  };

  const inputStyle = {
    padding: '8px',
    borderRadius: '4px',
    border: '1px solid #ccc',
    marginRight: '10px',
  };

  return (
    <div style={containerStyle}>
      <h1 style={headingStyle}>ContextualHelp Demo</h1>

      <div style={sectionStyle}>
        <h2 style={headingStyle}>Tooltip Examples</h2>
        <p>Hover over these elements to see tooltips:</p>

        <ContextualHelp
          type="tooltip"
          position="top"
          content="This is a simple top tooltip"
        >
          <button style={buttonStyle}>Top Tooltip</button>
        </ContextualHelp>

        <ContextualHelp
          type="tooltip"
          position="bottom"
          title="Bottom Tooltip"
          content="This is a tooltip with a title that appears below the element"
        >
          <button style={buttonStyle}>Bottom Tooltip with Title</button>
        </ContextualHelp>

        <ContextualHelp
          type="tooltip"
          position="left"
          content="This appears to the left"
        >
          <button style={buttonStyle}>Left Tooltip</button>
        </ContextualHelp>

        <ContextualHelp
          type="tooltip"
          position="right"
          content="This appears to the right"
        >
          <button style={buttonStyle}>Right Tooltip</button>
        </ContextualHelp>
      </div>

      <div style={sectionStyle}>
        <h2 style={headingStyle}>Popover Examples</h2>
        <p>Click on these elements to toggle popovers:</p>

        <ContextualHelp
          type="popover"
          position="top"
          title="Important Information"
          content="This is a popover with more detailed information. It stays open until you click elsewhere."
        >
          <button style={buttonStyle}>Show Top Popover</button>
        </ContextualHelp>

        <ContextualHelp
          type="popover"
          position="bottom"
          title="Help"
          content="Click elsewhere on the page to close this popover."
        >
          <button style={buttonStyle}>Show Bottom Popover</button>
        </ContextualHelp>
      </div>

      <div style={sectionStyle}>
        <h2 style={headingStyle}>Form Field Hints</h2>
        <p>Hover over inputs to see hints:</p>

        <div>
          <label>Username: </label>
          <ContextualHelp
            type="hint"
            position="right"
            content="Enter a username that is 5-20 characters long"
          >
            <input style={inputStyle} type="text" placeholder="Username" />
          </ContextualHelp>
        </div>
        <br />
        <div>
          <label>Password: </label>
          <ContextualHelp
            type="hint"
            position="right"
            content="Password must contain at least 8 characters with numbers and symbols"
          >
            <input style={inputStyle} type="password" placeholder="Password" />
          </ContextualHelp>
        </div>
      </div>
    </div>
  );
};

export default BasicHelpDemo;
