import React, { ReactNode, useEffect } from 'react';
import { ThemeProvider, useTheme, ThemeMode, ThemeStyle } from './ThemeContext';
import {
  themeMap,
  cyberpunkDarkTheme,
  cyberpunkLightTheme,
  corporateDarkTheme,
  corporateLightTheme,
  classicDarkTheme,
  classicLightTheme,
} from './theme-definitions';

interface ThemeRegistryProps {
  children: ReactNode;
}

/**
 * Applies the CSS variables for a given theme and mode
 */
const generateCssVariables = (theme: any, selector: string) => {
  let cssVars = '';

  // Convert HSL values in theme to CSS variables
  Object.entries(theme).forEach(([key, value]) => {
    if (
      typeof value === 'string' &&
      !key.includes('Filter') &&
      !key.includes('Opacity')
    ) {
      cssVars += `  --${key.replace(/([A-Z])/g, '-$1').toLowerCase()}: ${value};\n`;
    }
  });

  return `${selector} {\n${cssVars}}\n`;
};

/**
 * Generates the CSS styles for all themes
 */
const ThemeStyles = () => {
  // Generate CSS for all themes
  const themeStyles = `
  /* Base styles and CSS variables */
  :root {
    --font-size-factor: 1;
    --contrast-level: 3;
    --font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    --radius: 0.5rem;
    --brand-primary: #00FFFF;
    --brand-secondary: #FF9D00;

    /* Default transitions */
    --transition-standard: 0.2s ease;
    --transition-long: 0.5s ease;

    /* Animation properties for reduced motion preferences */
    --animation-duration: 0.5s;
    --animation-timing: ease;
  }

  /* Font size adjustments */
  html {
    font-size: calc(16px * var(--font-size-factor));
  }

  /* Reduced motion preference */
  @media (prefers-reduced-motion) {
    :root {
      --animation-duration: 0.001s;
      --animation-timing: step-end;
      --transition-standard: 0s;
      --transition-long: 0s;
    }
  }

  .reduced-motion * {
    transition-duration: 0.001s !important;
    animation-duration: 0.001s !important;
    transition-timing-function: step-end !important;
    animation-timing-function: step-end !important;
  }

  /* Neon text effect for cyberpunk theme */
  .cyberpunk .neon-text {
    text-shadow:
      0 0 5px hsl(var(--neon-primary)),
      0 0 10px hsl(var(--neon-primary)),
      0 0 20px hsl(var(--neon-primary)),
      0 0 40px hsl(var(--neon-primary));
    transition: text-shadow var(--transition-long);
  }

  .cyberpunk .neon-border {
    box-shadow:
      0 0 5px hsl(var(--neon-primary)),
      0 0 10px hsl(var(--neon-primary));
    border-color: hsl(var(--neon-primary));
  }

  .cyberpunk .neon-secondary {
    text-shadow:
      0 0 5px hsl(var(--neon-secondary)),
      0 0 10px hsl(var(--neon-secondary)),
      0 0 15px hsl(var(--neon-secondary));
  }

  /* Glass effect for cyberpunk theme */
  .cyberpunk .glass {
    background: linear-gradient(
      135deg,
      hsla(var(--background), 0.6) 0%,
      hsla(var(--background), 0.3) 100%
    );
    backdrop-filter: var(--backdrop-filter);
    -webkit-backdrop-filter: var(--backdrop-filter);
    border: 1px solid hsla(var(--border), 0.3);
  }

  /* Theme definitions */
  ${generateCssVariables(cyberpunkDarkTheme, '.dark.cyberpunk')}
  ${generateCssVariables(cyberpunkLightTheme, '.light.cyberpunk')}
  ${generateCssVariables(corporateDarkTheme, '.dark.corporate')}
  ${generateCssVariables(corporateLightTheme, '.light.corporate')}
  ${generateCssVariables(classicDarkTheme, '.dark.classic')}
  ${generateCssVariables(classicLightTheme, '.light.classic')}

  /* High contrast overrides for accessibility */
  .contrast-high {
    --contrast-level: 5;
    --border: 0 0% 0%;
    --foreground: 0 0% 0%;
    --background: 0 0% 100%;
    --primary: 210 100% 30%;
    --primary-foreground: 0 0% 100%;
    --secondary: 0 0% 0%;
    --secondary-foreground: 0 0% 100%;
  }

  .dark.contrast-high {
    --contrast-level: 5;
    --border: 0 0% 100%;
    --foreground: 0 0% 100%;
    --background: 0 0% 0%;
    --primary: 210 100% 70%;
    --primary-foreground: 0 0% 0%;
    --secondary: 0 0% 100%;
    --secondary-foreground: 0 0% 0%;
  }

  /* Custom accent color support */
  .accent-cyan {
    --accent: 180 100% 50%;
    --accent-foreground: 0 0% 0%;
    --neon-primary: 180 100% 60%;
  }

  .accent-purple {
    --accent: 270 100% 60%;
    --accent-foreground: 0 0% 100%;
    --neon-primary: 270 100% 70%;
  }

  .accent-orange {
    --accent: 30 100% 50%;
    --accent-foreground: 0 0% 0%;
    --neon-primary: 30 100% 60%;
  }

  .accent-green {
    --accent: 120 100% 40%;
    --accent-foreground: 0 0% 0%;
    --neon-primary: 120 100% 50%;
  }

  .accent-pink {
    --accent: 330 100% 60%;
    --accent-foreground: 0 0% 100%;
    --neon-primary: 330 100% 70%;
  }

  /* Branding overrides */
  .custom-brand {
    --primary: var(--brand-primary);
    --secondary: var(--brand-secondary);
  }
  `;

  return <style>{themeStyles}</style>;
};

/**
 * ThemeRegistry component that provides theme context and CSS variable definitions
 */
export const ThemeRegistry: React.FC<ThemeRegistryProps> = ({ children }) => {
  return (
    <ThemeProvider>
      <ThemeRegistryContent>{children}</ThemeRegistryContent>
    </ThemeProvider>
  );
};

/**
 * Internal content component that uses the theme context
 */
const ThemeRegistryContent: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const { theme } = useTheme();

  // Apply body classes when theme changes
  useEffect(() => {
    // Add contrast class if high contrast is enabled
    if (theme.contrastLevel >= 4) {
      document.body.classList.add('contrast-high');
    } else {
      document.body.classList.remove('contrast-high');
    }

    // Add accent color class
    document.body.classList.remove(
      'accent-cyan',
      'accent-purple',
      'accent-orange',
      'accent-green',
      'accent-pink'
    );
    document.body.classList.add(`accent-${theme.accentColor}`);
  }, [theme]);

  return (
    <>
      <ThemeStyles />
      {children}
    </>
  );
};

export default ThemeRegistry;
