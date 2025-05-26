import React from 'react';
import { useTheme } from './ThemeContext';

interface DayNightToggleProps {
  className?: string;
  size?: 'small' | 'medium' | 'large' | 'sm';
  showLabel?: boolean;
}

const DayNightToggle: React.FC<DayNightToggleProps> = ({
  className = '',
  size = 'medium',
  showLabel = false,
}) => {
  const { theme, toggleMode } = useTheme();
  const isDark = theme.mode === 'dark';

  // Size variants
  const sizeMap = {
    small: {
      button: 'w-8 h-8',
      icon: 'w-4 h-4',
    },
    medium: {
      button: 'w-10 h-10',
      icon: 'w-5 h-5',
    },
    large: {
      button: 'w-12 h-12',
      icon: 'w-6 h-6',
    },
    // Add fallback for 'sm' that maps to 'small'
    sm: {
      button: 'w-8 h-8',
      icon: 'w-4 h-4',
    },
  };

  // Add a fallback to medium size if the provided size doesn't exist in sizeMap
  const { button: buttonSize, icon: iconSize } =
    sizeMap[size] || sizeMap.medium;

  return (
    <div className={`flex items-center ${className}`}>
      {showLabel && (
        <span className="mr-2 text-sm text-foreground">
          {isDark ? 'Night' : 'Day'}
        </span>
      )}

      <button
        onClick={toggleMode}
        className={`${buttonSize} relative rounded-full flex items-center justify-center transition-all duration-500 overflow-hidden focus:outline-none focus:ring-2 focus:ring-primary focus:ring-opacity-50`}
        aria-label={`Switch to ${isDark ? 'light' : 'dark'} theme`}
        title={`Switch to ${isDark ? 'day' : 'night'} mode`}
      >
        <div
          className={`absolute inset-0 transition-colors duration-500 ${
            isDark ? 'bg-gray-900' : 'bg-blue-100'
          }`}
        />

        {/* Day/night background graphics */}
        {isDark ? (
          <>
            {/* Stars */}
            <div className="absolute inset-0 overflow-hidden opacity-80">
              <div className="absolute h-1 w-1 rounded-full bg-white top-1 left-2" />
              <div className="absolute h-1 w-1 rounded-full bg-white top-3 left-7" />
              <div className="absolute h-0.5 w-0.5 rounded-full bg-white top-5 left-3" />
              <div className="absolute h-0.5 w-0.5 rounded-full bg-white top-2 left-5" />
              <div className="absolute h-0.5 w-0.5 rounded-full bg-white top-6 left-8" />
            </div>
          </>
        ) : (
          <>
            {/* Clouds */}
            <div className="absolute inset-0 overflow-hidden opacity-70">
              <div className="absolute h-2 w-4 rounded-full bg-white top-1 left-1" />
              <div className="absolute h-1.5 w-3 rounded-full bg-white top-5 left-6" />
            </div>
          </>
        )}

        {/* Sun/Moon Icons */}
        <div className={`relative ${iconSize} transition-all duration-300`}>
          {isDark ? (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className={`${iconSize} text-yellow-300`}
            >
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className={`${iconSize} text-yellow-500`}
            >
              <circle cx="12" cy="12" r="5" />
              <line x1="12" y1="1" x2="12" y2="3" />
              <line x1="12" y1="21" x2="12" y2="23" />
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
              <line x1="1" y1="12" x2="3" y2="12" />
              <line x1="21" y1="12" x2="23" y2="12" />
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
            </svg>
          )}
        </div>
      </button>

      {/* Neon glow effect for dark mode */}
      {isDark && theme.style === 'cyberpunk' && (
        <div className="absolute inset-0 rounded-full pointer-events-none">
          <div className="absolute inset-0 rounded-full opacity-50 blur-sm bg-cyan-400 animate-pulse" />
        </div>
      )}
    </div>
  );
};

export default DayNightToggle;
