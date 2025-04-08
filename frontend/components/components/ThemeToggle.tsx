import React, { useState, useEffect } from 'react';

interface ThemeToggleProps {
  onThemeChange?: (theme: 'light' | 'dark') => void;
  initialTheme?: 'light' | 'dark';
  className?: string;
}

/**
 * ThemeToggle provides a switch to toggle between light and dark themes
 */
const ThemeToggle: React.FC<ThemeToggleProps> = ({
  onThemeChange,
  initialTheme = 'light',
  className = '',
}) => {
  const [theme, setTheme] = useState<'light' | 'dark'>(initialTheme);

  // Apply theme to document when changed
  useEffect(() => {
    document.documentElement.classList.remove('light-theme', 'dark-theme');
    document.documentElement.classList.add(`${theme}-theme`);

    // Update CSS variables for theme colors
    if (theme === 'dark') {
      document.documentElement.style.setProperty('--bg-primary', '#1a202c');
      document.documentElement.style.setProperty('--bg-secondary', '#2d3748');
      document.documentElement.style.setProperty('--text-primary', '#f7fafc');
      document.documentElement.style.setProperty('--text-secondary', '#e2e8f0');
      document.documentElement.style.setProperty('--accent-color', '#4299e1');
    } else {
      document.documentElement.style.setProperty('--bg-primary', '#ffffff');
      document.documentElement.style.setProperty('--bg-secondary', '#f7fafc');
      document.documentElement.style.setProperty('--text-primary', '#1a202c');
      document.documentElement.style.setProperty('--text-secondary', '#4a5568');
      document.documentElement.style.setProperty('--accent-color', '#3182ce');
    }

    // Store theme preference in localStorage
    localStorage.setItem('ultraTheme', theme);

    // Notify parent component about theme change
    if (onThemeChange) {
      onThemeChange(theme);
    }
  }, [theme, onThemeChange]);

  // Check for saved theme preference on component mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('ultraTheme') as
      | 'light'
      | 'dark'
      | null;
    if (savedTheme) {
      setTheme(savedTheme);
    } else {
      // Check if user prefers dark mode at system level
      const prefersDarkMode = window.matchMedia(
        '(prefers-color-scheme: dark)'
      ).matches;
      setTheme(prefersDarkMode ? 'dark' : 'light');
    }
  }, []);

  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  return (
    <div className={`theme-toggle ${className}`}>
      <button
        onClick={toggleTheme}
        className={`theme-toggle-button ${theme}`}
        aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
      >
        {theme === 'light' ? (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
          </svg>
        ) : (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
          </svg>
        )}
      </button>
    </div>
  );
};

export default ThemeToggle;

// Add this CSS to your global styles or component CSS file
/*
.theme-toggle-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s, color 0.3s;
}

.theme-toggle-button.light {
  color: #4a5568;
}

.theme-toggle-button.light:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.theme-toggle-button.dark {
  color: #e2e8f0;
}

.theme-toggle-button.dark:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f7fafc;
  --text-primary: #1a202c;
  --text-secondary: #4a5568;
  --accent-color: #3182ce;
}

.dark-theme {
  --bg-primary: #1a202c;
  --bg-secondary: #2d3748;
  --text-primary: #f7fafc;
  --text-secondary: #e2e8f0;
  --accent-color: #4299e1;
}
*/
