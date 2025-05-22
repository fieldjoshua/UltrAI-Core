# Typography

## Overview

The UltraAI typography system balances futuristic aesthetics with functional readability. The system uses a primary monospace family for brand elements and technical content, with careful hierarchy and spacing for optimal user experience.

## Font Families

### Primary: Orbitron
**Usage**: Brand text, headlines, cyberpunk theme emphasis
```css
font-family: 'Orbitron', 'JetBrains Mono', monospace;
```
- **Weights**: 400 (Regular), 600 (Semi-bold), 700 (Bold), 800 (Extra-bold)
- **Style**: Futuristic, geometric, high-tech
- **Character Set**: Extended Latin, numbers, symbols
- **Best For**: Logos, headlines, call-to-action buttons

### Secondary: JetBrains Mono  
**Usage**: Code, technical content, fallback
```css
font-family: 'JetBrains Mono', monospace;
```
- **Weights**: 400 (Regular), 500 (Medium), 600 (Semi-bold), 700 (Bold)
- **Style**: Developer-focused, highly readable
- **Features**: Ligatures, clear character distinction
- **Best For**: Code blocks, data tables, technical specifications

### System Fallback
**Usage**: Accessibility fallback, reduced data scenarios
```css
font-family: ui-monospace, 'Courier New', monospace;
```

## Typography Scale

### Heading Hierarchy
```css
/* H1 - Page titles, brand statements */
.text-6xl {
  font-size: clamp(3rem, 8vw, 6rem);      /* 48-96px */
  line-height: 1.1;
  font-weight: 700;
  letter-spacing: 0.1em;
}

/* H2 - Section headers */
.text-4xl {
  font-size: clamp(2rem, 5vw, 3.5rem);    /* 32-56px */
  line-height: 1.15;
  font-weight: 600;
  letter-spacing: 0.05em;
}

/* H3 - Subsection headers */
.text-2xl {
  font-size: clamp(1.5rem, 3vw, 2rem);    /* 24-32px */
  line-height: 1.2;
  font-weight: 600;
  letter-spacing: 0.025em;
}

/* H4 - Component titles */
.text-xl {
  font-size: clamp(1.25rem, 2vw, 1.5rem); /* 20-24px */
  line-height: 1.25;
  font-weight: 500;
  letter-spacing: 0.015em;
}

/* H5 - Small titles */
.text-lg {
  font-size: 1.125rem;                     /* 18px */
  line-height: 1.3;
  font-weight: 500;
  letter-spacing: 0.01em;
}

/* H6 - Micro titles */
.text-base {
  font-size: 1rem;                         /* 16px */
  line-height: 1.4;
  font-weight: 500;
}
```

### Body Text
```css
/* Large body text */
.text-lg-body {
  font-size: 1.125rem;   /* 18px */
  line-height: 1.6;
  font-weight: 400;
  font-family: 'JetBrains Mono', monospace;
}

/* Default body text */
.text-base-body {
  font-size: 1rem;       /* 16px */
  line-height: 1.6;
  font-weight: 400;
  font-family: 'JetBrains Mono', monospace;
}

/* Small body text */
.text-sm-body {
  font-size: 0.875rem;   /* 14px */
  line-height: 1.5;
  font-weight: 400;
  font-family: 'JetBrains Mono', monospace;
}

/* Micro text */
.text-xs-body {
  font-size: 0.75rem;    /* 12px */
  line-height: 1.4;
  font-weight: 400;
  font-family: 'JetBrains Mono', monospace;
}
```

### Specialized Text
```css
/* Code and technical content */
.text-code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.875rem;
  line-height: 1.4;
  font-weight: 400;
  letter-spacing: 0.01em;
}

/* Captions and metadata */
.text-caption {
  font-size: 0.75rem;
  line-height: 1.3;
  font-weight: 400;
  color: hsl(var(--foreground-muted));
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Labels and form elements */
.text-label {
  font-size: 0.875rem;
  line-height: 1.4;
  font-weight: 500;
  letter-spacing: 0.01em;
}
```

## Theme-Specific Typography

### Cyberpunk Theme Typography
```css
/* Brand text with neon glow */
.cyberpunk-brand {
  font-family: 'Orbitron', monospace;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: hsl(var(--neon-cyan));
  text-shadow: 
    0 0 10px hsl(var(--neon-cyan)),
    0 0 20px hsl(var(--neon-cyan)),
    0 0 30px hsl(var(--neon-cyan));
}

/* Secondary brand text */
.cyberpunk-secondary {
  font-family: 'Orbitron', monospace;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: hsl(var(--neon-orange));
  text-shadow: 
    0 0 10px hsl(var(--neon-orange)),
    0 0 20px hsl(var(--neon-orange));
}

/* Technical text with subtle glow */
.cyberpunk-tech {
  font-family: 'JetBrains Mono', monospace;
  color: hsl(var(--foreground));
  text-shadow: 0 0 5px hsl(var(--foreground) / 0.3);
}
```

### Corporate Theme Typography
```css
/* Professional brand text */
.corporate-brand {
  font-family: 'Orbitron', sans-serif;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: hsl(var(--corporate-blue));
}

/* Clean body text */
.corporate-body {
  font-family: 'Inter', 'JetBrains Mono', sans-serif;
  font-weight: 400;
  color: hsl(var(--foreground));
}
```

### Classic Theme Typography
```css
/* Balanced brand text */
.classic-brand {
  font-family: 'Orbitron', serif;
  font-weight: 500;
  letter-spacing: 0.025em;
  color: hsl(var(--foreground));
}

/* Readable body text */
.classic-body {
  font-family: 'Georgia', 'JetBrains Mono', serif;
  font-weight: 400;
  color: hsl(var(--foreground));
}
```

## Responsive Typography

### Fluid Scaling
```css
/* Responsive brand text */
.brand-responsive {
  font-size: clamp(2rem, 8vw, 6rem);
  line-height: clamp(1.1, 1.1, 1.1);
}

/* Responsive body text */
.body-responsive {
  font-size: clamp(0.875rem, 2.5vw, 1.125rem);
  line-height: clamp(1.4, 1.6, 1.8);
}
```

### Breakpoint-Specific Adjustments
```css
/* Mobile typography adjustments */
@media (max-width: 768px) {
  .mobile-brand {
    font-size: 2.5rem;
    letter-spacing: 0.05em;
  }
  
  .mobile-body {
    font-size: 1rem;
    line-height: 1.6;
  }
}

/* Desktop enhancements */
@media (min-width: 1024px) {
  .desktop-brand {
    font-size: 4rem;
    letter-spacing: 0.1em;
  }
}
```

## Typography Utilities

### Text Effects
```css
/* Neon glow animation */
@keyframes neon-pulse {
  0%, 100% {
    text-shadow: 
      0 0 5px currentColor,
      0 0 10px currentColor,
      0 0 20px currentColor;
  }
  50% {
    text-shadow: 
      0 0 10px currentColor,
      0 0 20px currentColor,
      0 0 30px currentColor,
      0 0 40px currentColor;
  }
}

.neon-pulse {
  animation: neon-pulse 2s ease-in-out infinite;
}

/* Glitch effect */
@keyframes glitch {
  0% { transform: translate(0); }
  20% { transform: translate(-2px, 2px); }
  40% { transform: translate(-2px, -2px); }
  60% { transform: translate(2px, 2px); }
  80% { transform: translate(2px, -2px); }
  100% { transform: translate(0); }
}

.glitch-text {
  animation: glitch 0.5s infinite;
}
```

### Text Spacing
```css
/* Letter spacing variants */
.tracking-tighter { letter-spacing: -0.05em; }
.tracking-tight { letter-spacing: -0.025em; }
.tracking-normal { letter-spacing: 0em; }
.tracking-wide { letter-spacing: 0.025em; }
.tracking-wider { letter-spacing: 0.05em; }
.tracking-widest { letter-spacing: 0.1em; }

/* Line height variants */
.leading-none { line-height: 1; }
.leading-tight { line-height: 1.25; }
.leading-snug { line-height: 1.375; }
.leading-normal { line-height: 1.5; }
.leading-relaxed { line-height: 1.625; }
.leading-loose { line-height: 2; }
```

## Accessibility Considerations

### Font Loading
```css
/* Font display optimization */
@font-face {
  font-family: 'Orbitron';
  font-display: swap; /* Improve loading performance */
  src: url('path/to/orbitron.woff2') format('woff2');
}
```

### Reduced Motion Support
```css
@media (prefers-reduced-motion: reduce) {
  .neon-pulse,
  .glitch-text {
    animation: none;
  }
  
  .cyberpunk-brand,
  .cyberpunk-secondary {
    text-shadow: none;
  }
}
```

### Font Size Scaling
```css
/* Support user font size preferences */
html {
  font-size: calc(1rem * var(--font-size-factor, 1));
}

/* Respect system font size settings */
@media (prefers-reduced-data: reduce) {
  html {
    font-family: system-ui, sans-serif;
  }
}
```

## Implementation Examples

### Brand Header Component
```tsx
interface BrandHeaderProps {
  theme: 'cyberpunk' | 'corporate' | 'classic';
  size: 'sm' | 'md' | 'lg';
}

const BrandHeader: React.FC<BrandHeaderProps> = ({ theme, size }) => {
  const sizeClasses = {
    sm: 'text-2xl',
    md: 'text-4xl', 
    lg: 'text-6xl'
  };
  
  const themeClasses = {
    cyberpunk: 'cyberpunk-brand neon-glow-cyan',
    corporate: 'corporate-brand',
    classic: 'classic-brand'
  };
  
  return (
    <h1 className={`${sizeClasses[size]} ${themeClasses[theme]}`}>
      ULTRA AI
    </h1>
  );
};
```

### Body Text Component
```tsx
interface BodyTextProps {
  variant: 'large' | 'default' | 'small';
  theme: 'cyberpunk' | 'corporate' | 'classic';
  children: React.ReactNode;
}

const BodyText: React.FC<BodyTextProps> = ({ variant, theme, children }) => {
  const variantClasses = {
    large: 'text-lg-body',
    default: 'text-base-body',
    small: 'text-sm-body'
  };
  
  const themeClasses = {
    cyberpunk: 'cyberpunk-tech',
    corporate: 'corporate-body',
    classic: 'classic-body'
  };
  
  return (
    <p className={`${variantClasses[variant]} ${themeClasses[theme]}`}>
      {children}
    </p>
  );
};
```

---

**Next**: Review [Component Library](./components/) for complete UI specifications.