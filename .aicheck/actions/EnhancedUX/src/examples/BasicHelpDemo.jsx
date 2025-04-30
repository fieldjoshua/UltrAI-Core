import React, { useState } from 'react';
import ContextualHelpBasic from '../components/ContextualHelp.basic';

/**
 * A simple demo component that shows how to use the basic version of ContextualHelp
 */
const BasicHelpDemo = () => {
  const [manualTooltipOpen, setManualTooltipOpen] = useState(false);

  const containerStyle = {
    fontFamily: 'Arial, sans-serif',
    maxWidth: '800px',
    margin: '0 auto',
    padding: '20px',
    backgroundColor: '#f5f5f5',
    borderRadius: '5px',
  };

  const sectionStyle = {
    marginBottom: '30px',
    padding: '15px',
    backgroundColor: '#fff',
    borderRadius: '4px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  };

  const buttonStyle = {
    backgroundColor: '#4a90e2',
    color: 'white',
    border: 'none',
    padding: '8px 15px',
    borderRadius: '4px',
    cursor: 'pointer',
    margin: '5px',
  };

  const headingStyle = {
    borderBottom: '1px solid #eee',
    paddingBottom: '10px',
    marginTop: '0',
  };

  return (
    <div style={containerStyle}>
      <h1 style={{ textAlign: 'center' }}>Contextual Help Demo</h1>

      <div style={sectionStyle}>
        <h2 style={headingStyle}>Tooltips</h2>
        <p>Hover over these elements to see tooltips:</p>

        <ContextualHelp
          type="tooltip"
          position="top"
          content="This tooltip appears above the button"
        >
          <button style={buttonStyle}>Tooltip (Top)</button>
        </ContextualHelp>

        <ContextualHelp
          type="tooltip"
          position="bottom"
          content="This tooltip appears below the button"
        >
          <button style={buttonStyle}>Tooltip (Bottom)</button>
        </ContextualHelp>

        <ContextualHelp
          type="tooltip"
          position="left"
          content="This tooltip appears to the left of the button"
        >
          <button style={buttonStyle}>Tooltip (Left)</button>
        </ContextualHelp>

        <ContextualHelp
          type="tooltip"
          position="right"
          content="This tooltip appears to the right of the button"
        >
          <button style={buttonStyle}>Tooltip (Right)</button>
        </ContextualHelp>
      </div>

      <div style={sectionStyle}>
        <h2 style={headingStyle}>Popovers</h2>
        <p>Click these buttons to toggle popovers:</p>

        <ContextualHelp
          type="popover"
          position="top"
          title="Important Information"
          content="This is a popover with a title. It contains more detailed information and stays open until you click the button again or click elsewhere."
        >
          <button style={buttonStyle}>Popover with Title</button>
        </ContextualHelp>

        <ContextualHelp
          type="popover"
          position="bottom"
          content="This is a simple popover without a title. Click the button again to close it."
        >
          <button style={buttonStyle}>Simple Popover</button>
        </ContextualHelp>
      </div>

      <div style={sectionStyle}>
        <h2 style={headingStyle}>Hints</h2>
        <p>Hover over these items to see hints:</p>

        <div style={{ display: 'flex', justifyContent: 'space-around' }}>
          <ContextualHelp
            type="hint"
            position="bottom"
            content="This field is required"
          >
            <input
              type="text"
              placeholder="Username (required)"
              style={{ padding: '8px' }}
            />
          </ContextualHelp>

          <ContextualHelp
            type="hint"
            position="bottom"
            content="Password must be at least 8 characters"
          >
            <input
              type="password"
              placeholder="Password"
              style={{ padding: '8px' }}
            />
          </ContextualHelp>
        </div>
      </div>
    </div>
  );
};

// Export for use in other files
window.BasicHelpDemo = BasicHelpDemo;
