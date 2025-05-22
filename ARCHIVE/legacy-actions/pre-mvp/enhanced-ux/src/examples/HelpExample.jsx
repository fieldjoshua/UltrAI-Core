import React, { useState } from 'react';
import ContextualHelp from '../components/ContextualHelp';
import '../components/ContextualHelp.css';
import './HelpExample.css';

/**
 * HelpExample Component
 *
 * Demonstrates the ContextualHelp component with different variants and configurations.
 */
const HelpExample = () => {
  const [showHint, setShowHint] = useState(false);
  const [showPopover, setShowPopover] = useState(false);

  return (
    <div className="help-example-container">
      <header className="help-example-header">
        <h1>Contextual Help System</h1>
        <p>
          Hover over elements or click the buttons to see different help types
        </p>
      </header>

      <div className="help-example-content">
        {/* Tooltip Examples */}
        <section className="help-demo-section">
          <h2>Tooltip Examples</h2>
          <div className="help-demo-items">
            <div id="basic-tooltip" className="help-demo-item">
              Basic Tooltip
            </div>
            <div id="tooltip-with-title" className="help-demo-item">
              Tooltip with Title
            </div>
            <div id="tooltip-with-position" className="help-demo-item">
              Positioned Tooltip
            </div>
            <div id="auto-dismiss-tooltip" className="help-demo-item">
              Auto-dismiss Tooltip
            </div>
          </div>

          {/* Basic tooltip */}
          <ContextualHelp
            targetId="basic-tooltip"
            content="This is a simple tooltip that appears on hover."
            trigger="hover"
            type="tooltip"
          />

          {/* Tooltip with title */}
          <ContextualHelp
            targetId="tooltip-with-title"
            title="INFORMATION"
            content="This tooltip includes a title section for more context."
            trigger="hover"
            type="tooltip"
          />

          {/* Positioned tooltip */}
          <ContextualHelp
            targetId="tooltip-with-position"
            content="This tooltip is positioned on the right side of the element."
            position="right"
            trigger="hover"
            type="tooltip"
          />

          {/* Auto-dismiss tooltip */}
          <ContextualHelp
            targetId="auto-dismiss-tooltip"
            content="This tooltip will automatically dismiss after 3 seconds."
            trigger="hover"
            type="tooltip"
            duration={3000}
          />
        </section>

        {/* Popover Examples */}
        <section className="help-demo-section">
          <h2>Popover Examples</h2>
          <div className="help-demo-items">
            <button
              id="click-popover"
              className="help-demo-button"
              onClick={() => setShowPopover(!showPopover)}
            >
              Click for Popover
            </button>
            <div id="image-popover" className="help-demo-item">
              Popover with Image
            </div>
            <div id="html-popover" className="help-demo-item">
              Popover with HTML
            </div>
          </div>

          {/* Click-triggered popover */}
          <ContextualHelp
            targetId="click-popover"
            title="COMMAND CONSOLE"
            content="The command console gives you direct access to system functions. Use keyboard shortcut Alt+C to open it quickly."
            trigger="manual"
            type="popover"
            isOpen={showPopover}
            onClose={() => setShowPopover(false)}
          />

          {/* Popover with image */}
          <ContextualHelp
            targetId="image-popover"
            title="NEURAL INTERFACE"
            content="Connect to the neural interface for direct brain-computer interaction."
            image="https://placehold.co/300x150/001122/00ccff?text=Neural+Interface"
            imageAlt="Neural interface illustration"
            trigger="hover"
            type="popover"
          />

          {/* Popover with HTML content */}
          <ContextualHelp
            targetId="html-popover"
            title="SYSTEM STATUS"
            content="<strong>System online.</strong><br>Current status: <span style='color:#00f0ff'>Operational</span><br><ul><li>CPU: 42%</li><li>Memory: 1.2TB</li><li>Network: Stable</li></ul>"
            allowHtml={true}
            trigger="hover"
            type="popover"
          />
        </section>

        {/* Hint Examples */}
        <section className="help-demo-section">
          <h2>Contextual Hint Examples</h2>
          <div className="help-demo-items">
            <button
              id="feature-hint"
              className="help-demo-button pulse-button"
              onClick={() => setShowHint(!showHint)}
            >
              New Feature
            </button>
          </div>

          {/* Contextual hint */}
          <ContextualHelp
            targetId="feature-hint"
            title="NEW FEATURE UNLOCKED"
            content="You've unlocked advanced neural networking capabilities. Click to activate and upgrade your system."
            trigger="manual"
            type="hint"
            isOpen={showHint}
            onClose={() => setShowHint(false)}
            position="top"
          />
        </section>
      </div>

      <footer className="help-example-footer">
        <p>
          ContextualHelp component provides tooltips, popovers, and contextual
          hints with cyberpunk styling
        </p>
      </footer>
    </div>
  );
};

export default HelpExample;
