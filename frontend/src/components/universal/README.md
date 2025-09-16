# Universal UI Container System

The Universal UI Container System is a flexible, theme-agnostic component library designed to create consistent functional UI elements that can be rapidly skinned with different visual styles.

## Key Features

- **Universal Container Base** - Functional foundations with theme-agnostic structure
- **Style Configuration Schema** - Declarative styling for visual customization
- **Theme Engine** - Dynamic theming with preset visual styles
- **Specialized Components** - Pre-built UI panels for common use cases
- **Custom Decorative Elements** - Optional visual embellishments for unique styling

## Components

### UniversalContainer

The base container component that can adapt to any visual style while maintaining consistent functionality.

```tsx
import UniversalContainer from './components/universal/UniversalContainer';

<UniversalContainer
  variant="primary"
  size="md"
  styleConfig={{
    baseStyle: 'bg-gray-900/80 backdrop-blur-md',
    accentColor: 'cyan',
    borderStyle: 'neon',
    decorativeElements: { drones: true },
  }}
  isFloating={true}
>
  {/* Your content */}
</UniversalContainer>;
```

### PrimaryUIPanel (Functional Box)

A sleek UI panel for primary user interactions with:

- Text entry for query input
- Attachments toggle section
- Next step buttons for guided workflow

```tsx
import PrimaryUIPanel from './components/universal/PrimaryUIPanel';

<PrimaryUIPanel
  placeholder="What do you want to accomplish?"
  onSubmit={(value, attachments) => {
    /* Handle submission */
  }}
  onNext={autoConfig => {
    /* Handle next step */
  }}
  styleConfig={
    {
      /* Optional style overrides */
    }
  }
  isFloating={true}
/>;
```

### ProgressPanel (Secondary Floating Box)

A floating HUD-like panel that shows:

- Sequential numbered progress steps
- Selected options summary
- Estimated cost
- Submit button

```tsx
import ProgressPanel from './components/universal/ProgressPanel';

const steps = [
  { id: 'step1', label: 'Input' },
  { id: 'step2', label: 'Select' },
  { id: 'step3', label: 'Review' },
];

<ProgressPanel
  steps={steps}
  currentStep="step2"
  summary={{
    options: { Models: 'GPT-4, Claude-3' },
    cost: '$5.75',
  }}
  onSubmit={() => {
    /* Handle submission */
  }}
  styleConfig={
    {
      /* Optional style overrides */
    }
  }
/>;
```

## Styling System

The container styling system is highly customizable with:

### Style Configuration Schema

```typescript
interface ContainerStyleConfig {
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
```

### Predefined Themes

The system includes several predefined themes:

- **Cyberpunk** - High-tech with neon accents and floating elements
- **Futuristic** - Clean interfaces with holographic elements
- **Corporate** - Professional, minimal styling
- **Virtual Reality** - Sci-fi inspired with energy fields

### Theme Styler

Use the ThemeStyler component to visually customize containers:

```tsx
import { ThemeStylerProvider, ThemeStylerPanel } from './theme/ThemeStyler';

// Wrap your app or section with the provider
<ThemeStylerProvider>
  <YourComponents />

  {/* Open the theme panel when needed */}
  <ThemeStylerPanel
    containerType="primary"
    onClose={() => {
      /* Handle close */
    }}
  />
</ThemeStylerProvider>;
```

## Usage Example

```tsx
import React from 'react';
import { ThemeStylerProvider, useThemeStyler } from './theme/ThemeStyler';
import PrimaryUIPanel from './components/universal/PrimaryUIPanel';
import ProgressPanel from './components/universal/ProgressPanel';

const YourComponent = () => {
  const { getStyleConfig } = useThemeStyler();

  // Get style configurations for different container types
  const primaryStyle = getStyleConfig('primary');
  const progressStyle = getStyleConfig('progress');

  return (
    <div className="flex gap-8">
      {/* Primary UI Panel */}
      <PrimaryUIPanel
        placeholder="What would you like to analyze?"
        styleConfig={primaryStyle}
        onNext={autoConfig => {
          /* Handle next */
        }}
      />

      {/* Progress Panel */}
      <ProgressPanel
        steps={
          [
            /* Your steps */
          ]
        }
        currentStep="step1"
        styleConfig={progressStyle}
      />
    </div>
  );
};

// Wrap with provider at a higher level
const App = () => (
  <ThemeStylerProvider>
    <YourComponent />
  </ThemeStylerProvider>
);

export default App;
```

## Design Philosophy

The Universal UI Container System is built on the principle of separating functional structure from visual styling. This allows for:

1. **Consistent User Experience** - Functional elements maintain their usability regardless of theming
2. **Rapid Visual Customization** - Change the look and feel without altering functionality
3. **Theme Adaptability** - Components adjust dynamically to the active theme
4. **Flexible Decoration** - Optional visual elements like drones and neon trim can be toggled
5. **Cohesive Styling** - All components follow the same visual language when styled together

This approach enables designers and developers to create interfaces that are both functionally consistent and visually distinctive.
