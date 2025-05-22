# Buttons

## Overview

Button components in the UltraAI design system provide consistent interaction patterns across all themes. From cyberpunk neon effects to clean corporate styling, buttons maintain functional consistency while adapting to visual contexts.

## Button Variants

### Primary Button
The main call-to-action button, used for primary actions like "GENERATE", "SUBMIT", "CONFIRM".

```tsx
<Button variant="primary" size="lg">
  GENERATE
</Button>
```

#### Cyberpunk Theme
```css
.btn-primary-cyberpunk {
  background: linear-gradient(135deg, hsl(var(--neon-cyan)), hsl(var(--neon-cyan) / 0.8));
  color: hsl(var(--background));
  border: 2px solid hsl(var(--neon-cyan));
  font-family: 'Orbitron', monospace;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  box-shadow: 
    0 0 20px hsl(var(--neon-cyan) / 0.4),
    inset 0 1px 0 hsl(var(--neon-cyan) / 0.2);
  transition: all 0.2s ease;
}

.btn-primary-cyberpunk:hover {
  background: hsl(var(--neon-cyan));
  box-shadow: 
    0 0 30px hsl(var(--neon-cyan) / 0.6),
    0 0 40px hsl(var(--neon-cyan) / 0.3),
    inset 0 1px 0 hsl(var(--neon-cyan) / 0.3);
  transform: translateY(-1px);
}

.btn-primary-cyberpunk:active {
  transform: translateY(0);
  box-shadow: 
    0 0 15px hsl(var(--neon-cyan) / 0.5),
    inset 0 2px 4px hsl(var(--background) / 0.3);
}
```

#### Corporate Theme  
```css
.btn-primary-corporate {
  background: linear-gradient(135deg, hsl(var(--corporate-blue)), hsl(var(--corporate-blue) / 0.9));
  color: white;
  border: 1px solid hsl(var(--corporate-blue));
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  box-shadow: 0 2px 4px hsl(var(--corporate-blue) / 0.2);
  transition: all 0.2s ease;
}

.btn-primary-corporate:hover {
  background: hsl(var(--corporate-blue) / 0.9);
  box-shadow: 0 4px 8px hsl(var(--corporate-blue) / 0.3);
  transform: translateY(-1px);
}
```

### Secondary Button
Supporting actions, alternative choices, or less prominent actions.

```tsx
<Button variant="secondary" size="md">
  Cancel
</Button>
```

#### Cyberpunk Theme
```css
.btn-secondary-cyberpunk {
  background: transparent;
  color: hsl(var(--neon-cyan));
  border: 2px solid hsl(var(--neon-cyan) / 0.5);
  font-family: 'Orbitron', monospace;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  transition: all 0.2s ease;
}

.btn-secondary-cyberpunk:hover {
  background: hsl(var(--neon-cyan) / 0.1);
  border-color: hsl(var(--neon-cyan));
  box-shadow: 
    0 0 15px hsl(var(--neon-cyan) / 0.3),
    inset 0 0 15px hsl(var(--neon-cyan) / 0.1);
}
```

### Accent Button
Special actions using the orange accent color, often for destructive or warning actions.

```tsx
<Button variant="accent" size="md">
  Delete
</Button>
```

#### Cyberpunk Theme
```css
.btn-accent-cyberpunk {
  background: linear-gradient(135deg, hsl(var(--neon-orange)), hsl(var(--neon-orange) / 0.8));
  color: hsl(var(--background));
  border: 2px solid hsl(var(--neon-orange));
  font-family: 'Orbitron', monospace;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  box-shadow: 0 0 20px hsl(var(--neon-orange) / 0.4);
  transition: all 0.2s ease;
}

.btn-accent-cyberpunk:hover {
  box-shadow: 
    0 0 30px hsl(var(--neon-orange) / 0.6),
    0 0 40px hsl(var(--neon-orange) / 0.3);
}
```

### Ghost Button
Minimal button for subtle actions, often used in navigation or as tertiary actions.

```tsx
<Button variant="ghost" size="sm">
  Learn More
</Button>
```

## Button Sizes

### Size Specifications
```css
/* Large - Primary CTAs */
.btn-lg {
  padding: 16px 32px;
  font-size: 1.125rem;
  border-radius: 12px;
  min-height: 56px;
  min-width: 120px;
}

/* Medium - Standard actions */
.btn-md {
  padding: 12px 24px;
  font-size: 1rem;
  border-radius: 8px;
  min-height: 44px;
  min-width: 100px;
}

/* Small - Secondary actions */
.btn-sm {
  padding: 8px 16px;
  font-size: 0.875rem;
  border-radius: 6px;
  min-height: 36px;
  min-width: 80px;
}

/* Extra Small - Compact interfaces */
.btn-xs {
  padding: 6px 12px;
  font-size: 0.75rem;
  border-radius: 4px;
  min-height: 28px;
  min-width: 60px;
}
```

## Button States

### Loading State
```tsx
<Button variant="primary" loading>
  <Spinner size="sm" />
  Generating...
</Button>
```

```css
.btn-loading {
  position: relative;
  color: transparent;
}

.btn-loading::after {
  content: '';
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: currentColor;
  /* Spinner animation */
}
```

### Disabled State
```css
.btn-disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

/* Cyberpunk disabled state */
.btn-disabled.cyberpunk {
  background: hsl(var(--muted));
  color: hsl(var(--foreground-muted));
  border-color: hsl(var(--border));
  box-shadow: none;
  text-shadow: none;
}
```

### Focus State (Accessibility)
```css
.btn:focus-visible {
  outline: 2px solid hsl(var(--ring));
  outline-offset: 2px;
}

/* Cyberpunk focus with glow */
.btn-cyberpunk:focus-visible {
  outline: none;
  box-shadow: 
    0 0 0 2px hsl(var(--background)),
    0 0 0 4px hsl(var(--neon-cyan)),
    0 0 20px hsl(var(--neon-cyan) / 0.4);
}
```

## Icon Buttons

### Icon with Text
```tsx
<Button variant="primary">
  <UploadIcon size={16} />
  Upload Files
</Button>
```

### Icon Only
```tsx
<Button variant="ghost" size="sm" aria-label="Close">
  <XIcon size={16} />
</Button>
```

```css
.btn-icon-only {
  aspect-ratio: 1;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

## Button Groups

### Horizontal Group
```tsx
<ButtonGroup>
  <Button variant="primary">Save</Button>
  <Button variant="secondary">Save & Continue</Button>
  <Button variant="ghost">Cancel</Button>
</ButtonGroup>
```

```css
.btn-group {
  display: flex;
  gap: 8px;
}

.btn-group.connected {
  gap: 0;
}

.btn-group.connected .btn:not(:first-child) {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  margin-left: -1px;
}

.btn-group.connected .btn:not(:last-child) {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}
```

## Responsive Behavior

### Mobile Adaptations
```css
@media (max-width: 768px) {
  /* Full-width primary buttons on mobile */
  .btn-primary.btn-mobile-full {
    width: 100%;
    max-width: none;
  }
  
  /* Smaller padding on mobile */
  .btn-lg {
    padding: 14px 24px;
    font-size: 1rem;
  }
  
  /* Larger touch targets */
  .btn {
    min-height: 44px;
  }
}
```

### Touch Interactions
```css
/* Larger touch targets for mobile */
.btn-touch {
  min-height: 44px;
  min-width: 44px;
}

/* Haptic feedback simulation */
.btn:active {
  transform: scale(0.98);
}
```

## Animation Examples

### Cyberpunk Button Hover Animation
```css
@keyframes neon-btn-hover {
  0% {
    box-shadow: 0 0 20px hsl(var(--neon-cyan) / 0.4);
  }
  50% {
    box-shadow: 
      0 0 30px hsl(var(--neon-cyan) / 0.6),
      0 0 40px hsl(var(--neon-cyan) / 0.3);
  }
  100% {
    box-shadow: 0 0 20px hsl(var(--neon-cyan) / 0.4);
  }
}

.btn-cyberpunk:hover {
  animation: neon-btn-hover 1s ease-in-out infinite;
}
```

### Loading Spinner
```css
@keyframes btn-spinner {
  to {
    transform: rotate(360deg);
  }
}

.btn-spinner {
  animation: btn-spinner 1s linear infinite;
}
```

## Implementation Example

```tsx
import React from 'react';
import { useTheme } from '../theme/ThemeContext';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'accent' | 'ghost';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  children,
  onClick,
  className = ''
}) => {
  const { theme } = useTheme();
  
  const baseClasses = 'btn transition-all duration-200 focus:outline-none focus-visible:ring-2';
  const variantClasses = {
    primary: `btn-${variant}-${theme.style}`,
    secondary: `btn-${variant}-${theme.style}`,
    accent: `btn-${variant}-${theme.style}`,
    ghost: `btn-${variant}-${theme.style}`
  };
  const sizeClasses = `btn-${size}`;
  const stateClasses = {
    loading: loading ? 'btn-loading' : '',
    disabled: disabled ? 'btn-disabled' : ''
  };
  
  const allClasses = [
    baseClasses,
    variantClasses[variant],
    sizeClasses,
    stateClasses.loading,
    stateClasses.disabled,
    className
  ].filter(Boolean).join(' ');
  
  return (
    <button
      className={allClasses}
      onClick={onClick}
      disabled={disabled || loading}
      aria-disabled={disabled || loading}
    >
      {loading ? (
        <>
          <span className="btn-spinner">⟳</span>
          Loading...
        </>
      ) : (
        children
      )}
    </button>
  );
};

export default Button;
```

---

**Next**: Review [Forms](./forms.md) for input and form component specifications.