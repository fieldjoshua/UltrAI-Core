/**
 * Personalization Module
 *
 * Provides components and utilities for personalizing the user experience
 * with themes, preferences, and customization options.
 */

import ThemeManager, { THEMES, defaultThemeSettings } from './ThemeManager';
import ThemeProvider, { useTheme } from './ThemeProvider';
import ThemeSwitcher from './ThemeSwitcher';

// Export all components and utilities
export {
  ThemeManager,
  THEMES,
  defaultThemeSettings,
  ThemeProvider,
  useTheme,
  ThemeSwitcher,
};

// Default export for easier imports
export default {
  ThemeManager,
  ThemeProvider,
  ThemeSwitcher,
  THEMES,
};
