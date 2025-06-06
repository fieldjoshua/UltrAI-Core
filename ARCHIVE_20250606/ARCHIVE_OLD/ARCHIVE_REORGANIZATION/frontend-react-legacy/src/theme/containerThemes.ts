import { ContainerStyleConfig } from '../components/universal/UniversalContainer';

/**
 * Container theme collection
 */
export interface ContainerThemeCollection {
  [themeName: string]: {
    primary: ContainerStyleConfig;
    secondary: ContainerStyleConfig;
    progress: ContainerStyleConfig;
    alert: ContainerStyleConfig;
    modal: ContainerStyleConfig;
    card: ContainerStyleConfig;
  };
}

/**
 * Predefined container themes for rapid UI customization
 */
export const containerThemes: ContainerThemeCollection = {
  /**
   * High-tech cyberpunk-inspired theme with neon accents and floating elements
   */
  cyberpunk: {
    primary: {
      baseStyle: 'bg-gray-900/80 backdrop-blur-md',
      gradientFrom: '#1a1a2e',
      gradientTo: '#16213e',
      accentColor: 'cyan',
      borderStyle: 'neon',
      borderWidth: 'thin',
      glassEffect: 'medium',
      transparency: 'medium',
      animation: 'glow',
      decorativeElements: {
        neonTrim: true,
        holographicDisplay: true,
      },
      positionStyle: 'detached',
      orientation: 'front-facing',
    },
    secondary: {
      baseStyle: 'bg-gray-900/70 backdrop-blur-md',
      gradientFrom: '#16213e',
      gradientTo: '#1a1a2e',
      accentColor: 'magenta',
      borderStyle: 'neon',
      borderWidth: 'thin',
      glassEffect: 'medium',
      transparency: 'medium',
      animation: 'float',
      decorativeElements: {
        drones: true,
        neonTrim: true,
      },
      positionStyle: 'offset-left',
      orientation: 'front-facing',
    },
    progress: {
      baseStyle: 'bg-gray-900/60 backdrop-blur-md',
      accentColor: 'cyan',
      borderStyle: 'neon',
      borderWidth: 'thin',
      glassEffect: 'light',
      transparency: 'heavy',
      animation: 'float',
      decorativeElements: {
        drones: true,
        neonTrim: true,
      },
      positionStyle: 'offset-left',
      orientation: 'front-facing',
    },
    alert: {
      baseStyle: 'bg-gray-900/90 backdrop-blur-md',
      accentColor: 'magenta',
      borderStyle: 'neon',
      borderWidth: 'medium',
      glassEffect: 'light',
      transparency: 'light',
      animation: 'pulse',
      decorativeElements: {
        neonTrim: true,
      },
      positionStyle: 'centered',
      orientation: 'front-facing',
    },
    modal: {
      baseStyle: 'bg-gray-900/80 backdrop-blur-md',
      gradientFrom: '#1a1a2e',
      gradientTo: '#16213e',
      accentColor: 'cyan',
      borderStyle: 'neon',
      borderWidth: 'medium',
      glassEffect: 'medium',
      transparency: 'medium',
      animation: 'none',
      decorativeElements: {
        neonTrim: true,
        holographicDisplay: true,
      },
      positionStyle: 'centered',
      orientation: 'front-facing',
    },
    card: {
      baseStyle: 'bg-gray-900/70 backdrop-blur-md',
      accentColor: 'cyan',
      borderStyle: 'neon',
      borderWidth: 'thin',
      glassEffect: 'light',
      transparency: 'medium',
      animation: 'none',
      decorativeElements: {
        neonTrim: true,
      },
      positionStyle: 'centered',
      orientation: 'front-facing',
    },
  },

  /**
   * Futuristic clean interface with holographic elements and soft gradients
   */
  futuristic: {
    primary: {
      baseStyle: 'bg-indigo-900/40 backdrop-blur-md',
      gradientFrom: '#2c3e50',
      gradientTo: '#4a69bd',
      accentColor: 'cyan',
      borderStyle: 'solid',
      borderWidth: 'thin',
      glassEffect: 'heavy',
      transparency: 'medium',
      animation: 'none',
      decorativeElements: {
        holographicDisplay: true,
      },
      positionStyle: 'centered',
      orientation: 'front-facing',
    },
    secondary: {
      baseStyle: 'bg-indigo-900/30 backdrop-blur-md',
      gradientFrom: '#4a69bd',
      gradientTo: '#2c3e50',
      accentColor: 'cyan',
      borderStyle: 'solid',
      borderWidth: 'thin',
      glassEffect: 'heavy',
      transparency: 'heavy',
      animation: 'float',
      decorativeElements: {
        holographicDisplay: true,
      },
      positionStyle: 'offset-left',
      orientation: 'front-facing',
    },
    progress: {
      baseStyle: 'bg-indigo-900/20 backdrop-blur-md',
      accentColor: 'cyan',
      borderStyle: 'solid',
      borderWidth: 'thin',
      glassEffect: 'heavy',
      transparency: 'heavy',
      animation: 'float',
      decorativeElements: {
        holographicDisplay: true,
      },
      positionStyle: 'offset-left',
      orientation: 'front-facing',
    },
    alert: {
      baseStyle: 'bg-indigo-900/50 backdrop-blur-md',
      accentColor: 'cyan',
      borderStyle: 'solid',
      borderWidth: 'thin',
      glassEffect: 'medium',
      transparency: 'medium',
      animation: 'pulse',
      decorativeElements: {
        holographicDisplay: true,
      },
      positionStyle: 'centered',
      orientation: 'front-facing',
    },
    modal: {
      baseStyle: 'bg-indigo-900/40 backdrop-blur-md',
      gradientFrom: '#2c3e50',
      gradientTo: '#4a69bd',
      accentColor: 'cyan',
      borderStyle: 'solid',
      borderWidth: 'thin',
      glassEffect: 'heavy',
      transparency: 'medium',
      animation: 'none',
      decorativeElements: {
        holographicDisplay: true,
      },
      positionStyle: 'centered',
      orientation: 'front-facing',
    },
    card: {
      baseStyle: 'bg-indigo-900/30 backdrop-blur-md',
      accentColor: 'cyan',
      borderStyle: 'solid',
      borderWidth: 'thin',
      glassEffect: 'heavy',
      transparency: 'medium',
      animation: 'none',
      decorativeElements: {
        holographicDisplay: true,
      },
      positionStyle: 'centered',
      orientation: 'front-facing',
    },
  },

  /**
   * Corporate clean design with minimal accents and professional appearance
   */
  corporate: {
    primary: {
      baseStyle: 'bg-white dark:bg-gray-800',
      gradientFrom: '#ffffff',
      gradientTo: '#f8f9fa',
      accentColor: 'blue',
      borderStyle: 'solid',
      borderWidth: 'thin',
      glassEffect: 'none',
      transparency: 'none',
      animation: 'none',
      decorativeElements: {},
      positionStyle: 'centered',
      orientation: 'front-facing',
    },
    secondary: {
      baseStyle: 'bg-gray-50 dark:bg-gray-850',
      accentColor: 'blue',
      borderStyle: 'solid',
      borderWidth: 'thin',
      glassEffect: 'none',
      transparency: 'none',
      animation: 'none',
      decorativeElements: {},
      positionStyle: 'centered',
      orientation: 'front-facing',
    },
    progress: {
      baseStyle: 'bg-gray-100 dark:bg-gray-750',
      accentColor: 'blue',
      borderStyle: 'solid',
      borderWidth: 'thin',
      glassEffect: 'none',
      transparency: 'none',
      animation: 'none',
      decorativeElements: {},
      positionStyle: 'centered',
      orientation: 'front-facing',
    },
    alert: {
      baseStyle: 'bg-white dark:bg-gray-800',
      accentColor: 'blue',
      borderStyle: 'solid',
      borderWidth: 'thin',
      glassEffect: 'none',
      transparency: 'none',
      animation: 'none',
      decorativeElements: {},
      positionStyle: 'centered',
      orientation: 'front-facing',
    },
    modal: {
      baseStyle: 'bg-white dark:bg-gray-800',
      accentColor: 'blue',
      borderStyle: 'solid',
      borderWidth: 'thin',
      glassEffect: 'none',
      transparency: 'none',
      animation: 'none',
      decorativeElements: {},
      positionStyle: 'centered',
      orientation: 'front-facing',
    },
    card: {
      baseStyle: 'bg-white dark:bg-gray-800',
      accentColor: 'blue',
      borderStyle: 'solid',
      borderWidth: 'thin',
      glassEffect: 'none',
      transparency: 'none',
      animation: 'none',
      decorativeElements: {},
      positionStyle: 'centered',
      orientation: 'front-facing',
    },
  },

  /**
   * Sci-fi virtual reality theme with holographic displays and energy fields
   */
  virtualReality: {
    primary: {
      baseStyle: 'bg-blue-900/30 backdrop-blur-lg',
      gradientFrom: '#051937',
      gradientTo: '#004d7a',
      accentColor: 'cyan',
      borderStyle: 'neon',
      borderWidth: 'thin',
      glassEffect: 'heavy',
      transparency: 'medium',
      animation: 'glow',
      decorativeElements: {
        holographicDisplay: true,
        neonTrim: true,
      },
      positionStyle: 'detached',
      orientation: 'angled',
    },
    secondary: {
      baseStyle: 'bg-blue-900/20 backdrop-blur-lg',
      gradientFrom: '#004d7a',
      gradientTo: '#008793',
      accentColor: 'cyan',
      borderStyle: 'neon',
      borderWidth: 'thin',
      glassEffect: 'heavy',
      transparency: 'heavy',
      animation: 'float',
      decorativeElements: {
        holographicDisplay: true,
        drones: true,
      },
      positionStyle: 'offset-left',
      orientation: 'angled',
    },
    progress: {
      baseStyle: 'bg-blue-900/15 backdrop-blur-lg',
      accentColor: 'cyan',
      borderStyle: 'neon',
      borderWidth: 'thin',
      glassEffect: 'heavy',
      transparency: 'heavy',
      animation: 'float',
      decorativeElements: {
        drones: true,
      },
      positionStyle: 'offset-left',
      orientation: 'front-facing',
    },
    alert: {
      baseStyle: 'bg-blue-900/40 backdrop-blur-lg',
      accentColor: 'cyan',
      borderStyle: 'neon',
      borderWidth: 'thin',
      glassEffect: 'medium',
      transparency: 'medium',
      animation: 'pulse',
      decorativeElements: {
        holographicDisplay: true,
      },
      positionStyle: 'centered',
      orientation: 'front-facing',
    },
    modal: {
      baseStyle: 'bg-blue-900/30 backdrop-blur-lg',
      gradientFrom: '#051937',
      gradientTo: '#004d7a',
      accentColor: 'cyan',
      borderStyle: 'neon',
      borderWidth: 'thin',
      glassEffect: 'heavy',
      transparency: 'medium',
      animation: 'none',
      decorativeElements: {
        holographicDisplay: true,
        neonTrim: true,
      },
      positionStyle: 'centered',
      orientation: 'front-facing',
    },
    card: {
      baseStyle: 'bg-blue-900/20 backdrop-blur-lg',
      accentColor: 'cyan',
      borderStyle: 'neon',
      borderWidth: 'thin',
      glassEffect: 'heavy',
      transparency: 'medium',
      animation: 'none',
      decorativeElements: {
        neonTrim: true,
      },
      positionStyle: 'centered',
      orientation: 'front-facing',
    },
  },
};

/**
 * Helper function to get a container theme
 */
export const getContainerTheme = (
  themeName: string = 'cyberpunk',
  containerType: keyof ContainerThemeCollection['cyberpunk'] = 'primary'
): ContainerStyleConfig => {
  // Default to cyberpunk theme if requested theme doesn't exist
  const theme = containerThemes[themeName] || containerThemes.cyberpunk;
  return theme[containerType];
};

export default containerThemes;
