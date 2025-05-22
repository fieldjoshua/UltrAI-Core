import React, { createContext, useContext, useEffect, useState } from 'react';
import { ThemeManager, THEMES } from './ThemeManager';

// Create a context for theme data
const ThemeContext = createContext(null);

/**
 * Theme Provider Component
 *
 * Provides theme context to all child components and handles theme changes.
 */
const ThemeProvider = ({
  children,
  initialTheme = THEMES.STANDARD,
  persistenceKey = 'ultraai_theme_preferences',
  customThemes = {},
}) => {
  // Initialize theme manager
  const [themeManager] = useState(
    () =>
      new ThemeManager({
        initialTheme,
        persistenceKey,
        customThemes,
      })
  );

  // Track current theme settings in state for components to access
  const [currentTheme, setCurrentTheme] = useState(
    themeManager.getCurrentTheme()
  );
  const [themeSettings, setThemeSettings] = useState(
    themeManager.getThemeSettings()
  );

  // Apply theme when component mounts
  useEffect(() => {
    // Set up theme change callback
    themeManager.onThemeChange = (themeName, settings) => {
      setCurrentTheme(themeName);
      setThemeSettings(settings);
    };

    // Apply initial theme
    themeManager.applyTheme();

    return () => {
      // Clean up
      themeManager.onThemeChange = null;
    };
  }, [themeManager]);

  // Context value with theme data and functions
  const contextValue = {
    currentTheme,
    themeSettings,
    availableThemes: themeManager.getAvailableThemes(),
    setTheme: (themeName) => themeManager.switchTheme(themeName),
    createCustomTheme: (themeName, settings) =>
      themeManager.createCustomTheme(themeName, settings),
  };

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
};

/**
 * Hook to access theme data and functions
 */
const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export { ThemeProvider, useTheme, THEMES };
export default ThemeProvider;
