/**
 * Theme definitions for Ultra AI
 *
 * This file contains the CSS variable definitions for different themes.
 * These themes are applied through the ThemeProvider component.
 */

// Theme interfaces
export interface ThemeColors {
  background: string;
  foreground: string;
  card: string;
  cardForeground: string;
  popover: string;
  popoverForeground: string;
  primary: string;
  primaryForeground: string;
  secondary: string;
  secondaryForeground: string;
  muted: string;
  mutedForeground: string;
  accent: string;
  accentForeground: string;
  destructive: string;
  destructiveForeground: string;
  border: string;
  input: string;
  ring: string;
  // Theme-specific additional variables
  neonPrimary?: string;
  neonSecondary?: string;
  backdropFilter?: string;
  cardOpacity?: string;
}

// Shared values
const baseRadius = '0.5rem';
const baseFontFamily =
  'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

// Cyberpunk Dark Theme (Night)
export const cyberpunkDarkTheme: ThemeColors = {
  // Base colors
  background: '224 71% 4%', // Deep blue-black
  foreground: '213 31% 91%', // Bright white-blue

  // Card & popover
  card: '222 47% 11%', // Dark blue-gray
  cardForeground: '210 40% 98%', // Bright white
  popover: '224 71% 4%', // Same as background
  popoverForeground: '215 20.2% 65.1%', // Light gray-blue

  // Primary & secondary
  primary: '180 100% 60%', // Bright cyan (neon)
  primaryForeground: '220 47.4% 11.2%', // Dark blue
  secondary: '30 100% 60%', // Bright orange-gold
  secondaryForeground: '210 40% 98%', // Bright white

  // Supporting colors
  muted: '223 47% 11%', // Dark muted blue
  mutedForeground: '215.4 16.3% 56.9%', // Medium gray-blue
  accent: '270 100% 60%', // Vibrant purple
  accentForeground: '210 40% 98%', // Bright white
  destructive: '0 63% 31%', // Dark red
  destructiveForeground: '210 40% 98%', // Bright white

  // UI elements
  border: '216 34% 17%', // Dark border
  input: '216 34% 17%', // Dark input
  ring: '180 100% 50%', // Cyan ring

  // Theme-specific
  neonPrimary: '180 100% 60%', // Neon cyan
  neonSecondary: '30 100% 60%', // Neon orange-gold
  backdropFilter: 'blur(8px)',
  cardOpacity: '0.8',
};

// Cyberpunk Light Theme (Day)
export const cyberpunkLightTheme: ThemeColors = {
  // Base colors
  background: '210 40% 96.1%', // Light blue-gray
  foreground: '222.2 47.4% 11.2%', // Dark blue-gray

  // Card & popover
  card: '0 0% 100%', // White
  cardForeground: '222.2 47.4% 11.2%', // Dark blue-gray
  popover: '0 0% 100%', // White
  popoverForeground: '222.2 47.4% 11.2%', // Dark blue-gray

  // Primary & secondary
  primary: '270 80% 50%', // Vibrant purple (matching billboard in daytime mockup)
  primaryForeground: '210 40% 98%', // White
  secondary: '180 100% 50%', // Bright cyan
  secondaryForeground: '222.2 47.4% 11.2%', // Dark blue

  // Supporting colors
  muted: '210 40% 96.1%', // Light blue-gray
  mutedForeground: '215.4 16.3% 46.9%', // Medium gray
  accent: '262.1 83.3% 57.8%', // Purple
  accentForeground: '210 40% 98%', // White
  destructive: '0 84.2% 60.2%', // Bright red
  destructiveForeground: '210 40% 98%', // White

  // UI elements
  border: '214.3 31.8% 91.4%', // Light border
  input: '214.3 31.8% 91.4%', // Light input
  ring: '262.1 83.3% 57.8%', // Purple

  // Theme-specific
  neonPrimary: '270 80% 50%', // Purple (for daytime billboard)
  neonSecondary: '180 100% 50%', // Cyan text
  backdropFilter: 'blur(4px)',
  cardOpacity: '0.9',
};

// Corporate Theme - Dark
export const corporateDarkTheme: ThemeColors = {
  // Base colors
  background: '220 14% 12%', // Dark gray
  foreground: '0 0% 95%', // Off-white

  // Card & popover
  card: '220 13% 18%', // Dark gray
  cardForeground: '0 0% 95%', // Off-white
  popover: '220 13% 18%', // Dark gray
  popoverForeground: '0 0% 95%', // Off-white

  // Primary & secondary
  primary: '210 100% 50%', // Blue
  primaryForeground: '0 0% 98%', // White
  secondary: '210 40% 30%', // Dark blue
  secondaryForeground: '0 0% 98%', // White

  // Supporting colors
  muted: '220 13% 23%', // Slightly lighter gray
  mutedForeground: '220 10% 60%', // Medium gray
  accent: '210 40% 40%', // Medium blue
  accentForeground: '0 0% 98%', // White
  destructive: '0 70% 50%', // Red
  destructiveForeground: '0 0% 98%', // White

  // UI elements
  border: '220 13% 25%', // Border
  input: '220 13% 25%', // Input
  ring: '210 100% 50%', // Blue
};

// Corporate Theme - Light
export const corporateLightTheme: ThemeColors = {
  // Base colors
  background: '0 0% 98%', // Off-white
  foreground: '224 71% 4%', // Almost black

  // Card & popover
  card: '0 0% 100%', // White
  cardForeground: '224 71% 4%', // Almost black
  popover: '0 0% 100%', // White
  popoverForeground: '224 71% 4%', // Almost black

  // Primary & secondary
  primary: '210 100% 50%', // Blue
  primaryForeground: '0 0% 98%', // White
  secondary: '220 13% 91%', // Light gray
  secondaryForeground: '220 70% 40%', // Blue-gray

  // Supporting colors
  muted: '220 13% 95%', // Very light gray
  mutedForeground: '220 10% 40%', // Medium-dark gray
  accent: '220 13% 91%', // Light gray
  accentForeground: '220 70% 40%', // Blue-gray
  destructive: '0 70% 50%', // Red
  destructiveForeground: '0 0% 98%', // White

  // UI elements
  border: '220 13% 85%', // Light gray border
  input: '220 13% 85%', // Light gray input
  ring: '210 100% 50%', // Blue
};

// Classic Theme - Dark
export const classicDarkTheme: ThemeColors = {
  // Base colors
  background: '222.2 84% 4.9%', // Black
  foreground: '210 40% 98%', // White

  // Card & popover
  card: '222.2 84% 4.9%', // Black
  cardForeground: '210 40% 98%', // White
  popover: '222.2 84% 4.9%', // Black
  popoverForeground: '210 40% 98%', // White

  // Primary & secondary
  primary: '210 40% 98%', // White
  primaryForeground: '222.2 47.4% 11.2%', // Dark gray
  secondary: '217.2 32.6% 17.5%', // Dark gray
  secondaryForeground: '210 40% 98%', // White

  // Supporting colors
  muted: '217.2 32.6% 17.5%', // Dark gray
  mutedForeground: '215 20.2% 65.1%', // Light gray
  accent: '217.2 32.6% 17.5%', // Dark gray
  accentForeground: '210 40% 98%', // White
  destructive: '0 62.8% 30.6%', // Dark red
  destructiveForeground: '210 40% 98%', // White

  // UI elements
  border: '217.2 32.6% 17.5%', // Dark gray
  input: '217.2 32.6% 17.5%', // Dark gray
  ring: '212.7 26.8% 83.9%', // Light gray
};

// Classic Theme - Light
export const classicLightTheme: ThemeColors = {
  // Base colors
  background: '0 0% 100%', // White
  foreground: '222.2 84% 4.9%', // Black

  // Card & popover
  card: '0 0% 100%', // White
  cardForeground: '222.2 84% 4.9%', // Black
  popover: '0 0% 100%', // White
  popoverForeground: '222.2 84% 4.9%', // Black

  // Primary & secondary
  primary: '222.2 47.4% 11.2%', // Dark gray
  primaryForeground: '210 40% 98%', // White
  secondary: '210 40% 96.1%', // Light gray
  secondaryForeground: '222.2 47.4% 11.2%', // Dark gray

  // Supporting colors
  muted: '210 40% 96.1%', // Light gray
  mutedForeground: '215.4 16.3% 46.9%', // Medium gray
  accent: '210 40% 96.1%', // Light gray
  accentForeground: '222.2 47.4% 11.2%', // Dark gray
  destructive: '0 84.2% 60.2%', // Red
  destructiveForeground: '210 40% 98%', // White

  // UI elements
  border: '214.3 31.8% 91.4%', // Very light gray
  input: '214.3 31.8% 91.4%', // Very light gray
  ring: '222.2 84% 4.9%', // Black
};

// Export theme map
export const themeMap = {
  'cyberpunk-dark': cyberpunkDarkTheme,
  'cyberpunk-light': cyberpunkLightTheme,
  'corporate-dark': corporateDarkTheme,
  'corporate-light': corporateLightTheme,
  'classic-dark': classicDarkTheme,
  'classic-light': classicLightTheme,
};
