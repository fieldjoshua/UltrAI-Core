# Contextual Help Component

A cyberpunk-styled component for providing contextual help through tooltips, popovers, and hints in UltraAI applications.

## Features

- Three different types: tooltip, popover, and hint
- Cyberpunk styling with neon glows and animations
- Smart positioning that adapts to available space
- Support for titles, images, and HTML content
- Multiple trigger options (hover, click, manual)
- Auto-dismiss functionality
- Keyboard navigation and accessibility features

## Installation

The ContextualHelp component is part of the EnhancedUX action package. Import it directly:

```jsx
import { ContextualHelp } from '.aicheck/actions/EnhancedUX/src/components';
import '.aicheck/actions/EnhancedUX/src/components/ContextualHelp.css';
```

## Basic Usage

```jsx
import React from 'react';
import { ContextualHelp } from '.aicheck/actions/EnhancedUX/src/components';
import '.aicheck/actions/EnhancedUX/src/components/ContextualHelp.css';

function MyComponent() {
  return (
    <div>
      {/* Element that will trigger the tooltip */}
      <button id="help-trigger">Help</button>

      {/* Basic tooltip that appears on hover */}
      <ContextualHelp
        targetId="help-trigger"
        content="This is a simple tooltip with helpful information."
        trigger="hover"
        type="tooltip"
      />
    </div>
  );
}
```

## Component Types

### Tooltip

A simple, small popup for brief explanations:

```jsx
<ContextualHelp
  targetId="element-id"
  content="Brief explanation here."
  type="tooltip"
/>
```

### Popover

A larger popup with a title and more detailed information:

```jsx
<ContextualHelp
  targetId="element-id"
  title="FEATURE NAME"
  content="More detailed explanation with additional context."
  type="popover"
/>
```

### Hint

An attention-grabbing notification for new features or important information:

```jsx
<ContextualHelp
  targetId="element-id"
  title="NEW FEATURE"
  content="You've unlocked a new capability!"
  type="hint"
  isOpen={true}
/>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `targetId` | String | Required | ID or CSS selector of the target element |
| `content` | String | Required | Content to display in the tooltip/popover |
| `title` | String | - | Optional title for the tooltip/popover |
| `position` | String | 'auto' | Position relative to target ('top', 'right', 'bottom', 'left', 'auto') |
| `trigger` | String | 'hover' | How the tooltip is triggered ('hover', 'click', 'manual') |
| `type` | String | 'tooltip' | Type of help component ('tooltip', 'popover', 'hint') |
| `isOpen` | Boolean | false | Whether the tooltip is open (for manual control) |
| `onClose` | Function | - | Callback when the tooltip is closed |
| `className` | String | '' | Additional CSS class for styling |
| `showIcon` | Boolean | true | Whether to show the help icon |
| `allowHtml` | Boolean | false | Whether to allow HTML in the content |
| `image` | String | - | URL of an optional image |
| `imageAlt` | String | - | Alt text for the image |
| `delay` | Number | 300 | Delay before showing tooltip (ms) |
| `duration` | Number | 0 | Duration to show tooltip (ms, 0 for indefinite) |

## Trigger Types

### Hover

Show on mouse hover over the target element:

```jsx
<ContextualHelp
  targetId="element-id"
  content="Appears on hover."
  trigger="hover"
/>
```

### Click

Show when the target element is clicked:

```jsx
<ContextualHelp
  targetId="element-id"
  content="Appears on click."
  trigger="click"
/>
```

### Manual

Manually control visibility through the `isOpen` prop:

```jsx
<ContextualHelp
  targetId="element-id"
  content="Manually controlled."
  trigger="manual"
  isOpen={isTooltipOpen}
  onClose={() => setIsTooltipOpen(false)}
/>
```

## Styling

The component comes with cyberpunk-themed styling by default. You can customize the appearance by:

1. Modifying CSS variables in your stylesheet:

```css
:root {
  --help-primary: #00f0ff; /* Primary neon color */
  --help-secondary: #ff00aa; /* Secondary neon color */
  --help-background: rgba(13, 15, 25, 0.95); /* Background color */
  --help-text: #ffffff; /* Text color */
  --help-border-glow: 0 0 10px rgba(0, 240, 255, 0.7); /* Glow effect */
  --help-tooltip-glow: 0 0 15px rgba(255, 0, 170, 0.5); /* Tooltip glow */
  --help-hint-glow: 0 0 15px rgba(255, 204, 0, 0.5); /* Hint glow */
}
```

2. Using the `className` prop to add custom styles:

```jsx
<ContextualHelp
  className="my-custom-tooltip"
  // other props...
/>
```

## Advanced Features

### HTML Content

Display rich HTML content:

```jsx
<ContextualHelp
  targetId="element-id"
  content="<strong>Bold text</strong> and <em>italics</em><br>With line breaks."
  allowHtml={true}
/>
```

### Auto-dismiss

Show a tooltip for a limited time:

```jsx
<ContextualHelp
  targetId="element-id"
  content="This will disappear after 5 seconds."
  duration={5000}
/>
```

### Images

Include images in popovers:

```jsx
<ContextualHelp
  targetId="element-id"
  title="FEATURE OVERVIEW"
  content="Visual explanation of the feature."
  image="/path/to/image.jpg"
  imageAlt="Feature illustration"
  type="popover"
/>
```

## Accessibility

The ContextualHelp component includes appropriate ARIA attributes and supports keyboard navigation:

- For tooltips and popovers, ESC key dismisses them
- Click outside a popover or hint will dismiss it
- Proper focus management for keyboard navigation

## Example

Check out the HelpExample component for a complete implementation example:

```
.aicheck/actions/EnhancedUX/src/examples/HelpExample.jsx
.aicheck/actions/EnhancedUX/src/examples/HelpExample.css
```
