# Color System

## Overview

The UltraAI color system supports three distinct themes while maintaining functional consistency. Each theme uses CSS variables for dynamic switching and includes semantic color tokens for consistent component behavior.

## Core Color Philosophy

### Cyberpunk Theme
High-contrast neon colors against dark backgrounds create the signature "digital billboard" aesthetic seen in the mockups.

### Corporate Theme  
Professional blues and grays provide enterprise-friendly alternatives while maintaining brand recognition.

### Classic Theme
Balanced, accessible colors ensure broad compatibility and WCAG compliance.

## Color Tokens

### CSS Variable Structure
```css
:root {
  /* Semantic tokens */
  --background: /* Primary background */
  --foreground: /* Primary text */
  --primary: /* Primary actions/brand */
  --secondary: /* Secondary actions */
  --accent: /* Accent/highlight color */
  --muted: /* Subdued content */
  --border: /* Borders and dividers */
  
  /* Neon effects (Cyberpunk only) */
  --neon-cyan: #00FFFF;
  --neon-orange: #FF6B35;
  --neon-pink: #FF00DE;
  --neon-glow: 0 0 20px currentColor;
}
```

## Theme-Specific Palettes

### Cyberpunk Theme (Default)

#### Primary Colors
```css
:root.cyberpunk {
  /* Core brand colors */
  --neon-cyan: 180 100% 50%;      /* #00FFFF - Primary brand */
  --neon-orange: 17 100% 60%;     /* #FF6B35 - Secondary brand */
  --neon-pink: 306 100% 50%;      /* #FF00DE - Accent highlights */
  
  /* Background system */
  --background: 222 84% 5%;        /* #0A0F1C - Deep space blue */
  --background-secondary: 220 45% 8%; /* #121A2B - Elevated surfaces */
  --background-tertiary: 218 35% 12%; /* #1A2332 - Cards/panels */
  
  /* Text system */
  --foreground: 180 100% 90%;      /* #E6FFFF - Primary text */
  --foreground-secondary: 180 50% 70%; /* #80CCCC - Secondary text */
  --foreground-muted: 180 30% 50%;    /* #668080 - Muted text */
  
  /* Interactive system */
  --primary: var(--neon-cyan);
  --primary-foreground: 222 84% 5%;
  --secondary: 218 35% 15%;
  --secondary-foreground: var(--foreground);
  --accent: var(--neon-orange);
  --accent-foreground: 222 84% 5%;
  
  /* Feedback colors */
  --success: 120 100% 40%;         /* #00CC00 - Neon green */
  --warning: var(--neon-orange);
  --error: 0 100% 50%;             /* #FF0000 - Neon red */
  --info: var(--neon-cyan);
  
  /* Surface system */
  --card: var(--background-tertiary);
  --card-foreground: var(--foreground);
  --border: 180 50% 25%;           /* #336666 - Subtle cyan tint */
  --input: var(--background-secondary);
  --ring: var(--neon-cyan);
}
```

#### Neon Glow Effects
```css
/* Text glow utilities */
.neon-glow-cyan {
  color: hsl(var(--neon-cyan));
  text-shadow: 
    0 0 5px hsl(var(--neon-cyan)),
    0 0 10px hsl(var(--neon-cyan)),
    0 0 20px hsl(var(--neon-cyan)),
    0 0 30px hsl(var(--neon-cyan));
}

.neon-glow-orange {
  color: hsl(var(--neon-orange));
  text-shadow: 
    0 0 5px hsl(var(--neon-orange)),
    0 0 10px hsl(var(--neon-orange)),
    0 0 20px hsl(var(--neon-orange));
}

.neon-glow-pink {
  color: hsl(var(--neon-pink));
  text-shadow: 
    0 0 5px hsl(var(--neon-pink)),
    0 0 10px hsl(var(--neon-pink)),
    0 0 20px hsl(var(--neon-pink));
}
```

### Corporate Theme

#### Professional Palette
```css
:root.corporate {
  /* Brand colors */
  --corporate-blue: 217 91% 60%;   /* #3B82F6 - Primary blue */
  --corporate-navy: 217 33% 17%;   /* #1E293B - Dark blue */
  --corporate-slate: 215 28% 47%;  /* #64748B - Medium gray */
  
  /* Background system */
  --background: 0 0% 98%;          /* #FAFAFA - Off white */
  --background-secondary: 0 0% 96%; /* #F5F5F5 - Light gray */
  --background-tertiary: 0 0% 100%; /* #FFFFFF - Pure white */
  
  /* Text system */
  --foreground: var(--corporate-navy);
  --foreground-secondary: var(--corporate-slate);
  --foreground-muted: 215 16% 65%;
  
  /* Interactive system */
  --primary: var(--corporate-blue);
  --primary-foreground: 0 0% 100%;
  --secondary: 215 28% 88%;
  --secondary-foreground: var(--corporate-navy);
  --accent: 217 91% 60%;
  --accent-foreground: 0 0% 100%;
  
  /* Feedback colors */
  --success: 142 76% 36%;          /* #16A34A - Green */
  --warning: 38 92% 50%;           /* #EAB308 - Amber */
  --error: 0 84% 60%;              /* #DC2626 - Red */
  --info: var(--corporate-blue);
  
  /* Surface system */
  --card: var(--background-tertiary);
  --card-foreground: var(--foreground);
  --border: 214 32% 91%;
  --input: var(--background-tertiary);
  --ring: var(--corporate-blue);
}
```

### Classic Theme

#### Balanced Palette
```css
:root.classic {
  /* Neutral colors */
  --classic-dark: 210 11% 15%;     /* #222831 - Dark gray */
  --classic-medium: 209 13% 65%;   /* #9CA3AF - Medium gray */
  --classic-light: 210 40% 98%;    /* #F9FAFB - Light background */
  
  /* Background system */
  --background: var(--classic-light);
  --background-secondary: 210 40% 96%;
  --background-tertiary: 0 0% 100%;
  
  /* Text system */
  --foreground: var(--classic-dark);
  --foreground-secondary: var(--classic-medium);
  --foreground-muted: 210 6% 56%;
  
  /* Interactive system */
  --primary: 217 91% 60%;          /* Subtle blue */
  --primary-foreground: 0 0% 100%;
  --secondary: 210 40% 94%;
  --secondary-foreground: var(--classic-dark);
  --accent: 262 83% 58%;           /* Purple accent */
  --accent-foreground: 0 0% 100%;
  
  /* Feedback colors */
  --success: 142 76% 36%;
  --warning: 38 92% 50%;
  --error: 0 84% 60%;
  --info: 217 91% 60%;
  
  /* Surface system */
  --card: var(--background-tertiary);
  --card-foreground: var(--foreground);
  --border: 214 32% 91%;
  --input: var(--background-tertiary);
  --ring: var(--primary);
}
```

## Data Visualization Colors

### Chart Color Sequences
```css
:root {
  /* Primary sequence - high contrast */
  --chart-1: 180 100% 50%;  /* Cyan */
  --chart-2: 17 100% 60%;   /* Orange */
  --chart-3: 306 100% 50%;  /* Pink */
  --chart-4: 120 100% 40%;  /* Green */
  --chart-5: 270 100% 60%;  /* Purple */
  
  /* Secondary sequence - muted variants */
  --chart-1-muted: 180 60% 40%;
  --chart-2-muted: 17 60% 50%;
  --chart-3-muted: 306 60% 40%;
  --chart-4-muted: 120 60% 35%;
  --chart-5-muted: 270 60% 50%;
}
```

### Usage in Charts
```tsx
const chartColors = {
  cyberpunk: [
    'hsl(var(--chart-1))',
    'hsl(var(--chart-2))',
    'hsl(var(--chart-3))',
    'hsl(var(--chart-4))',
    'hsl(var(--chart-5))'
  ],
  corporate: [
    'hsl(217 91% 60%)',  /* Blue variations */
    'hsl(217 91% 70%)',
    'hsl(217 91% 50%)',
    'hsl(217 91% 40%)',
    'hsl(217 91% 80%)'
  ]
};
```

## Semantic Color Usage

### Status Colors
```css
/* Success states */
.text-success { color: hsl(var(--success)); }
.bg-success { background-color: hsl(var(--success)); }

/* Warning states */
.text-warning { color: hsl(var(--warning)); }
.bg-warning { background-color: hsl(var(--warning)); }

/* Error states */
.text-error { color: hsl(var(--error)); }
.bg-error { background-color: hsl(var(--error)); }

/* Info states */
.text-info { color: hsl(var(--info)); }
.bg-info { background-color: hsl(var(--info)); }
```

### Interactive States
```css
/* Button primary */
.btn-primary {
  background-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
}

.btn-primary:hover {
  background-color: hsl(var(--primary) / 0.9);
}

/* Button secondary */
.btn-secondary {
  background-color: hsl(var(--secondary));
  color: hsl(var(--secondary-foreground));
}

/* Accent highlights */
.accent {
  color: hsl(var(--accent));
}
```

## Accessibility Considerations

### Contrast Ratios
- **AA Standard**: Minimum 4.5:1 for normal text
- **AAA Standard**: 7:1 for optimal accessibility
- **Large Text**: 3:1 minimum (18pt+ or 14pt+ bold)

### Color Testing
```css
/* High contrast mode support */
@media (prefers-contrast: high) {
  :root {
    --background: 0 0% 0%;
    --foreground: 0 0% 100%;
    --border: 0 0% 50%;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .neon-glow-cyan,
  .neon-glow-orange,
  .neon-glow-pink {
    text-shadow: none;
    animation: none;
  }
}
```

### Color-Blind Considerations
- Neon cyan/orange combination provides strong contrast
- Corporate theme uses tested blue/gray combinations
- Never rely solely on color to convey information
- Include icons and text labels for status indicators

## Implementation Guidelines

### Using Color Tokens
```tsx
// ✅ Correct - Use semantic tokens
<button className="bg-primary text-primary-foreground">

// ❌ Incorrect - Don't hardcode colors
<button style={{backgroundColor: '#00FFFF'}}>

// ✅ Correct - Dynamic theme support
<div className="text-foreground bg-background">

// ✅ Correct - Neon effects in cyberpunk theme
<h1 className="neon-glow-cyan">ULTRA AI</h1>
```

### Theme Switching
Colors automatically update when theme classes change on the document root:
```tsx
// Theme switching updates all color tokens
document.documentElement.className = 'cyberpunk dark';
document.documentElement.className = 'corporate light';
document.documentElement.className = 'classic light';
```

---

**Next**: Review [Typography](./typography.md) for text styling guidelines.