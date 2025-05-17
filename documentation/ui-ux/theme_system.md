# UltrAI Theme System Documentation

The UltrAI Theme System provides a flexible and customizable theming solution for the application, allowing users to personalize their experience and supporting enterprise branding requirements.

## Features

- **Multiple Theme Styles**: Choose between Cyberpunk, Corporate, and Classic styles
- **Light/Dark Mode**: Toggle between day (light) and night (dark) modes
- **Accent Colors**: Select from various accent colors to personalize the UI
- **Accessibility Options**: Adjust contrast levels, font size, and motion preferences
- **Enterprise Branding**: Support for custom branding in enterprise deployments
- **Persistent Preferences**: User preferences are saved to localStorage

## Theme Components

### ThemeProvider

The `ThemeProvider` component manages the theme state and provides context to child components. It handles:

- Loading saved preferences from localStorage
- Detecting system color scheme preferences
- Toggling between light and dark modes
- Changing theme styles and accent colors
- Adjusting accessibility settings

```tsx
import { ThemeProvider } from '../theme';

function App() {
  return <ThemeProvider>{/* App content */}</ThemeProvider>;
}
```

### ThemeRegistry

The `ThemeRegistry` component applies the theme CSS variables to the document and handles special effects for different themes.

```tsx
import { ThemeProvider, ThemeRegistry } from '../theme';

function App() {
  return (
    <ThemeProvider>
      <ThemeRegistry>{/* App content */}</ThemeRegistry>
    </ThemeProvider>
  );
}
```

### DayNightToggle

The `DayNightToggle` component provides a visually appealing toggle button for switching between day (light) and night (dark) modes.

```tsx
import { DayNightToggle } from '../theme';

function Header() {
  return (
    <header>
      {/* Other header content */}
      <DayNightToggle size="sm" />
    </header>
  );
}
```

Available sizes: "sm", "md", "lg"

### ThemePanel

The `ThemePanel` component provides a UI for customizing theme settings, including theme style, accent color, font size, and contrast.

```tsx
import { ThemePanel } from '../theme';

function SettingsPage() {
  return (
    <div>
      <h1>Settings</h1>
      <ThemePanel
        onClose={() => {
          /* handle close */
        }}
      />
    </div>
  );
}
```

## Using the Theme Hook

The `useTheme` hook provides access to the current theme state and theme-related functions.

```tsx
import { useTheme } from '../theme';

function MyComponent() {
  const {
    theme, // Current theme preferences
    toggleMode, // Toggle between light/dark
    setThemeStyle, // Change theme style
    setAccentColor, // Change accent color
    setFontSize, // Adjust font size
    setContrastLevel, // Adjust contrast
    toggleAnimations, // Toggle animations
    toggleReducedMotion, // Toggle reduced motion
  } = useTheme();

  return (
    <div>
      <p>
        Current theme: {theme.style} ({theme.mode})
      </p>
      <button onClick={toggleMode}>
        Switch to {theme.mode === 'dark' ? 'light' : 'dark'} mode
      </button>
    </div>
  );
}
```

## CSS Variables

The theme system uses CSS variables for dynamic theme application. These variables are available globally and can be used in your components.

```css
/* Example: Using theme variables in CSS */
.my-component {
  background-color: hsl(var(--background));
  color: hsl(var(--foreground));
  border: 1px solid hsl(var(--border));
}

/* Example: Using accent color */
.my-button {
  background-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
}
```

## Cyberpunk Theme

The Cyberpunk theme includes special effects like neon text and glass morphism:

```tsx
// Neon text effect
<span className="neon-text">UltrAI</span>

// Glass panel effect
<div className="glass-panel">
  Content
</div>
```

## Enterprise Branding

For enterprise deployments, the theme system supports custom branding:

```tsx
import { ThemeProvider } from '../theme';

function App() {
  return (
    <ThemeProvider
      branding={{
        companyName: 'ACME Corp',
        primaryColor: 'hsl(240, 100%, 50%)',
        logo: '/path/to/logo.svg',
        favicon: '/path/to/favicon.ico',
      }}
    >
      {/* App content */}
    </ThemeProvider>
  );
}
```

## Integration with Tailwind CSS

The theme system is designed to work seamlessly with Tailwind CSS. Theme variables are mapped to Tailwind utility classes.

```tsx
// Example: Using theme-aware utility classes
<div className="bg-background text-foreground">
  <button className="bg-primary text-primary-foreground">Click Me</button>
</div>
```

## Accessibility Considerations

The theme system includes several accessibility features:

- High contrast mode
- Font size adjustments
- Reduced motion option
- Proper color contrast ratios
- Keyboard navigation support

## Best Practices

1. Use the theme utility classes instead of hardcoded colors
2. Test components in both light and dark modes
3. Ensure sufficient contrast for text and interactive elements
4. Use theme variables for consistent styling
5. Consider users with accessibility needs

## Implementation Details

The theme system is implemented using:

- React Context API for state management
- CSS variables for dynamic theme application
- localStorage for persistent preferences
- Media queries for system preference detection
- Tailwind CSS for utility classes
