import React, { createContext, useContext, useState, useEffect } from 'react';
import { useTheme } from './ThemeContext';
import { ContainerStyleConfig } from '../components/universal/UniversalContainer';
import { containerThemes, getContainerTheme } from './containerThemes';

/**
 * Theme styler context interface
 */
interface ThemeStylerContextType {
  // Custom theme overrides for different UI elements
  customThemes: {
    [containerType: string]: Partial<ContainerStyleConfig>;
  };
  // Currently active theme name
  activeThemeName: string;
  // Set active theme
  setActiveTheme: (themeName: string) => void;
  // Update a custom theme override
  setCustomTheme: (
    containerType: string,
    config: Partial<ContainerStyleConfig>
  ) => void;
  // Get a container style configuration
  getStyleConfig: (containerType: string) => Partial<ContainerStyleConfig>;
  // Reset to defaults
  resetCustomThemes: () => void;
}

// Create the context
const ThemeStylerContext = createContext<ThemeStylerContextType | undefined>(
  undefined
);

/**
 * Available container types that can be styled
 */
export type ContainerType =
  | 'primary'
  | 'secondary'
  | 'progress'
  | 'alert'
  | 'modal'
  | 'card';

/**
 * Default custom themes (empty overrides)
 */
const defaultCustomThemes = {
  primary: {},
  secondary: {},
  progress: {},
  alert: {},
  modal: {},
  card: {},
};

/**
 * Theme Styler Provider component
 */
export const ThemeStylerProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { theme } = useTheme();
  const [activeThemeName, setActiveThemeName] = useState<string>('cyberpunk');
  const [customThemes, setCustomThemes] = useState<{
    [key: string]: Partial<ContainerStyleConfig>;
  }>(defaultCustomThemes);

  // Update active theme based on main theme style
  useEffect(() => {
    // Map the main theme style to a container theme
    const themeMap: { [key: string]: string } = {
      cyberpunk: 'cyberpunk',
      corporate: 'corporate',
      classic: 'corporate',
    };

    setActiveThemeName(themeMap[theme.style] || 'cyberpunk');
  }, [theme.style]);

  /**
   * Set the active theme name
   */
  const setActiveTheme = (themeName: string) => {
    if (containerThemes[themeName]) {
      setActiveThemeName(themeName);
    }
  };

  /**
   * Update a custom theme configuration for a specific container type
   */
  const setCustomTheme = (
    containerType: string,
    config: Partial<ContainerStyleConfig>
  ) => {
    setCustomThemes(prev => ({
      ...prev,
      [containerType]: {
        ...prev[containerType],
        ...config,
      },
    }));
  };

  /**
   * Get the style configuration for a specific container type
   * Merges the base theme with custom overrides
   */
  const getStyleConfig = (
    containerType: string
  ): Partial<ContainerStyleConfig> => {
    // Get the base container theme
    const baseConfig = getContainerTheme(activeThemeName, containerType as any);

    // Merge with custom overrides
    return {
      ...baseConfig,
      ...(customThemes[containerType] || {}),
      // Special handling for decorative elements to merge them properly
      decorativeElements: {
        ...(baseConfig.decorativeElements || {}),
        ...(customThemes[containerType]?.decorativeElements || {}),
      },
    };
  };

  /**
   * Reset all custom theme overrides to defaults
   */
  const resetCustomThemes = () => {
    setCustomThemes(defaultCustomThemes);
  };

  return (
    <ThemeStylerContext.Provider
      value={{
        customThemes,
        activeThemeName,
        setActiveTheme,
        setCustomTheme,
        getStyleConfig,
        resetCustomThemes,
      }}
    >
      {children}
    </ThemeStylerContext.Provider>
  );
};

/**
 * Hook to use the theme styler
 */
export const useThemeStyler = (): ThemeStylerContextType => {
  const context = useContext(ThemeStylerContext);
  if (!context) {
    throw new Error('useThemeStyler must be used within a ThemeStylerProvider');
  }
  return context;
};

/**
 * Theme Styler Control Panel component for visually customizing containers
 */
export const ThemeStylerPanel: React.FC<{
  containerType: ContainerType;
  onClose?: () => void;
}> = ({ containerType, onClose }) => {
  const { activeThemeName, setActiveTheme, getStyleConfig, setCustomTheme } =
    useThemeStyler();

  const currentConfig = getStyleConfig(containerType);

  // Theme name options
  const themeOptions = Object.keys(containerThemes);

  // Style properties for customization
  const styleProperties = [
    {
      label: 'Border Style',
      key: 'borderStyle' as keyof ContainerStyleConfig,
      options: ['none', 'solid', 'dashed', 'neon'],
    },
    {
      label: 'Border Width',
      key: 'borderWidth' as keyof ContainerStyleConfig,
      options: ['thin', 'medium', 'thick'],
    },
    {
      label: 'Glass Effect',
      key: 'glassEffect' as keyof ContainerStyleConfig,
      options: ['none', 'light', 'medium', 'heavy'],
    },
    {
      label: 'Transparency',
      key: 'transparency' as keyof ContainerStyleConfig,
      options: ['none', 'light', 'medium', 'heavy'],
    },
    {
      label: 'Animation',
      key: 'animation' as keyof ContainerStyleConfig,
      options: ['none', 'float', 'pulse', 'glow'],
    },
    {
      label: 'Position Style',
      key: 'positionStyle' as keyof ContainerStyleConfig,
      options: ['centered', 'offset-left', 'offset-right', 'detached'],
    },
    {
      label: 'Orientation',
      key: 'orientation' as keyof ContainerStyleConfig,
      options: ['front-facing', 'angled'],
    },
  ];

  // Accent color options
  const accentColors = [
    'cyan',
    'magenta',
    'blue',
    'purple',
    'pink',
    'green',
    'orange',
  ];

  // Decorative elements
  const decorativeElements = [
    { key: 'drones', label: 'Show Drone Attachments' },
    { key: 'neonTrim', label: 'Show Neon Trim Effects' },
    { key: 'holographicDisplay', label: 'Show Holographic Display' },
  ];

  // Update a style property
  const updateStyleProperty = (key: keyof ContainerStyleConfig, value: any) => {
    setCustomTheme(containerType, { [key]: value });
  };

  // Update a decorative element
  const updateDecorativeElement = (key: string, checked: boolean) => {
    const currentElements = currentConfig.decorativeElements || {};
    setCustomTheme(containerType, {
      decorativeElements: {
        ...currentElements,
        [key]: checked,
      },
    });
  };

  return (
    <div className="bg-background border border-border rounded-lg p-4 w-full max-w-md max-h-[80vh] overflow-y-auto">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium">
          Customize {containerType} Container
        </h3>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1 rounded-md hover:bg-muted/50"
          >
            &times;
          </button>
        )}
      </div>

      {/* Theme Selector */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-muted-foreground mb-2">
          Base Theme
        </label>
        <div className="flex flex-wrap gap-2">
          {themeOptions.map(name => (
            <button
              key={name}
              onClick={() => setActiveTheme(name)}
              className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                activeThemeName === name
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted/50 hover:bg-muted'
              }`}
            >
              {name.charAt(0).toUpperCase() + name.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Accent Color Selector */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-muted-foreground mb-2">
          Accent Color
        </label>
        <div className="flex flex-wrap gap-3">
          {accentColors.map(color => (
            <button
              key={color}
              onClick={() => updateStyleProperty('accentColor', color)}
              className={`w-8 h-8 rounded-full transition-all ${
                currentConfig.accentColor === color
                  ? 'ring-2 ring-offset-2 ring-offset-background'
                  : ''
              }`}
              style={{
                background:
                  color === 'cyan'
                    ? '#00FFFF'
                    : color === 'magenta'
                      ? '#FF00FF'
                      : color === 'blue'
                        ? '#0066FF'
                        : color === 'purple'
                          ? '#9900FF'
                          : color === 'pink'
                            ? '#FF00AA'
                            : color === 'green'
                              ? '#00FF66'
                              : color === 'orange'
                                ? '#FF9900'
                                : '#888888',
              }}
              title={color}
            />
          ))}
        </div>
      </div>

      {/* Style Properties */}
      <div className="space-y-4 mb-6">
        {styleProperties.map(prop => (
          <div key={prop.key}>
            <label className="block text-sm font-medium text-muted-foreground mb-2">
              {prop.label}
            </label>
            <div className="flex flex-wrap gap-2">
              {prop.options.map(option => (
                <button
                  key={option}
                  onClick={() => updateStyleProperty(prop.key, option)}
                  className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                    currentConfig[prop.key] === option
                      ? 'bg-primary/20 border border-primary/40'
                      : 'bg-muted/50 hover:bg-muted border border-transparent'
                  }`}
                >
                  {option.charAt(0).toUpperCase() +
                    option.slice(1).replace('-', ' ')}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Decorative Elements */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-muted-foreground mb-2">
          Decorative Elements
        </label>
        <div className="space-y-2">
          {decorativeElements.map(elem => (
            <label
              key={elem.key}
              className="flex items-center gap-2 cursor-pointer"
            >
              <input
                type="checkbox"
                checked={Boolean(
                  currentConfig.decorativeElements?.[
                    elem.key as keyof typeof currentConfig.decorativeElements
                  ]
                )}
                onChange={e =>
                  updateDecorativeElement(elem.key, e.target.checked)
                }
                className="w-4 h-4 rounded border-border text-primary focus:ring-primary/50"
              />
              <span className="text-sm">{elem.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Reset Button */}
      <button
        onClick={() => setCustomTheme(containerType, {})}
        className="w-full py-2 text-sm border border-border rounded-md hover:bg-muted transition-colors"
      >
        Reset to Default
      </button>
    </div>
  );
};

export default ThemeStylerProvider;
