import React, { useState } from 'react';
import { ContextualHelpBasic } from '../components';

const BasicHelpExample = () => {
  const [showHelp, setShowHelp] = useState(false);

  const sampleContent =
    'This is a simplified tooltip with minimal styling. It uses inline styles instead of external CSS.';

  const buttonStyle = {
    padding: '10px 15px',
    backgroundColor: '#333',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    margin: '10px',
    cursor: 'pointer',
  };

  const containerStyle = {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  };

  return (
    <div style={containerStyle}>
      <h1>ContextualHelpBasic Demo</h1>

      <h2>Hover Example</h2>
      <div>
        <span id="hover-target" style={{ fontWeight: 'bold' }}>
          Hover over me!
        </span>
        <ContextualHelpBasic
          targetId="hover-target"
          content="This tooltip appears on hover"
          title="Hover Tooltip"
          position="top"
          trigger="hover"
        />
      </div>

      <h2>Click Example</h2>
      <div>
        <button id="click-target" style={buttonStyle}>
          Click for Help
        </button>
        <ContextualHelpBasic
          targetId="click-target"
          content="This tooltip appears when you click the button"
          title="Click Tooltip"
          position="right"
          trigger="click"
        />
      </div>

      <h2>Manual Control Example</h2>
      <div>
        <button
          id="manual-target"
          style={buttonStyle}
          onClick={() => setShowHelp(!showHelp)}
        >
          {showHelp ? 'Hide Help' : 'Show Help'}
        </button>
        <ContextualHelpBasic
          targetId="manual-target"
          content="This tooltip is manually controlled through state"
          title="Manual Control"
          position="bottom"
          trigger="manual"
          isOpen={showHelp}
          onClose={() => setShowHelp(false)}
        />
      </div>
    </div>
  );
};

export default BasicHelpExample;
