import React, { ReactNode } from 'react';
import { cn } from '../../lib/utils';
import { useTheme } from '../../theme/ThemeContext';

/**
 * Style configuration for container appearance
 */
export interface ContainerStyleConfig {
  // Base appearance
  baseStyle: string;
  // Gradient colors
  gradientFrom?: string;
  gradientTo?: string;
  // Border/accent styling
  accentColor?: string;
  borderStyle?: 'solid' | 'dashed' | 'neon' | 'none';
  borderWidth?: 'thin' | 'medium' | 'thick';
  // Glass/blur effects
  glassEffect?: 'none' | 'light' | 'medium' | 'heavy';
  transparency?: 'none' | 'light' | 'medium' | 'heavy';
  // Animation effects
  animation?: 'none' | 'float' | 'pulse' | 'glow';
  // Custom elements
  decorativeElements?: {
    drones?: boolean;
    neonTrim?: boolean;
    holographicDisplay?: boolean;
  };
  // Position and alignment
  positionStyle?: 'centered' | 'offset-left' | 'offset-right' | 'detached';
  orientation?: 'front-facing' | 'angled';
}

/**
 * Container variations
 */
export type ContainerVariant =
  | 'primary' // Main interaction panel
  | 'secondary' // Supporting information
  | 'progress' // Progress tracker
  | 'alert' // Notifications
  | 'modal' // Overlays
  | 'card'; // Content cards

/**
 * Container sizes
 */
export type ContainerSize = 'sm' | 'md' | 'lg' | 'xl' | 'full';

/**
 * Props for the UniversalContainer component
 */
export interface UniversalContainerProps {
  children: ReactNode;
  variant?: ContainerVariant;
  size?: ContainerSize;
  className?: string;
  styleConfig?: Partial<ContainerStyleConfig>;
  isFloating?: boolean;
  hasDropShadow?: boolean;
  isInteractive?: boolean;
  animationLevel?: 'none' | 'subtle' | 'moderate' | 'high';
  id?: string;
}

/**
 * Universal UI Container that can be skinned in different visual styles
 * while maintaining consistent functional elements
 */
const UniversalContainer: React.FC<UniversalContainerProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  styleConfig = {},
  isFloating = false,
  hasDropShadow = true,
  isInteractive = true,
  animationLevel = 'subtle',
  id,
}) => {
  const { theme } = useTheme();

  // Base size classes
  const sizeClasses = {
    sm: 'max-w-sm p-4',
    md: 'max-w-md p-5',
    lg: 'max-w-lg p-6',
    xl: 'max-w-xl p-6',
    full: 'w-full p-6',
  };

  // Base variant classes - functional structure independent of theme
  const variantClasses = {
    primary: 'rounded-lg flex flex-col gap-4',
    secondary: 'rounded-lg flex flex-col gap-3',
    progress: 'rounded-lg flex flex-col gap-2',
    alert: 'rounded-md flex items-center gap-3',
    modal: 'rounded-xl flex flex-col gap-4',
    card: 'rounded-md flex flex-col gap-2',
  };

  // Theme-specific style application - these would come from the theme system
  // and blend with the styleConfig prop for custom instances
  const getThemeStyles = () => {
    // Default cyberpunk-inspired style
    if (theme.style === 'cyberpunk') {
      const isDark = theme.mode === 'dark';

      const accentColor =
        styleConfig.accentColor ||
        (theme.accentColor === 'cyan'
          ? 'cyan'
          : theme.accentColor === 'purple'
            ? 'purple'
            : theme.accentColor === 'pink'
              ? 'pink'
              : 'cyan');

      // Neon glow effects based on accent color
      const glowEffects = {
        cyan: isDark
          ? 'shadow-[0_0_15px_rgba(0,255,255,0.3)]'
          : 'shadow-[0_0_10px_rgba(0,210,255,0.15)]',
        purple: isDark
          ? 'shadow-[0_0_15px_rgba(155,0,255,0.3)]'
          : 'shadow-[0_0_10px_rgba(155,0,255,0.15)]',
        pink: isDark
          ? 'shadow-[0_0_15px_rgba(255,0,170,0.3)]'
          : 'shadow-[0_0_10px_rgba(255,0,170,0.15)]',
      };

      // Border effects based on accent color
      const borderEffects = {
        cyan: isDark ? 'border-cyan-500/40' : 'border-cyan-600/30',
        purple: isDark ? 'border-purple-500/40' : 'border-purple-600/30',
        pink: isDark ? 'border-pink-500/40' : 'border-pink-600/30',
      };

      // Glass effects based on dark/light mode
      const glassEffect = isDark
        ? 'bg-gray-900/70 backdrop-blur-md'
        : 'bg-white/70 backdrop-blur-md';

      // Combine effects based on styleConfig and theme
      return cn(
        // Base glass effect
        glassEffect,
        // Border styling
        'border border-t-0 border-l-1 border-r-1 border-b-2',
        borderEffects[accentColor as keyof typeof borderEffects] ||
          borderEffects.cyan,
        // Glow effects if enabled
        hasDropShadow
          ? glowEffects[accentColor as keyof typeof glowEffects] ||
              glowEffects.cyan
          : '',
        // Animation classes
        isFloating && animationLevel !== 'none' ? 'animate-float' : '',
        // Additional interactive behaviors
        isInteractive ? 'transition-all duration-300 hover:shadow-lg' : ''
      );
    }

    // Corporate clean style
    else if (theme.style === 'corporate') {
      const isDark = theme.mode === 'dark';

      return cn(
        // Base style
        isDark ? 'bg-gray-800/95' : 'bg-white/95',
        // Border styling
        'border',
        isDark ? 'border-gray-700' : 'border-gray-200',
        // Shadow
        hasDropShadow
          ? isDark
            ? 'shadow-md shadow-black/20'
            : 'shadow-md shadow-black/10'
          : ''
      );
    }

    // Default/classic style
    else {
      const isDark = theme.mode === 'dark';

      return cn(
        // Base style
        isDark ? 'bg-gray-900' : 'bg-white',
        // Border styling
        'border',
        isDark ? 'border-gray-800' : 'border-gray-100',
        // Shadow
        hasDropShadow ? (isDark ? 'shadow-lg' : 'shadow-md') : ''
      );
    }
  };

  // Decorative elements based on theme and config
  const renderDecorativeElements = () => {
    if (theme.style !== 'cyberpunk' || !styleConfig.decorativeElements)
      return null;

    return (
      <>
        {/* Drone attachments for floating panels */}
        {styleConfig.decorativeElements.drones && isFloating && (
          <>
            <div className="absolute -top-4 -left-4 w-8 h-8 opacity-80">
              <div className="relative w-full h-full">
                <div className="absolute inset-0 animate-pulse-slow bg-cyan-500 rounded-full w-2 h-2 left-3 top-3" />
                <svg
                  viewBox="0 0 24 24"
                  className="absolute inset-0"
                  stroke="currentColor"
                  fill="none"
                >
                  <path
                    d="M12 4v2m0 12v2M4 12h2m12 0h2"
                    strokeWidth="1"
                    className="text-cyan-500"
                  />
                  <circle
                    cx="12"
                    cy="12"
                    r="4"
                    strokeWidth="1"
                    className="text-gray-400"
                  />
                  <circle
                    cx="12"
                    cy="12"
                    r="8"
                    strokeWidth="1"
                    strokeDasharray="2 2"
                    className="text-gray-600"
                  />
                </svg>
              </div>
            </div>

            <div className="absolute -top-4 -right-4 w-8 h-8 opacity-80">
              <div className="relative w-full h-full">
                <div className="absolute inset-0 animate-pulse-slow bg-pink-500 rounded-full w-2 h-2 right-3 top-3" />
                <svg
                  viewBox="0 0 24 24"
                  className="absolute inset-0"
                  stroke="currentColor"
                  fill="none"
                >
                  <path
                    d="M12 4v2m0 12v2M4 12h2m12 0h2"
                    strokeWidth="1"
                    className="text-pink-500"
                  />
                  <circle
                    cx="12"
                    cy="12"
                    r="4"
                    strokeWidth="1"
                    className="text-gray-400"
                  />
                  <circle
                    cx="12"
                    cy="12"
                    r="8"
                    strokeWidth="1"
                    strokeDasharray="2 2"
                    className="text-gray-600"
                  />
                </svg>
              </div>
            </div>
          </>
        )}

        {/* Neon trim effects */}
        {styleConfig.decorativeElements.neonTrim && (
          <div className="absolute inset-0 pointer-events-none">
            <div
              className={cn(
                'absolute top-0 left-8 right-8 h-px opacity-70',
                theme.accentColor === 'cyan'
                  ? 'bg-gradient-to-r from-transparent via-cyan-400 to-transparent'
                  : theme.accentColor === 'purple'
                    ? 'bg-gradient-to-r from-transparent via-purple-400 to-transparent'
                    : 'bg-gradient-to-r from-transparent via-pink-400 to-transparent'
              )}
            />
          </div>
        )}

        {/* Holographic display elements */}
        {styleConfig.decorativeElements.holographicDisplay && (
          <div className="absolute top-1 right-3 flex space-x-1 opacity-60">
            <div className="w-1 h-1 rounded-full bg-red-500"></div>
            <div className="w-1 h-1 rounded-full bg-green-500"></div>
            <div className="w-1 h-1 rounded-full bg-blue-500"></div>
          </div>
        )}
      </>
    );
  };

  return (
    <div
      id={id}
      className={cn(
        // Functional base classes
        'relative',
        sizeClasses[size],
        variantClasses[variant],
        // Apply theme-specific styling
        getThemeStyles(),
        // Additional custom classes
        className
      )}
    >
      {renderDecorativeElements()}
      {children}
    </div>
  );
};

export default UniversalContainer;
