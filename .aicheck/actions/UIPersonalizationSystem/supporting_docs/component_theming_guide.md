# Component Theming Guide

This document provides guidelines for implementing theme-aware components in the UltraLLMOrchestrator UI Personalization System.

## Overview

Component theming enables consistent application of themes across the interface while maintaining component functionality and behavior. This guide outlines the approach for converting existing components to be theme-aware and creating new themed components.

## Component Theming Principles

### 1. Separation of Concerns

Components should separate:
- **Structure**: HTML/JSX markup
- **Behavior**: JavaScript/TypeScript functionality
- **Appearance**: Theme-dependent styling

### 2. Theme Consumption

Components should consume theme properties through:
- CSS variables for styling
- Theme context for dynamic properties
- Attribute-based variants for structural changes

### 3. Styling Approach

Component styling should use:
- Tailwind utility classes that reference theme variables
- CSS modules with theme variable consumption
- Inline styles only when dynamically computed

### 4. Backwards Compatibility

Component updates should maintain:
- Existing props and API
- Default styling that matches current appearance
- Graceful fallbacks for missing theme properties

## Converting Existing Components

### 1. Component Analysis

Before converting a component:

1. **Identify Style Properties**:
   - Colors (background, text, borders)
   - Typography (font family, size, weight)
   - Spacing (margin, padding)
   - Borders (width, radius, style)
   - Shadows and effects

2. **Identify Variants**:
   - Visual variants (primary, secondary, etc.)
   - Size variants (small, medium, large)
   - State variants (disabled, active, focused)
   - Content variants (with icon, text only, etc.)

3. **Identify Interactions**:
   - Hover effects
   - Focus states
   - Active/pressed states
   - Animation and transitions

### 2. Theme Mapping

Map component properties to theme tokens:

1. **Color Mapping**:
   - Component background → theme background tokens
   - Component text → theme text tokens
   - Component borders → theme border tokens
   - Component accents → theme accent tokens

2. **Typography Mapping**:
   - Component font family → theme typography tokens
   - Component font size → theme size tokens
   - Component font weight → theme weight tokens

3. **Layout Mapping**:
   - Component spacing → theme spacing tokens
   - Component borders → theme border tokens
   - Component shadows → theme shadow tokens

### 3. Conversion Process

#### Step 1: Add Theme Context Consumption

```jsx
// Before
function Button({ variant, size, children, ...props }) {
  // Component implementation
}

// After
function Button({ variant, size, children, ...props }) {
  const { activeTheme } = useTheme();
  // Component implementation with theme awareness
}
```

#### Step 2: Replace Hardcoded Styles with Theme References

```jsx
// Before
<button className="bg-blue-600 text-white hover:bg-blue-700">
  {children}
</button>

// After
<button className="bg-primary text-primary-foreground hover:bg-primary/90">
  {children}
</button>
```

#### Step 3: Add Variant Handling with Theme Awareness

```jsx
// Before
const variantStyles = {
  primary: "bg-blue-600 text-white",
  secondary: "bg-gray-200 text-gray-800",
};

// After
const variantStyles = {
  primary: "bg-primary text-primary-foreground",
  secondary: "bg-secondary text-secondary-foreground",
};
```

#### Step 4: Add Component-Specific Theme Overrides

```jsx
// Component-specific overrides
const componentStyles = activeTheme.components?.button?.[variant] || variantStyles[variant];
```

## Creating New Themed Components

### 1. Component Planning

When creating new themed components:

1. **Define Theme Requirements**:
   - Required theme tokens
   - Optional theme tokens with defaults
   - Component-specific theme properties

2. **Define Component API**:
   - Props for variants and configuration
   - Theme override props
   - Default behaviors

3. **Plan Theme Integration**:
   - How theme changes affect the component
   - Transition effects for theme changes
   - Fallbacks for missing theme properties

### 2. Implementation Process

#### Step 1: Create Component Structure

```jsx
export interface ThemedComponentProps {
  variant?: 'default' | 'alternate';
  size?: 'sm' | 'md' | 'lg';
  // Other props
}

export function ThemedComponent({
  variant = 'default',
  size = 'md',
  // Other props with defaults
}: ThemedComponentProps) {
  const { activeTheme } = useTheme();
  
  // Component implementation
}
```

#### Step 2: Implement Theme-Aware Styling

```jsx
// Using CSS variables via Tailwind
const containerClasses = classNames(
  "rounded-md transition-colors",
  {
    'bg-primary text-primary-foreground': variant === 'default',
    'bg-secondary text-secondary-foreground': variant === 'alternate',
  },
  {
    'text-sm p-2': size === 'sm',
    'text-base p-4': size === 'md',
    'text-lg p-6': size === 'lg',
  }
);

return (
  <div className={containerClasses}>
    {/* Component content */}
  </div>
);
```

#### Step 3: Add Component-Specific Theme Overrides

```jsx
// Get component-specific overrides if they exist
const componentOverrides = activeTheme.components?.themedComponent;

// Apply overrides if available
const customStyles = componentOverrides?.[variant] ? {
  backgroundColor: componentOverrides[variant].backgroundColor,
  color: componentOverrides[variant].textColor,
  // Other override properties
} : {};

return (
  <div className={containerClasses} style={customStyles}>
    {/* Component content */}
  </div>
);
```

## Theme-Aware Component Patterns

### 1. Compound Components

Compound components maintain theme consistency across child components:

```jsx
// Compound component pattern
function ThemedCard({ children, ...props }) {
  const { activeTheme } = useTheme();
  
  return (
    <div className="bg-card text-card-foreground rounded-lg shadow">
      {children}
    </div>
  );
}

ThemedCard.Header = function ThemedCardHeader({ children }) {
  return <div className="p-4 border-b border-border">{children}</div>;
};

ThemedCard.Body = function ThemedCardBody({ children }) {
  return <div className="p-4">{children}</div>;
};

ThemedCard.Footer = function ThemedCardFooter({ children }) {
  return <div className="p-4 border-t border-border">{children}</div>;
};
```

### 2. Render Props

Render props provide theme values to child components:

```jsx
// Render props pattern
function WithTheme({ children, selector }) {
  const { activeTheme } = useTheme();
  const themeValue = selector ? selector(activeTheme) : activeTheme;
  
  return children(themeValue);
}

// Usage
<WithTheme selector={theme => theme.colors.primary}>
  {(primaryColor) => (
    <div style={{ backgroundColor: primaryColor }}>
      Themed content
    </div>
  )}
</WithTheme>
```

### 3. Higher-Order Components

HOCs wrap components with theme awareness:

```jsx
// HOC pattern
function withTheme(Component) {
  return function ThemedComponent(props) {
    const theme = useTheme();
    return <Component {...props} theme={theme} />;
  };
}

// Usage
const ThemedButton = withTheme(Button);
```

### 4. Custom Hooks

Custom hooks provide theme values to components:

```jsx
// Custom hook pattern
function useComponentTheme(componentName, variant) {
  const { activeTheme } = useTheme();
  const componentTheme = activeTheme.components?.[componentName]?.[variant];
  
  return {
    componentTheme,
    activeTheme
  };
}

// Usage
function CustomButton({ variant }) {
  const { componentTheme } = useComponentTheme('button', variant);
  // Use componentTheme for styling
}
```

## Theme-Aware Layout Components

Layout components require special considerations:

### 1. Themed Containers

```jsx
function ThemedContainer({ children }) {
  return (
    <div className="bg-background text-foreground min-h-screen">
      {children}
    </div>
  );
}
```

### 2. Themed Navigation

```jsx
function ThemedNavigation() {
  const { activeTheme } = useTheme();
  
  return (
    <nav className="bg-primary text-primary-foreground p-4">
      {/* Navigation content */}
    </nav>
  );
}
```

### 3. Themed Layout Grid

```jsx
function ThemedGrid({ columns, children }) {
  return (
    <div className={`grid grid-cols-${columns} gap-4`}>
      {children}
    </div>
  );
}
```

## Component Theme Overrides

Components can support theme-specific overrides:

### 1. Override Structure

```typescript
interface ComponentOverrides {
  button?: {
    primary?: {
      backgroundColor?: string;
      textColor?: string;
      borderRadius?: string;
      // Other override properties
    };
    secondary?: {
      // Secondary variant overrides
    };
    // Other variant overrides
  };
  card?: {
    // Card component overrides
  };
  // Other component overrides
}
```

### 2. Applying Overrides

```jsx
function ThemedButton({ variant, ...props }) {
  const { activeTheme } = useTheme();
  
  // Get component overrides
  const overrides = activeTheme.components?.button?.[variant];
  
  // Create style object from overrides
  const overrideStyles = overrides ? {
    backgroundColor: overrides.backgroundColor,
    color: overrides.textColor,
    borderRadius: overrides.borderRadius,
  } : {};
  
  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]}`}
      style={overrideStyles}
      {...props}
    />
  );
}
```

## Testing Theme-Aware Components

### 1. Theme Variation Testing

Test components with different themes:

```jsx
// Test with different themes
it('renders correctly with dark theme', () => {
  render(
    <ThemeProvider theme="dark">
      <Button variant="primary">Test Button</Button>
    </ThemeProvider>
  );
  
  // Assert correct styling
});
```

### 2. Theme Transition Testing

Test theme transitions:

```jsx
// Test theme transitions
it('transitions smoothly between themes', async () => {
  const { getByRole, rerender } = render(
    <ThemeProvider theme="light">
      <Button variant="primary">Test Button</Button>
    </ThemeProvider>
  );
  
  // Check initial styling
  
  // Change theme
  rerender(
    <ThemeProvider theme="dark">
      <Button variant="primary">Test Button</Button>
    </ThemeProvider>
  );
  
  // Check transition and final styling
});
```

### 3. Theme Token Testing

Test correct token application:

```jsx
// Test theme token application
it('applies correct theme tokens', () => {
  const theme = {
    colors: {
      primary: '#0000ff',
    },
  };
  
  render(
    <ThemeProvider theme={theme}>
      <Button variant="primary">Test Button</Button>
    </ThemeProvider>
  );
  
  // Assert specific token values are applied
});
```

## Best Practices

### 1. Component Design

- Design components for theme adaptability from the start
- Use flexible layouts that adapt to theme changes
- Avoid hardcoded values for themeable properties
- Provide sensible defaults for missing theme properties

### 2. Performance Optimization

- Minimize style recalculations during theme changes
- Use memoization for computed theme values
- Batch DOM updates when applying theme changes
- Lazy load theme-specific assets

### 3. Accessibility

- Ensure sufficient contrast in all themes
- Test focus indicators across themes
- Maintain consistent interaction patterns between themes
- Support high-contrast and reduced-motion themes

### 4. Documentation

- Document theme dependencies for each component
- Provide usage examples with different themes
- Document component-specific theme overrides
- Include visual examples of themed components

## Component Conversion Checklist

Use this checklist when converting existing components:

- [ ] Component consumes theme context
- [ ] Hardcoded colors replaced with theme tokens
- [ ] Typography uses theme font tokens
- [ ] Spacing uses theme spacing tokens
- [ ] Borders and shadows use theme tokens
- [ ] Variants adapt to theme changes
- [ ] Component supports theme overrides
- [ ] Transitions added for smooth theme changes
- [ ] Default styling matches original appearance
- [ ] Tests updated for theme awareness
- [ ] Documentation updated with theming information

## Component Priority List

Convert components in the following order:

1. **Core UI Components**
   - Button
   - Card
   - Input
   - Checkbox
   - Select

2. **Layout Components**
   - Container
   - Navigation
   - Sidebar
   - Footer

3. **Complex Components**
   - DataTable
   - Tabs
   - Modal
   - Menu

4. **Specialized Components**
   - Charts
   - Visualizations
   - Result displays
   - Model comparisons