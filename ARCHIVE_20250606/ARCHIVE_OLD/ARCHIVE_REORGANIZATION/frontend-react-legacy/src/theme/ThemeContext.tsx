import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from 'react';

// Theme types
export type ThemeMode = 'light' | 'dark';
export type ThemeStyle = 'cyberpunk' | 'classic' | 'corporate';
export type AccentColor = 'cyan' | 'purple' | 'orange' | 'green' | 'pink';

export interface ThemePreferences {
  mode: ThemeMode;
  style: ThemeStyle;
  accentColor: AccentColor;
  contrastLevel: number; // 1-5, where 5 is highest contrast
  animationsEnabled: boolean;
  reducedMotion: boolean;
  fontSize: number; // 0.8-1.2 scaling factor
}

export interface BrandingOptions {
  primaryColor?: string;
  secondaryColor?: string;
  logoUrl?: string;
  companyName?: string;
  customFontFamily?: string;
}

export interface ThemeContextType {
  theme: ThemePreferences;
  branding: BrandingOptions;
  setTheme: (theme: Partial<ThemePreferences>) => void;
  setBranding: (branding: Partial<BrandingOptions>) => void;
  resetToDefaults: () => void;
  toggleMode: () => void;
}

// Default theme preferences
export const defaultTheme: ThemePreferences = {
  mode: 'dark', // Default to dark mode based on your mockups
  style: 'cyberpunk', // Set the cyberpunk style as default
  accentColor: 'cyan',
  contrastLevel: 3,
  animationsEnabled: true,
  reducedMotion: false,
  fontSize: 1,
};

// Default branding
export const defaultBranding: BrandingOptions = {
  primaryColor: '#00FFFF', // Cyan
  secondaryColor: '#FF9D00', // Orange
  logoUrl: '',
  companyName: 'Ultra AI',
  customFontFamily: '',
};

// Create the context with a default value
const ThemeContext = createContext<ThemeContextType>({
  theme: defaultTheme,
  branding: defaultBranding,
  setTheme: () => {},
  setBranding: () => {},
  resetToDefaults: () => {},
  toggleMode: () => {},
});

// Local storage keys
const THEME_STORAGE_KEY = 'ultraAI_theme_preferences';
const BRANDING_STORAGE_KEY = 'ultraAI_branding_options';

interface ThemeProviderProps {
  children: ReactNode;
  initialTheme?: Partial<ThemePreferences>;
  initialBranding?: Partial<BrandingOptions>;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({
  children,
  initialTheme = {},
  initialBranding = {},
}) => {
  // Get initial theme from localStorage or use defaults + passed props
  const getInitialTheme = (): ThemePreferences => {
    try {
      const storedTheme = localStorage.getItem(THEME_STORAGE_KEY);

      if (storedTheme) {
        // Merge stored theme with defaults to ensure all properties exist
        return { ...defaultTheme, ...JSON.parse(storedTheme), ...initialTheme };
      }

      // If no stored theme, check system preference for dark mode
      if (
        window.matchMedia &&
        window.matchMedia('(prefers-color-scheme: dark)').matches
      ) {
        return { ...defaultTheme, mode: 'dark', ...initialTheme };
      }

      return { ...defaultTheme, ...initialTheme };
    } catch (error) {
      console.error('Error loading theme from localStorage:', error);
      return { ...defaultTheme, ...initialTheme };
    }
  };

  // Get initial branding from localStorage
  const getInitialBranding = (): BrandingOptions => {
    try {
      const storedBranding = localStorage.getItem(BRANDING_STORAGE_KEY);

      if (storedBranding) {
        return {
          ...defaultBranding,
          ...JSON.parse(storedBranding),
          ...initialBranding,
        };
      }

      return { ...defaultBranding, ...initialBranding };
    } catch (error) {
      console.error('Error loading branding from localStorage:', error);
      return { ...defaultBranding, ...initialBranding };
    }
  };

  // State initialization
  const [theme, setThemeState] = useState<ThemePreferences>(getInitialTheme);
  const [branding, setBrandingState] =
    useState<BrandingOptions>(getInitialBranding);

  // Update theme handler
  const setTheme = (newTheme: Partial<ThemePreferences>) => {
    setThemeState((prevTheme) => {
      const updatedTheme = { ...prevTheme, ...newTheme };

      // Save to localStorage
      try {
        localStorage.setItem(THEME_STORAGE_KEY, JSON.stringify(updatedTheme));
      } catch (error) {
        console.error('Error saving theme to localStorage:', error);
      }

      return updatedTheme;
    });
  };

  // Update branding handler
  const setBranding = (newBranding: Partial<BrandingOptions>) => {
    setBrandingState((prevBranding) => {
      const updatedBranding = { ...prevBranding, ...newBranding };

      // Save to localStorage
      try {
        localStorage.setItem(
          BRANDING_STORAGE_KEY,
          JSON.stringify(updatedBranding)
        );
      } catch (error) {
        console.error('Error saving branding to localStorage:', error);
      }

      return updatedBranding;
    });
  };

  // Reset to defaults
  const resetToDefaults = () => {
    setThemeState(defaultTheme);
    setBrandingState(defaultBranding);

    // Clear localStorage
    try {
      localStorage.removeItem(THEME_STORAGE_KEY);
      localStorage.removeItem(BRANDING_STORAGE_KEY);
    } catch (error) {
      console.error('Error clearing theme from localStorage:', error);
    }
  };

  // Toggle between light and dark mode
  const toggleMode = () => {
    setTheme({ mode: theme.mode === 'light' ? 'dark' : 'light' });
  };

  // Listen for system theme preference changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleChange = (e: MediaQueryListEvent) => {
      // Only update if user hasn't explicitly set a preference
      if (!localStorage.getItem(THEME_STORAGE_KEY)) {
        setThemeState((prev) => ({
          ...prev,
          mode: e.matches ? 'dark' : 'light',
        }));
      }
    };

    mediaQuery.addEventListener('change', handleChange);

    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, []);

  // Apply CSS variables when theme changes
  useEffect(() => {
    // Add mode class to document
    document.documentElement.classList.remove('light', 'dark');
    document.documentElement.classList.add(theme.mode);

    // Add theme style class
    document.documentElement.classList.remove(
      'cyberpunk',
      'classic',
      'corporate'
    );
    document.documentElement.classList.add(theme.style);

    // Set reduced motion if enabled
    if (theme.reducedMotion) {
      document.documentElement.classList.add('reduced-motion');
    } else {
      document.documentElement.classList.remove('reduced-motion');
    }

    // Set font size
    document.documentElement.style.setProperty(
      '--font-size-factor',
      theme.fontSize.toString()
    );

    // Set contrast level
    document.documentElement.style.setProperty(
      '--contrast-level',
      theme.contrastLevel.toString()
    );

    // Apply accent color
    document.documentElement.style.setProperty(
      '--accent-h',
      getAccentHue(theme.accentColor)
    );

    // Apply branding
    if (branding.primaryColor) {
      document.documentElement.style.setProperty(
        '--brand-primary',
        branding.primaryColor
      );
    }
    if (branding.secondaryColor) {
      document.documentElement.style.setProperty(
        '--brand-secondary',
        branding.secondaryColor
      );
    }
    if (branding.customFontFamily) {
      document.documentElement.style.setProperty(
        '--font-family',
        branding.customFontFamily
      );
    }
  }, [theme, branding]);

  return (
    <ThemeContext.Provider
      value={{
        theme,
        branding,
        setTheme,
        setBranding,
        resetToDefaults,
        toggleMode,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
};

// Helper function to get hue value for different accent colors
function getAccentHue(accentColor: AccentColor): string {
  switch (accentColor) {
    case 'cyan':
      return '180';
    case 'purple':
      return '270';
    case 'orange':
      return '30';
    case 'green':
      return '120';
    case 'pink':
      return '330';
    default:
      return '180'; // Default to cyan
  }
}

// Custom hook for accessing the theme context
export const useTheme = () => useContext(ThemeContext);

export default ThemeContext;
