import React from 'react';
import { useTheme, THEMES } from './ThemeProvider';

/**
 * Theme Switcher Component
 *
 * Allows users to switch between available themes.
 */
const ThemeSwitcher = ({
  showLabel = true,
  compact = false,
  className = '',
  style = {},
}) => {
  const { currentTheme, availableThemes, setTheme, themeSettings } = useTheme();

  // Style for the theme switcher container
  const containerStyle = {
    display: 'flex',
    flexDirection: compact ? 'row' : 'column',
    alignItems: compact ? 'center' : 'flex-start',
    gap: compact ? '10px' : '5px',
    ...style,
  };

  // Style for theme option buttons
  const themeButtonStyle = (themeName) => ({
    padding: compact ? '5px 10px' : '8px 12px',
    border: `2px solid ${
      themeName === currentTheme ? themeSettings.accentColor : 'transparent'
    }`,
    borderRadius: themeSettings.borderRadius,
    backgroundColor:
      themeName === currentTheme
        ? themeSettings.secondaryColor
        : 'rgba(0,0,0,0.1)',
    color:
      themeName === currentTheme
        ? themeSettings.primaryColor
        : themeSettings.textColor,
    cursor: 'pointer',
    fontFamily: themeSettings.fontFamily,
    fontSize: compact ? '12px' : '14px',
    transition: 'all 0.2s ease',
    margin: '2px',
    fontWeight: themeName === currentTheme ? 'bold' : 'normal',
  });

  // Get a friendlier display name for the theme
  const getThemeDisplayName = (themeKey) => {
    return themeKey
      .replace(/([A-Z])/g, ' $1') // Add spaces before capital letters
      .replace(/-/g, ' ') // Replace hyphens with spaces
      .split(' ')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  };

  return (
    <div
      className={`theme-switcher ${className}`}
      style={containerStyle}
      data-testid="theme-switcher"
    >
      {showLabel && (
        <label
          style={{
            color: themeSettings.textColor,
            fontFamily: themeSettings.fontFamily,
            fontSize: compact ? '12px' : '14px',
            marginBottom: compact ? '0' : '8px',
            fontWeight: 'bold',
          }}
        >
          Select Theme:
        </label>
      )}

      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '5px',
        }}
      >
        {Object.entries(availableThemes).map(([key, value]) => (
          <button
            key={key}
            onClick={() => setTheme(value)}
            style={themeButtonStyle(value)}
            aria-pressed={currentTheme === value}
            aria-label={`Switch to ${getThemeDisplayName(key)} theme`}
          >
            {getThemeDisplayName(key)}
          </button>
        ))}
      </div>
    </div>
  );
};

export default ThemeSwitcher;
