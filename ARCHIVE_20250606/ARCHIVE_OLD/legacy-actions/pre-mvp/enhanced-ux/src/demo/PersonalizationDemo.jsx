import React, { useState } from 'react';
import {
  ThemeProvider,
  ThemeSwitcher,
  THEMES,
  useTheme,
} from '../personalization';

/**
 * Personalization Demo
 *
 * Demonstrates the theme personalization capabilities with live preview.
 */
const PersonalizationDemo = () => {
  return (
    <ThemeProvider initialTheme={THEMES.CYBERPUNK}>
      <DemoContent />
    </ThemeProvider>
  );
};

// Component that uses the theme context
const DemoContent = () => {
  const { themeSettings, currentTheme } = useTheme();
  const [customThemeName, setCustomThemeName] = useState('');
  const [primaryColor, setPrimaryColor] = useState('#3498db');

  // Demo container style
  const containerStyle = {
    fontFamily: themeSettings.fontFamily,
    backgroundColor: themeSettings.backgroundColor,
    color: themeSettings.textColor,
    padding: '20px',
    borderRadius: themeSettings.borderRadius,
    maxWidth: '800px',
    margin: '0 auto',
    transition: 'all 0.3s ease',
  };

  // Card style
  const cardStyle = {
    backgroundColor: themeSettings.secondaryColor,
    padding: '15px',
    margin: '15px 0',
    borderRadius: themeSettings.borderRadius,
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    border:
      currentTheme === THEMES.CYBERPUNK
        ? `1px solid ${themeSettings.primaryColor}`
        : 'none',
  };

  // Button style
  const buttonStyle = {
    backgroundColor: themeSettings.primaryColor,
    color: '#ffffff',
    border: 'none',
    borderRadius: themeSettings.borderRadius,
    padding: '8px 16px',
    margin: '5px',
    cursor: 'pointer',
    fontFamily: themeSettings.fontFamily,
    fontSize: themeSettings.fontSize,
  };

  // Header style
  const headerStyle = {
    color: themeSettings.primaryColor,
    borderBottom: `2px solid ${themeSettings.accentColor}`,
    paddingBottom: '10px',
    marginBottom: '20px',
  };

  return (
    <div style={containerStyle}>
      <h1 style={headerStyle}>Theme Personalization Demo</h1>

      <div style={cardStyle}>
        <h2>Select a Theme</h2>
        <ThemeSwitcher />
      </div>

      <div style={cardStyle}>
        <h2>Theme Preview</h2>
        <p>
          This demo showcases the dynamic theme system. Try switching between
          different themes to see how the interface adapts.
        </p>

        <div>
          <h3>Button Examples</h3>
          <button style={buttonStyle}>Primary Button</button>
          <button
            style={{
              ...buttonStyle,
              backgroundColor: themeSettings.accentColor,
            }}
          >
            Accent Button
          </button>
        </div>

        <div>
          <h3>Current Theme: {currentTheme}</h3>
          <p>
            The current theme settings are applied to all elements in this demo.
          </p>

          <ul style={{ color: themeSettings.textColor }}>
            <li>
              Primary Color:{' '}
              <span
                style={{
                  color: themeSettings.primaryColor,
                  fontWeight: 'bold',
                }}
              >
                {themeSettings.primaryColor}
              </span>
            </li>
            <li>
              Secondary Color:{' '}
              <span
                style={{
                  color: themeSettings.secondaryColor,
                  fontWeight: 'bold',
                  backgroundColor: '#333',
                  padding: '2px 5px',
                }}
              >
                {themeSettings.secondaryColor}
              </span>
            </li>
            <li>
              Accent Color:{' '}
              <span
                style={{ color: themeSettings.accentColor, fontWeight: 'bold' }}
              >
                {themeSettings.accentColor}
              </span>
            </li>
            <li>Font Family: {themeSettings.fontFamily}</li>
          </ul>
        </div>
      </div>

      {currentTheme === THEMES.CYBERPUNK && (
        <div
          style={{
            ...cardStyle,
            border: `1px solid ${themeSettings.accentColor}`,
            boxShadow: `0 0 15px ${themeSettings.primaryColor}`,
          }}
        >
          <h2 style={{ color: themeSettings.accentColor }}>
            Cyberpunk Special Features
          </h2>
          <p>
            The cyberpunk theme includes special visual effects like glowing
            borders and animated elements.
          </p>

          <div
            style={{
              padding: '10px',
              border: `1px solid ${themeSettings.primaryColor}`,
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            <p style={{ position: 'relative', zIndex: 1 }}>
              This content has a scanline effect and glowing border.
            </p>

            {/* Scanline effect */}
            <div
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundImage:
                  'linear-gradient(transparent 50%, rgba(0, 0, 0, 0.3) 50%)',
                backgroundSize: '4px 4px',
                pointerEvents: 'none',
                opacity: 0.5,
                zIndex: 0,
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default PersonalizationDemo;
