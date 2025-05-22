/**
 * ThemeManager
 *
 * Manages application themes and user preferences for customization.
 * Provides theme switching capabilities and persistence.
 */

// Available themes with their properties
const THEMES = {
  STANDARD: 'standard',
  CYBERPUNK: 'cyberpunk',
  DARK: 'dark',
  LIGHT: 'light',
  HIGH_CONTRAST: 'high-contrast',
};

// Default theme settings
const defaultThemeSettings = {
  standard: {
    primaryColor: '#4a90e2',
    secondaryColor: '#f5f5f5',
    textColor: '#333333',
    backgroundColor: '#ffffff',
    accentColor: '#ff9900',
    borderRadius: '4px',
    fontFamily: 'Arial, sans-serif',
    fontSize: '14px',
  },
  cyberpunk: {
    primaryColor: '#ff00ff',
    secondaryColor: '#00ffff',
    textColor: '#ffffff',
    backgroundColor: '#0a0a1a',
    accentColor: '#ffff00',
    borderRadius: '0',
    fontFamily: '"Courier New", monospace',
    fontSize: '14px',
    glowEffect: '0 0 10px',
    scanlineEffect: true,
  },
  dark: {
    primaryColor: '#6200ee',
    secondaryColor: '#3700b3',
    textColor: '#ffffff',
    backgroundColor: '#121212',
    accentColor: '#bb86fc',
    borderRadius: '4px',
    fontFamily: 'Arial, sans-serif',
    fontSize: '14px',
  },
  light: {
    primaryColor: '#007bff',
    secondaryColor: '#e9ecef',
    textColor: '#212529',
    backgroundColor: '#ffffff',
    accentColor: '#28a745',
    borderRadius: '4px',
    fontFamily: 'Arial, sans-serif',
    fontSize: '14px',
  },
  'high-contrast': {
    primaryColor: '#ffffff',
    secondaryColor: '#000000',
    textColor: '#ffffff',
    backgroundColor: '#000000',
    accentColor: '#ffff00',
    borderRadius: '4px',
    fontFamily: 'Arial, sans-serif',
    fontSize: '16px',
    fontWeight: 'bold',
  },
};

class ThemeManager {
  constructor(options = {}) {
    this.activeTheme = options.initialTheme || THEMES.STANDARD;
    this.customThemes = options.customThemes || {};
    this.persistenceKey = options.persistenceKey || 'ultraai_theme_preferences';
    this.onThemeChange = options.onThemeChange || (() => {});

    // Load saved preferences if available
    this.loadSavedPreferences();
  }

  /**
   * Get all available themes
   * @returns {Object} Available themes
   */
  getAvailableThemes() {
    return { ...THEMES };
  }

  /**
   * Get settings for a specific theme
   * @param {String} themeName Theme identifier
   * @returns {Object} Theme settings
   */
  getThemeSettings(themeName = this.activeTheme) {
    // Check for custom theme first, then default
    if (this.customThemes[themeName]) {
      return this.customThemes[themeName];
    }
    return (
      defaultThemeSettings[themeName] || defaultThemeSettings[THEMES.STANDARD]
    );
  }

  /**
   * Get the currently active theme
   * @returns {String} Current theme identifier
   */
  getCurrentTheme() {
    return this.activeTheme;
  }

  /**
   * Switch to a different theme
   * @param {String} themeName Theme to switch to
   * @returns {Boolean} Success status
   */
  switchTheme(themeName) {
    // Verify theme exists
    if (!defaultThemeSettings[themeName] && !this.customThemes[themeName]) {
      console.error(`Theme "${themeName}" not found`);
      return false;
    }

    this.activeTheme = themeName;
    this.savePreferences();
    this.applyTheme();

    // Call any theme change callbacks
    if (typeof this.onThemeChange === 'function') {
      this.onThemeChange(themeName, this.getThemeSettings());
    }

    return true;
  }

  /**
   * Create or update a custom theme
   * @param {String} themeName Unique theme identifier
   * @param {Object} settings Theme settings
   * @returns {Boolean} Success status
   */
  createCustomTheme(themeName, settings) {
    if (!themeName || typeof settings !== 'object') {
      console.error('Invalid theme configuration');
      return false;
    }

    this.customThemes[themeName] = {
      ...defaultThemeSettings[THEMES.STANDARD],
      ...settings,
    };

    this.savePreferences();
    return true;
  }

  /**
   * Apply the current theme to the DOM
   */
  applyTheme() {
    const settings = this.getThemeSettings();

    // Apply CSS variables to root element
    const root = document.documentElement;

    // Apply each setting as a CSS variable
    Object.entries(settings).forEach(([key, value]) => {
      root.style.setProperty(`--theme-${key}`, value);
    });

    // Add theme class to body
    document.body.className = document.body.className
      .replace(/theme-\w+/g, '')
      .trim();
    document.body.classList.add(`theme-${this.activeTheme}`);
  }

  /**
   * Save current preferences to storage
   */
  savePreferences() {
    if (typeof window !== 'undefined' && window.localStorage) {
      const data = {
        activeTheme: this.activeTheme,
        customThemes: this.customThemes,
      };

      try {
        localStorage.setItem(this.persistenceKey, JSON.stringify(data));
      } catch (e) {
        console.error('Failed to save theme preferences:', e);
      }
    }
  }

  /**
   * Load saved preferences from storage
   */
  loadSavedPreferences() {
    if (typeof window !== 'undefined' && window.localStorage) {
      try {
        const saved = localStorage.getItem(this.persistenceKey);

        if (saved) {
          const data = JSON.parse(saved);
          this.activeTheme = data.activeTheme || this.activeTheme;
          this.customThemes = data.customThemes || this.customThemes;
        }
      } catch (e) {
        console.error('Failed to load theme preferences:', e);
      }
    }
  }
}

// Export the theme manager and constants
export { ThemeManager, THEMES, defaultThemeSettings };
export default ThemeManager;
