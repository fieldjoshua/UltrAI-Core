/**
 * UltrAI Design Tokens System
 * Consistent design values across the application
 */

export const tokens = {
  // Spacing Scale (4px base)
  spacing: {
    none: '0',
    xs: '0.25rem', // 4px
    sm: '0.5rem', // 8px
    md: '1rem', // 16px
    lg: '1.5rem', // 24px
    xl: '2rem', // 32px
    '2xl': '3rem', // 48px
    '3xl': '4rem', // 64px
    '4xl': '6rem', // 96px
  },

  // Typography Scale
  typography: {
    fontFamily: {
      cyber: ['Orbitron', 'sans-serif'],
      mono: ['Share Tech Mono', 'monospace'],
      sans: ['Inter', 'system-ui', 'sans-serif'],
    },
    fontSize: {
      xs: { size: '0.75rem', lineHeight: '1rem' }, // 12px
      sm: { size: '0.875rem', lineHeight: '1.25rem' }, // 14px
      base: { size: '1rem', lineHeight: '1.5rem' }, // 16px
      lg: { size: '1.125rem', lineHeight: '1.75rem' }, // 18px
      xl: { size: '1.25rem', lineHeight: '1.75rem' }, // 20px
      '2xl': { size: '1.5rem', lineHeight: '2rem' }, // 24px
      '3xl': { size: '1.875rem', lineHeight: '2.25rem' }, // 30px
      '4xl': { size: '2.25rem', lineHeight: '2.5rem' }, // 36px
      '5xl': { size: '3rem', lineHeight: '1' }, // 48px
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
      extrabold: 800,
    },
    letterSpacing: {
      tighter: '-0.05em',
      tight: '-0.025em',
      normal: '0',
      wide: '0.025em',
      wider: '0.05em',
      widest: '0.1em',
      ultra: '0.35em', // For ULTRA SYNTHESIS™ style text
    },
  },

  // Border Radius
  borderRadius: {
    none: '0',
    sm: '0.25rem', // 4px
    base: '0.5rem', // 8px
    md: '0.75rem', // 12px
    lg: '1rem', // 16px
    xl: '1.5rem', // 24px
    '2xl': '2rem', // 32px
    full: '9999px',
  },

  // Shadows
  shadows: {
    none: 'none',
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    glass:
      '0 8px 32px rgba(0, 0, 0, 0.3), inset 0 0 40px rgba(255, 255, 255, 0.02)',
    neon: (color: string) => `0 0 20px ${color}, 0 0 40px ${color}20`,
  },

  // Animation Durations
  duration: {
    instant: '0ms',
    fast: '150ms',
    base: '300ms',
    slow: '500ms',
    slower: '700ms',
    slowest: '1000ms',
  },

  // Animation Easings
  easing: {
    linear: 'linear',
    ease: 'ease',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  },

  // Z-Index Scale
  zIndex: {
    base: 0,
    dropdown: 10,
    sticky: 20,
    fixed: 30,
    overlay: 40,
    modal: 50,
    popover: 60,
    tooltip: 70,
    notification: 80,
    max: 9999,
  },

  // Breakpoints
  breakpoints: {
    xs: '375px',
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },

  // Component-specific tokens
  components: {
    button: {
      height: {
        sm: '2.5rem', // 40px
        base: '2.75rem', // 44px (touch target)
        lg: '3rem', // 48px
      },
      padding: {
        sm: '0.75rem 1rem',
        base: '1rem 1.5rem',
        lg: '1.25rem 2rem',
      },
    },
    input: {
      height: '2.75rem', // 44px (touch target)
      padding: '0.75rem 1rem',
      borderWidth: '2px',
    },
    card: {
      padding: {
        sm: '1rem',
        base: '1.5rem',
        lg: '2rem',
      },
    },
    modal: {
      width: {
        sm: '24rem', // 384px
        base: '32rem', // 512px
        lg: '48rem', // 768px
        xl: '64rem', // 1024px
      },
    },
  },

  // Glass morphism styles
  glass: {
    light: {
      background: 'rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(20px) saturate(180%)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
    },
    medium: {
      background: 'rgba(0, 0, 0, 0.3)',
      backdropFilter: 'blur(30px) saturate(180%)',
      border: '1px solid rgba(255, 255, 255, 0.3)',
    },
    dark: {
      background: 'rgba(0, 0, 0, 0.6)',
      backdropFilter: 'blur(40px) saturate(180%)',
      border: '2px solid rgba(255, 255, 255, 0.4)',
    },
  },
};

// Helper functions
export const space = (key: keyof typeof tokens.spacing) => tokens.spacing[key];
export const fontSize = (key: keyof typeof tokens.typography.fontSize) =>
  tokens.typography.fontSize[key];
export const shadow = (
  key: keyof typeof tokens.shadows | 'neon',
  color?: string
) => {
  if (key === 'neon' && color) {
    return tokens.shadows.neon(color);
  }
  return tokens.shadows[key as keyof typeof tokens.shadows];
};
export const radius = (key: keyof typeof tokens.borderRadius) =>
  tokens.borderRadius[key];
export const duration = (key: keyof typeof tokens.duration) =>
  tokens.duration[key];

// Type exports
export type SpacingKey = keyof typeof tokens.spacing;
export type FontSizeKey = keyof typeof tokens.typography.fontSize;
export type BorderRadiusKey = keyof typeof tokens.borderRadius;
export type DurationKey = keyof typeof tokens.duration;
export type BreakpointKey = keyof typeof tokens.breakpoints;
