import { configureAxe } from 'jest-axe';

// Configure axe for your specific accessibility needs
export const axe = configureAxe({
  rules: {
    // Specify which rules to run
    'color-contrast': { enabled: true },
    'image-alt': { enabled: true },
    label: { enabled: true },
    'frame-title': { enabled: true },
    'aria-allowed-attr': { enabled: true },
    'aria-required-attr': { enabled: true },
    'aria-required-children': { enabled: true },
    'aria-required-parent': { enabled: true },
    'aria-valid-attr': { enabled: true },
    'aria-valid-attr-value': { enabled: false }, // Disabled due to dynamic values
  },
});
