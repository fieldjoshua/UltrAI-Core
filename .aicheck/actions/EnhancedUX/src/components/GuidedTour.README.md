# Guided Tour Component

A customizable, cyberpunk-themed guided tour component for progressive feature discovery in UltraAI applications.

## Features

- Cyberpunk-themed styling with neon effects and animations
- Step-by-step guided tours with customizable content
- Element highlighting for visual focus
- Responsive design that works on all screen sizes
- Supports images, extra content, and custom positioning
- Keyboard navigation and accessibility features
- Integrated with user experience tracking

## Installation

The GuidedTour component is part of the EnhancedUX action package. Import it directly:

```jsx
import GuidedTour from '.aicheck/actions/EnhancedUX/src/components/GuidedTour';
import '.aicheck/actions/EnhancedUX/src/components/GuidedTour.css';
```

## Basic Usage

```jsx
import React, { useState } from 'react';
import GuidedTour from '.aicheck/actions/EnhancedUX/src/components/GuidedTour';
import '.aicheck/actions/EnhancedUX/src/components/GuidedTour.css';

function MyComponent() {
  const [isTourOpen, setIsTourOpen] = useState(false);

  // Define your tour steps
  const tourSteps = [
    {
      target: '#first-element', // CSS selector for the target element
      title: 'Welcome to the Tour',
      content: 'This tour will guide you through the key features.',
      placement: 'bottom', // tooltip placement
    },
    {
      target: '#second-element',
      title: 'Important Feature',
      content: 'This feature helps you accomplish X.',
      placement: 'right',
      image: '/path/to/image.jpg', // optional image
    }
  ];

  return (
    <div>
      <button onClick={() => setIsTourOpen(true)}>Start Tour</button>

      {/* Elements to be highlighted in the tour */}
      <div id="first-element">First Feature</div>
      <div id="second-element">Second Feature</div>

      {/* Guided Tour Component */}
      <GuidedTour
        steps={tourSteps}
        isOpen={isTourOpen}
        onComplete={() => setIsTourOpen(false)}
        onSkip={() => setIsTourOpen(false)}
      />
    </div>
  );
}
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `steps` | Array | Required | Array of step objects defining the tour |
| `isOpen` | Boolean | `false` | Controls whether the tour is visible |
| `startAt` | Number | `0` | Index of the starting step |
| `onComplete` | Function | - | Callback when tour is completed |
| `onSkip` | Function | - | Callback when tour is skipped |
| `onStepChange` | Function | - | Callback when step changes, receives `(stepIndex, stepData)` |
| `className` | String | `''` | Additional CSS class for styling |

## Step Configuration

Each step in the `steps` array should be an object with the following properties:

```js
{
  // Required properties
  title: 'Step Title',
  content: 'Step description text',

  // Target element (optional but recommended)
  target: '#element-selector', // CSS selector for the target element

  // Optional properties
  placement: 'bottom', // Positioning: 'top', 'right', 'bottom', 'left', 'auto'
  image: '/path/to/image.jpg', // Optional image URL
  imageAlt: 'Image description', // Alt text for image

  // Advanced usage
  extraContent: <div>Additional React component</div>, // Extra content (React node)
  highlightPadding: 8, // Additional padding for highlight (px)
}
```

## Styling

The component comes with cyberpunk-themed styling by default. You can customize the appearance by:

1. Modifying CSS variables in your stylesheet:

```css
:root {
  --tour-primary: #00f0ff; /* Primary neon color */
  --tour-secondary: #ff00aa; /* Secondary neon color */
  --tour-background: rgba(13, 15, 25, 0.95); /* Tour background */
  --tour-text: #ffffff; /* Text color */
  --tour-border-glow: 0 0 10px rgba(0, 240, 255, 0.8); /* Glow effect */
  --tour-highlight-glow: 0 0 20px rgba(255, 0, 170, 0.6); /* Highlight glow */
}
```

2. Using the `className` prop to add custom styles:

```jsx
<GuidedTour
  className="my-custom-tour"
  // other props...
/>
```

## Integration with Experience Tracking

For full integration with the experience tracking system:

```jsx
import { FeatureDiscovery, FEATURE_CATEGORIES } from '.aicheck/actions/EnhancedUX/src/feature_discovery';

function MyApp() {
  // Create feature discovery instance
  const featureDiscovery = new FeatureDiscovery({
    onTourCompleted: (tour) => {
      console.log(`Tour ${tour.id} completed!`);
    }
  });

  // Register your tour
  featureDiscovery.registerTour('main-features', {
    name: 'Main Features Tour',
    description: 'Discover the key features of UltraAI',
    category: FEATURE_CATEGORIES.ESSENTIAL,
    steps: tourSteps
  });

  const startTour = () => {
    featureDiscovery.startTour('main-features');
  };

  // Rest of your component...
}
```

## Accessibility

The GuidedTour component supports keyboard navigation and includes appropriate ARIA attributes. Users can navigate through the tour using:

- `Tab` to focus on buttons
- `Enter` or `Space` to activate buttons
- `Escape` to close the tour

## Example

Check the TourExample component for a complete implementation example:

```
.aicheck/actions/EnhancedUX/src/examples/TourExample.jsx
.aicheck/actions/EnhancedUX/src/examples/TourExample.css
```
