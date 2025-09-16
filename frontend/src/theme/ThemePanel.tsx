import React, { useState } from 'react';
import {
  useTheme,
  ThemePreferences,
  ThemeMode,
  ThemeStyle,
  AccentColor,
} from './ThemeContext';
import DayNightToggle from './DayNightToggle';

interface ThemePanelProps {
  className?: string;
  isOpen?: boolean;
  onClose?: () => void;
}

/**
 * ThemePanel provides a UI for adjusting theme settings
 */
const ThemePanel: React.FC<ThemePanelProps> = ({
  className = '',
  isOpen = false,
  onClose,
}) => {
  const { theme, setTheme, resetToDefaults } = useTheme();

  // Local state for panel settings
  const [localTheme, setLocalTheme] = useState<ThemePreferences>({ ...theme });

  // Update local theme state
  const updateLocalTheme = <K extends keyof ThemePreferences>(
    key: K,
    value: ThemePreferences[K]
  ) => {
    setLocalTheme(prev => ({ ...prev, [key]: value }));
  };

  // Apply local theme settings to global theme
  const applyTheme = () => {
    setTheme(localTheme);
  };

  // Reset local theme when panel opens
  React.useEffect(() => {
    if (isOpen) {
      setLocalTheme({ ...theme });
    }
  }, [isOpen, theme]);

  // Apply theme automatically when changing certain settings
  React.useEffect(() => {
    setTheme(localTheme);
  }, [
    localTheme.mode,
    localTheme.style,
    localTheme.accentColor,
    localTheme.reducedMotion,
  ]);

  return (
    <div className={`theme-panel ${className} ${isOpen ? 'block' : 'hidden'}`}>
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />

      <div className="fixed right-0 top-0 bottom-0 w-full sm:w-96 bg-card border-l border-border shadow-xl z-50 overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold">Theme Settings</h2>

            <button
              onClick={onClose}
              className="p-2 rounded-full hover:bg-muted"
              aria-label="Close theme panel"
            >
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
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>

          {/* Theme Mode */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-3">Mode</h3>
            <div className="flex space-x-4">
              <label
                className={`flex flex-col items-center cursor-pointer ${localTheme.mode === 'light' ? 'text-primary' : 'text-muted-foreground'}`}
              >
                <div
                  className={`p-3 rounded-lg mb-2 ${localTheme.mode === 'light' ? 'bg-primary bg-opacity-10 border-2 border-primary' : 'bg-muted'}`}
                >
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
                </div>
                <input
                  type="radio"
                  name="mode"
                  value="light"
                  checked={localTheme.mode === 'light'}
                  onChange={() => updateLocalTheme('mode', 'light')}
                  className="sr-only"
                />
                Light
              </label>

              <label
                className={`flex flex-col items-center cursor-pointer ${localTheme.mode === 'dark' ? 'text-primary' : 'text-muted-foreground'}`}
              >
                <div
                  className={`p-3 rounded-lg mb-2 ${localTheme.mode === 'dark' ? 'bg-primary bg-opacity-10 border-2 border-primary' : 'bg-muted'}`}
                >
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
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                  </svg>
                </div>
                <input
                  type="radio"
                  name="mode"
                  value="dark"
                  checked={localTheme.mode === 'dark'}
                  onChange={() => updateLocalTheme('mode', 'dark')}
                  className="sr-only"
                />
                Dark
              </label>

              <div className="flex flex-col items-center">
                <div className="p-3 rounded-lg mb-2 bg-muted">
                  <DayNightToggle size="small" />
                </div>
                <span className="text-muted-foreground">Auto</span>
              </div>
            </div>
          </div>

          {/* Theme Style */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-3">Style</h3>
            <div className="grid grid-cols-3 gap-4">
              {(['cyberpunk', 'corporate', 'classic'] as ThemeStyle[]).map(
                style => (
                  <label
                    key={style}
                    className={`flex flex-col items-center cursor-pointer ${
                      localTheme.style === style
                        ? 'text-primary'
                        : 'text-muted-foreground'
                    }`}
                  >
                    <div
                      className={`w-full aspect-video rounded-lg mb-2 border overflow-hidden ${
                        localTheme.style === style
                          ? 'border-2 border-primary'
                          : 'border-muted'
                      }`}
                    >
                      <div
                        className={`w-full h-full flex items-center justify-center ${style} ${localTheme.mode}`}
                        style={{
                          background:
                            style === 'cyberpunk'
                              ? 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)'
                              : style === 'corporate'
                                ? '#f8f9fa'
                                : '#ffffff',
                        }}
                      >
                        {style === 'cyberpunk' && (
                          <span className="text-xs font-bold text-cyan-400 neon-text">
                            ULTRA AI
                          </span>
                        )}
                        {style === 'corporate' && (
                          <span className="text-xs font-bold text-blue-600">
                            Ultra AI
                          </span>
                        )}
                        {style === 'classic' && (
                          <span className="text-xs font-bold text-gray-900">
                            Ultra AI
                          </span>
                        )}
                      </div>
                    </div>
                    <input
                      type="radio"
                      name="style"
                      value={style}
                      checked={localTheme.style === style}
                      onChange={() => updateLocalTheme('style', style)}
                      className="sr-only"
                    />
                    {style.charAt(0).toUpperCase() + style.slice(1)}
                  </label>
                )
              )}
            </div>
          </div>

          {/* Accent Color */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-3">Accent Color</h3>
            <div className="flex flex-wrap gap-3">
              {(
                ['cyan', 'purple', 'orange', 'green', 'pink'] as AccentColor[]
              ).map(color => (
                <label
                  key={color}
                  className="cursor-pointer"
                  title={color.charAt(0).toUpperCase() + color.slice(1)}
                >
                  <input
                    type="radio"
                    name="accentColor"
                    value={color}
                    checked={localTheme.accentColor === color}
                    onChange={() => updateLocalTheme('accentColor', color)}
                    className="sr-only"
                  />
                  <div
                    className={`w-8 h-8 rounded-full transition-all ${
                      localTheme.accentColor === color
                        ? 'ring-2 ring-offset-2 ring-offset-background'
                        : ''
                    }`}
                    style={{
                      background:
                        color === 'cyan'
                          ? '#00FFFF'
                          : color === 'purple'
                            ? '#9900FF'
                            : color === 'orange'
                              ? '#FF9900'
                              : color === 'green'
                                ? '#00FF66'
                                : '#FF00AA',
                      boxShadow:
                        localTheme.accentColor === color &&
                        localTheme.style === 'cyberpunk'
                          ? `0 0 10px ${
                              color === 'cyan'
                                ? '#00FFFF'
                                : color === 'purple'
                                  ? '#9900FF'
                                  : color === 'orange'
                                    ? '#FF9900'
                                    : color === 'green'
                                      ? '#00FF66'
                                      : '#FF00AA'
                            }`
                          : 'none',
                    }}
                  />
                </label>
              ))}
            </div>
          </div>

          {/* Font Size */}
          <div className="mb-8">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-lg font-semibold">Font Size</h3>
              <span className="text-sm text-muted-foreground">
                {Math.round(localTheme.fontSize * 100)}%
              </span>
            </div>
            <input
              type="range"
              min="0.8"
              max="1.2"
              step="0.05"
              value={localTheme.fontSize}
              onChange={e =>
                updateLocalTheme('fontSize', parseFloat(e.target.value))
              }
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground mt-1">
              <span>A</span>
              <span className="text-base">A</span>
              <span className="text-lg">A</span>
            </div>
          </div>

          {/* Contrast */}
          <div className="mb-8">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-lg font-semibold">Contrast</h3>
              <span className="text-sm text-muted-foreground">
                {localTheme.contrastLevel === 1
                  ? 'Low'
                  : localTheme.contrastLevel === 5
                    ? 'High'
                    : 'Normal'}
              </span>
            </div>
            <input
              type="range"
              min="1"
              max="5"
              step="1"
              value={localTheme.contrastLevel}
              onChange={e =>
                updateLocalTheme('contrastLevel', parseInt(e.target.value))
              }
              className="w-full"
            />
          </div>

          {/* Animations */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-3">Animations</h3>
            <div className="flex flex-col space-y-4">
              <label className="flex items-center justify-between cursor-pointer">
                <span>Enable animations</span>
                <div className="relative inline-block w-10 h-6 transition duration-200 ease-in-out rounded-full">
                  <input
                    type="checkbox"
                    className="absolute w-6 h-6 opacity-0 rounded-full peer"
                    checked={localTheme.animationsEnabled}
                    onChange={e =>
                      updateLocalTheme('animationsEnabled', e.target.checked)
                    }
                  />
                  <span className="absolute inset-0 transition-colors duration-200 rounded-full bg-muted peer-checked:bg-primary"></span>
                  <span className="absolute inset-y-0 left-0 flex items-center justify-center w-6 h-6 transition-transform duration-200 transform translate-x-0 rounded-full bg-white shadow-sm peer-checked:translate-x-4"></span>
                </div>
              </label>

              <label className="flex items-center justify-between cursor-pointer">
                <span>Reduced motion</span>
                <div className="relative inline-block w-10 h-6 transition duration-200 ease-in-out rounded-full">
                  <input
                    type="checkbox"
                    className="absolute w-6 h-6 opacity-0 rounded-full peer"
                    checked={localTheme.reducedMotion}
                    onChange={e =>
                      updateLocalTheme('reducedMotion', e.target.checked)
                    }
                  />
                  <span className="absolute inset-0 transition-colors duration-200 rounded-full bg-muted peer-checked:bg-primary"></span>
                  <span className="absolute inset-y-0 left-0 flex items-center justify-center w-6 h-6 transition-transform duration-200 transform translate-x-0 rounded-full bg-white shadow-sm peer-checked:translate-x-4"></span>
                </div>
              </label>
            </div>
          </div>

          {/* Reset button */}
          <div className="pt-4 border-t border-border">
            <button
              onClick={resetToDefaults}
              className="px-4 py-2 text-sm rounded-md bg-muted hover:bg-muted/80 transition-colors"
            >
              Reset to Defaults
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ThemePanel;
