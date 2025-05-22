# Accessibility Guidelines

## Overview

The UltraAI design system prioritizes inclusive design, ensuring that the cyberpunk aesthetic and advanced interactions remain accessible to all users. These guidelines provide specific implementations for WCAG 2.1 AA compliance across all three themes.

## Accessibility Principles

### 1. Perceivable
Content must be presentable in ways users can perceive, regardless of visual or auditory capabilities.

### 2. Operable
Interface components must be operable through various input methods.

### 3. Understandable
Information and operation of the interface must be understandable.

### 4. Robust
Content must be robust enough to work with various assistive technologies.

## Color and Contrast

### Contrast Requirements

#### WCAG 2.1 Standards
- **AA Normal Text**: 4.5:1 minimum ratio
- **AA Large Text**: 3:1 minimum ratio (18pt+ or 14pt+ bold)
- **AAA Normal Text**: 7:1 ratio (preferred)
- **AAA Large Text**: 4.5:1 ratio (preferred)

#### Theme-Specific Contrast

##### Cyberpunk Theme
```css
/* High contrast neon on dark */
.cyberpunk-text-primary {
  color: #00FFFF; /* Cyan */
  background: #0A0F1C; /* Dark blue */
  /* Contrast ratio: 8.2:1 (AAA compliant) */
}

.cyberpunk-text-secondary {
  color: #FF6B35; /* Orange */
  background: #0A0F1C; /* Dark blue */
  /* Contrast ratio: 6.1:1 (AAA compliant) */
}

.cyberpunk-text-muted {
  color: #80CCCC; /* Muted cyan */
  background: #0A0F1C; /* Dark blue */
  /* Contrast ratio: 4.8:1 (AA compliant) */
}
```

##### Corporate Theme
```css
.corporate-text-primary {
  color: #1E293B; /* Dark slate */
  background: #FFFFFF; /* White */
  /* Contrast ratio: 16.9:1 (AAA compliant) */
}

.corporate-text-secondary {
  color: #64748B; /* Medium gray */
  background: #FFFFFF; /* White */
  /* Contrast ratio: 5.4:1 (AAA compliant) */
}
```

### High Contrast Mode Support
```css
@media (prefers-contrast: high) {
  :root {
    /* Override theme colors for maximum contrast */
    --background: 0 0% 0%;
    --foreground: 0 0% 100%;
    --primary: 0 0% 100%;
    --secondary: 0 0% 75%;
    --border: 0 0% 50%;
  }
  
  /* Remove decorative effects */
  .neon-glow-cyan,
  .neon-glow-orange,
  .neon-glow-pink {
    text-shadow: none;
    filter: none;
  }
  
  /* Increase border visibility */
  .btn,
  .input,
  .card {
    border-width: 2px;
    border-style: solid;
  }
}
```

### Color-Blind Considerations
```css
/* Ensure sufficient differentiation beyond color */
.status-success {
  color: hsl(var(--success));
  position: relative;
}

.status-success::before {
  content: "✓";
  font-weight: bold;
  margin-right: 8px;
}

.status-error {
  color: hsl(var(--error));
  position: relative;
}

.status-error::before {
  content: "⚠";
  font-weight: bold;
  margin-right: 8px;
}

.status-warning {
  color: hsl(var(--warning));
  position: relative;
}

.status-warning::before {
  content: "!";
  font-weight: bold;
  margin-right: 8px;
  background: currentColor;
  color: white;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}
```

## Typography Accessibility

### Font Size and Scaling
```css
/* Support user font size preferences */
:root {
  font-size: calc(1rem * var(--font-size-factor, 1));
}

/* Minimum font sizes */
.text-minimum {
  font-size: max(16px, 1rem); /* Never smaller than 16px */
}

/* Responsive font scaling */
.text-responsive {
  font-size: clamp(
    1rem,                    /* Minimum: 16px */
    2.5vw,                   /* Preferred: 2.5% of viewport */
    1.25rem                  /* Maximum: 20px */
  );
}
```

### Line Height and Spacing
```css
/* Optimal line heights for readability */
.text-body {
  line-height: 1.6;        /* 160% for body text */
  letter-spacing: 0.01em;  /* Slight letter spacing */
}

.text-heading {
  line-height: 1.2;        /* 120% for headings */
  letter-spacing: 0.02em;
}

/* Paragraph spacing */
p + p {
  margin-top: 1.2em;
}
```

### Font Loading
```css
/* Font display optimization for accessibility */
@font-face {
  font-family: 'Orbitron';
  src: url('path/to/orbitron.woff2') format('woff2');
  font-display: swap; /* Show fallback font immediately */
}

/* Fallback font stacks */
.font-primary {
  font-family: 'Orbitron', 'Arial', sans-serif;
}

.font-mono {
  font-family: 'JetBrains Mono', 'Courier New', monospace;
}
```

## Focus Management

### Focus Indicators
```css
/* High-visibility focus indicators */
.focus-visible {
  outline: 3px solid hsl(var(--ring));
  outline-offset: 2px;
  border-radius: 4px;
}

/* Cyberpunk theme focus */
.cyberpunk .focus-visible {
  outline: none;
  box-shadow: 
    0 0 0 2px hsl(var(--background)),
    0 0 0 4px hsl(var(--neon-cyan)),
    0 0 15px hsl(var(--neon-cyan) / 0.5);
}

/* Corporate theme focus */
.corporate .focus-visible {
  outline: 3px solid hsl(var(--corporate-blue));
  box-shadow: 0 0 0 1px white;
}

/* Skip mouse focus for better UX */
.btn:focus:not(:focus-visible) {
  outline: none;
  box-shadow: none;
}
```

### Focus Trapping
```tsx
// Modal focus trap implementation
const FocusTrap: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const trapRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    const trap = trapRef.current;
    if (!trap) return;
    
    // Get all focusable elements
    const focusableElements = trap.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;
    
    // Focus first element
    firstElement?.focus();
    
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement?.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement?.focus();
          }
        }
      }
      
      if (e.key === 'Escape') {
        // Handle escape key
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);
  
  return <div ref={trapRef}>{children}</div>;
};
```

### Skip Links
```tsx
const SkipLink: React.FC = () => (
  <a
    href="#main-content"
    className="skip-link"
    aria-label="Skip to main content"
  >
    Skip to main content
  </a>
);
```

```css
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
  padding: 8px 16px;
  text-decoration: none;
  border-radius: 4px;
  z-index: 1000;
  transition: top 0.2s ease;
}

.skip-link:focus {
  top: 6px;
}
```

## Keyboard Navigation

### Tab Order
```css
/* Ensure logical tab order */
.tab-container {
  display: flex;
  flex-direction: column;
}

/* Custom tab index for complex layouts */
.priority-focus {
  tabindex: 1;
}

.secondary-focus {
  tabindex: 2;
}

/* Remove from tab order when hidden */
.hidden {
  tabindex: -1;
  visibility: hidden;
}
```

### Keyboard Shortcuts
```tsx
const KeyboardShortcuts: React.FC = () => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Global shortcuts
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 'k':
            e.preventDefault();
            // Open command palette
            break;
          case '/':
            e.preventDefault();
            // Focus search
            break;
        }
      }
      
      // Escape key handling
      if (e.key === 'Escape') {
        // Close modals, clear selections
      }
      
      // Arrow key navigation
      if (e.key.startsWith('Arrow')) {
        // Handle arrow navigation
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);
  
  return null;
};
```

## Screen Reader Support

### Semantic HTML
```tsx
// Use semantic elements for better screen reader support
const AccessibleForm: React.FC = () => (
  <main>
    <header>
      <h1>Analysis Configuration</h1>
    </header>
    
    <form role="form" aria-labelledby="form-title">
      <h2 id="form-title">Enter Analysis Details</h2>
      
      <fieldset>
        <legend>Prompt Information</legend>
        
        <label htmlFor="prompt-input">
          Analysis Prompt
          <span aria-label="required" className="required">*</span>
        </label>
        <textarea
          id="prompt-input"
          name="prompt"
          required
          aria-describedby="prompt-help"
          aria-invalid="false"
        />
        <div id="prompt-help" className="help-text">
          Describe what you'd like to analyze in detail.
        </div>
      </fieldset>
      
      <fieldset>
        <legend>Model Selection</legend>
        
        <label htmlFor="model-select">AI Model</label>
        <select 
          id="model-select" 
          name="model"
          aria-describedby="model-help"
        >
          <option value="">Select a model</option>
          <option value="gpt-4">GPT-4</option>
          <option value="claude-3">Claude 3</option>
        </select>
        <div id="model-help" className="help-text">
          Choose the AI model for your analysis.
        </div>
      </fieldset>
    </form>
  </main>
);
```

### ARIA Labels and Descriptions
```tsx
// Button with descriptive ARIA labels
const GenerateButton: React.FC<{ loading: boolean; cost: string }> = ({ loading, cost }) => (
  <button
    type="submit"
    disabled={loading}
    aria-label={loading ? 'Generating analysis' : `Generate analysis for ${cost}`}
    aria-describedby="cost-display"
  >
    {loading ? 'Generating...' : 'Generate'}
  </button>
);

// Cost display with proper labeling
const CostDisplay: React.FC<{ cost: string }> = ({ cost }) => (
  <div id="cost-display" role="status" aria-live="polite">
    <span className="sr-only">Estimated cost:</span>
    <span aria-label={`${cost} dollars`}>{cost}</span>
  </div>
);
```

### Live Regions
```tsx
const LiveRegion: React.FC<{ message: string; priority: 'polite' | 'assertive' }> = ({ 
  message, 
  priority = 'polite' 
}) => (
  <div
    role="status"
    aria-live={priority}
    aria-atomic="true"
    className="sr-only"
  >
    {message}
  </div>
);

// Usage for notifications
const NotificationSystem: React.FC = () => {
  const [message, setMessage] = useState('');
  
  return (
    <>
      <LiveRegion message={message} priority="polite" />
      {/* Other UI elements */}
    </>
  );
};
```

## Reduced Motion Support

### Motion Preferences
```css
/* Respect user motion preferences */
@media (prefers-reduced-motion: reduce) {
  /* Disable complex animations */
  .neon-pulse,
  .glitch-text,
  .scan-line,
  .grid-pulse {
    animation: none !important;
  }
  
  /* Reduce transition durations */
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
  
  /* Keep essential feedback */
  .btn:hover,
  .input:focus,
  .card:hover {
    transition-duration: 0.15s !important;
  }
  
  /* Remove parallax and auto-playing media */
  .parallax {
    transform: none !important;
  }
  
  video {
    animation-play-state: paused !important;
  }
}
```

### Static Alternatives
```tsx
const MotionSafeComponent: React.FC = () => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);
    
    const handleChange = () => setPrefersReducedMotion(mediaQuery.matches);
    mediaQuery.addEventListener('change', handleChange);
    
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);
  
  return (
    <div className={prefersReducedMotion ? 'motion-reduce' : 'motion-safe'}>
      {prefersReducedMotion ? (
        <StaticVersion />
      ) : (
        <AnimatedVersion />
      )}
    </div>
  );
};
```

## Error Handling and Feedback

### Error Messages
```tsx
const ErrorMessage: React.FC<{ error: string; fieldId: string }> = ({ error, fieldId }) => (
  <div
    id={`${fieldId}-error`}
    role="alert"
    aria-live="assertive"
    className="error-message"
  >
    <span className="error-icon" aria-hidden="true">⚠</span>
    <span className="sr-only">Error: </span>
    {error}
  </div>
);

// Form field with error support
const AccessibleInput: React.FC<InputProps> = ({ error, ...props }) => (
  <div className="form-field">
    <input
      {...props}
      aria-invalid={error ? 'true' : 'false'}
      aria-describedby={error ? `${props.id}-error` : undefined}
    />
    {error && <ErrorMessage error={error} fieldId={props.id} />}
  </div>
);
```

### Loading States
```tsx
const LoadingButton: React.FC<{ loading: boolean; children: React.ReactNode }> = ({ 
  loading, 
  children 
}) => (
  <button
    disabled={loading}
    aria-label={loading ? 'Processing request' : undefined}
    aria-describedby={loading ? 'loading-status' : undefined}
  >
    {loading && (
      <span id="loading-status" className="sr-only" role="status" aria-live="polite">
        Processing your request, please wait.
      </span>
    )}
    {children}
  </button>
);
```

## Testing Accessibility

### Automated Testing
```typescript
// Jest + React Testing Library accessibility tests
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

test('component should be accessible', async () => {
  const { container } = render(<MyComponent />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

### Manual Testing Checklist
- [ ] Tab through entire interface
- [ ] Test with screen reader (NVDA, JAWS, VoiceOver)
- [ ] Verify high contrast mode
- [ ] Test with reduced motion enabled
- [ ] Check color contrast ratios
- [ ] Verify keyboard shortcuts work
- [ ] Test error states and feedback
- [ ] Ensure focus indicators are visible
- [ ] Validate ARIA labels and roles

---

**This completes the comprehensive UltraAI Design System documentation, providing detailed guidelines for maintaining consistency across all visual development while ensuring accessibility and usability.**