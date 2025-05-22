# Animation Guidelines

## Overview

Animations in the UltraAI design system enhance the cyberpunk aesthetic while providing meaningful feedback and smooth transitions. The animation system balances visual spectacle with performance and accessibility, ensuring a premium experience across all devices.

## Animation Principles

### 1. Purpose-Driven Motion
Every animation serves a functional purpose:
- **Feedback**: Confirm user actions (button presses, form submissions)
- **Status**: Indicate loading, processing, or completion states  
- **Guidance**: Direct attention to important elements
- **Continuity**: Maintain context during transitions

### 2. Performance-First
- Use CSS transforms and opacity for optimal performance
- Prefer hardware-accelerated properties (`transform`, `opacity`)
- Avoid animating layout properties (`width`, `height`, `top`, `left`)
- Implement `will-change` sparingly and remove after animation

### 3. Accessibility Respect
- Honor `prefers-reduced-motion` settings
- Provide static alternatives for essential information
- Keep essential functionality available without animation

## Core Animation System

### Duration Scale
```css
/* Duration tokens */
:root {
  --duration-instant: 0ms;
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;
  --duration-slower: 600ms;
  --duration-slowest: 1000ms;
}
```

### Easing Functions
```css
/* Easing tokens */
:root {
  --ease-linear: linear;
  --ease-in: cubic-bezier(0.4, 0.0, 1, 1);
  --ease-out: cubic-bezier(0.0, 0.0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0.0, 0.2, 1);
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
  --ease-elastic: cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
```

## Cyberpunk Signature Animations

### Neon Glow Effects

#### Pulsing Neon Text
```css
@keyframes neon-pulse {
  0%, 100% {
    text-shadow: 
      0 0 5px currentColor,
      0 0 10px currentColor,
      0 0 20px currentColor;
    opacity: 1;
  }
  50% {
    text-shadow: 
      0 0 10px currentColor,
      0 0 20px currentColor,
      0 0 30px currentColor,
      0 0 40px currentColor;
    opacity: 0.9;
  }
}

.neon-pulse {
  animation: neon-pulse var(--duration-slower) var(--ease-in-out) infinite;
}
```

#### Neon Border Glow
```css
@keyframes neon-border-pulse {
  0%, 100% {
    box-shadow: 
      0 0 0 1px hsl(var(--neon-cyan)),
      0 0 10px hsl(var(--neon-cyan) / 0.3);
  }
  50% {
    box-shadow: 
      0 0 0 2px hsl(var(--neon-cyan)),
      0 0 20px hsl(var(--neon-cyan) / 0.5),
      0 0 30px hsl(var(--neon-cyan) / 0.3);
  }
}

.neon-border-pulse {
  animation: neon-border-pulse 2s var(--ease-in-out) infinite;
}
```

### Digital Glitch Effects

#### Text Glitch
```css
@keyframes glitch {
  0% { 
    transform: translate(0);
    filter: hue-rotate(0deg);
  }
  10% { 
    transform: translate(-2px, 2px);
    filter: hue-rotate(90deg);
  }
  20% { 
    transform: translate(-2px, -2px);
    filter: hue-rotate(180deg);
  }
  30% { 
    transform: translate(2px, 2px);
    filter: hue-rotate(270deg);
  }
  40% { 
    transform: translate(2px, -2px);
    filter: hue-rotate(360deg);
  }
  50% { 
    transform: translate(-1px, 1px);
    filter: hue-rotate(45deg);
  }
  60% { 
    transform: translate(-1px, -1px);
    filter: hue-rotate(135deg);
  }
  70% { 
    transform: translate(1px, 1px);
    filter: hue-rotate(225deg);
  }
  80% { 
    transform: translate(1px, -1px);
    filter: hue-rotate(315deg);
  }
  90% { 
    transform: translate(-1px, 1px);
    filter: hue-rotate(405deg);
  }
  100% { 
    transform: translate(0);
    filter: hue-rotate(0deg);
  }
}

.glitch-text {
  animation: glitch var(--duration-slow) var(--ease-linear) infinite;
}

/* Reduced motion version */
@media (prefers-reduced-motion: reduce) {
  .glitch-text {
    animation: none;
    filter: none;
  }
}
```

#### Scan Line Effect
```css
@keyframes scan-line {
  0% {
    transform: translateY(-100%);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(100vh);
    opacity: 0;
  }
}

.scan-line {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent, 
    hsl(var(--neon-cyan)), 
    transparent
  );
  animation: scan-line 3s var(--ease-linear) infinite;
  pointer-events: none;
  z-index: 1000;
}
```

### Matrix/Grid Effects

#### Grid Background Animation
```css
@keyframes grid-pulse {
  0%, 100% {
    opacity: 0.1;
  }
  50% {
    opacity: 0.3;
  }
}

.grid-background {
  position: absolute;
  inset: 0;
  opacity: 0.1;
  background-image: 
    linear-gradient(hsl(var(--neon-cyan) / 0.5) 1px, transparent 1px),
    linear-gradient(90deg, hsl(var(--neon-cyan) / 0.5) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: grid-pulse 4s var(--ease-in-out) infinite;
}
```

## Interactive Animations

### Button Interactions

#### Cyberpunk Button Hover
```css
.btn-cyberpunk {
  position: relative;
  overflow: hidden;
  transition: all var(--duration-normal) var(--ease-out);
}

.btn-cyberpunk::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    hsl(var(--neon-cyan) / 0.3),
    transparent
  );
  transition: left var(--duration-slow) var(--ease-out);
}

.btn-cyberpunk:hover::before {
  left: 100%;
}

.btn-cyberpunk:hover {
  box-shadow: 
    0 0 20px hsl(var(--neon-cyan) / 0.4),
    0 0 40px hsl(var(--neon-cyan) / 0.2);
  transform: translateY(-2px);
}

.btn-cyberpunk:active {
  transform: translateY(0);
  transition-duration: var(--duration-fast);
}
```

#### Button Loading State
```css
@keyframes loading-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
}

@keyframes loading-spinner {
  to {
    transform: rotate(360deg);
  }
}

.btn-loading {
  position: relative;
  color: transparent;
}

.btn-loading::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 20px;
  height: 20px;
  margin: -10px 0 0 -10px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: loading-spinner var(--duration-slower) var(--ease-linear) infinite;
}
```

### Form Interactions

#### Input Focus Animation
```css
.input-cyberpunk {
  position: relative;
  transition: all var(--duration-normal) var(--ease-out);
}

.input-cyberpunk::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 2px;
  background: hsl(var(--neon-cyan));
  transition: all var(--duration-normal) var(--ease-out);
  transform: translateX(-50%);
}

.input-cyberpunk:focus::after {
  width: 100%;
}

.input-cyberpunk:focus {
  transform: translateY(-2px);
  box-shadow: 
    0 0 15px hsl(var(--neon-cyan) / 0.3),
    0 4px 8px hsl(var(--background) / 0.8);
}
```

#### File Upload Drag Animation
```css
.file-upload {
  transition: all var(--duration-normal) var(--ease-out);
}

.file-upload.dragover {
  transform: scale(1.02);
  box-shadow: 
    0 0 30px hsl(var(--neon-cyan) / 0.4),
    inset 0 0 30px hsl(var(--neon-cyan) / 0.1);
}

@keyframes upload-pulse {
  0%, 100% {
    border-color: hsl(var(--neon-cyan) / 0.5);
  }
  50% {
    border-color: hsl(var(--neon-cyan));
  }
}

.file-upload.dragover {
  animation: upload-pulse 1s var(--ease-in-out) infinite;
}
```

## Page Transitions

### Route Transitions
```css
/* Page enter animation */
@keyframes page-enter {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Page exit animation */
@keyframes page-exit {
  from {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  to {
    opacity: 0;
    transform: translateY(-20px) scale(0.98);
  }
}

.page-transition-enter {
  animation: page-enter var(--duration-slow) var(--ease-out);
}

.page-transition-exit {
  animation: page-exit var(--duration-normal) var(--ease-in);
}
```

### Modal Animations
```css
/* Modal backdrop */
@keyframes modal-backdrop-enter {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Modal panel */
@keyframes modal-panel-enter {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-backdrop {
  animation: modal-backdrop-enter var(--duration-normal) var(--ease-out);
}

.modal-panel {
  animation: modal-panel-enter var(--duration-normal) var(--ease-out);
}
```

## Data Visualization Animations

### Chart Animations
```css
/* Chart data reveal */
@keyframes chart-reveal {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.chart-container {
  animation: chart-reveal var(--duration-slow) var(--ease-out);
}

/* Bar chart growth */
@keyframes bar-grow {
  from {
    transform: scaleY(0);
    transform-origin: bottom;
  }
  to {
    transform: scaleY(1);
    transform-origin: bottom;
  }
}

.chart-bar {
  animation: bar-grow var(--duration-slow) var(--ease-out);
}
```

### Progress Animations
```css
@keyframes progress-fill {
  from {
    width: 0%;
  }
  to {
    width: var(--progress-width);
  }
}

.progress-bar {
  animation: progress-fill var(--duration-slower) var(--ease-out);
}

/* Indeterminate progress */
@keyframes progress-indeterminate {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.progress-indeterminate::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    hsl(var(--neon-cyan)),
    transparent
  );
  animation: progress-indeterminate 2s var(--ease-linear) infinite;
}
```

## Performance Optimization

### Hardware Acceleration
```css
/* Enable hardware acceleration for smooth animations */
.accelerated {
  will-change: transform, opacity;
  transform: translateZ(0); /* Force hardware acceleration */
}

/* Remove will-change after animation */
.animation-complete {
  will-change: auto;
}
```

### Reduced Motion Support
```css
/* Disable complex animations for reduced motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
  
  /* Keep essential feedback animations */
  .btn:hover,
  .input:focus {
    transition-duration: var(--duration-fast) !important;
  }
  
  /* Remove complex effects */
  .neon-pulse,
  .glitch-text,
  .scan-line {
    animation: none !important;
  }
}
```

## Implementation with Framer Motion

### Basic Setup
```tsx
import { motion } from 'framer-motion';

const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.3, ease: "easeOut" }
};

const Component = () => (
  <motion.div {...fadeInUp}>
    Content
  </motion.div>
);
```

### Cyberpunk Button with Framer Motion
```tsx
const CyberpunkButton = ({ children, ...props }) => {
  return (
    <motion.button
      className="btn-cyberpunk"
      whileHover={{ 
        scale: 1.02,
        boxShadow: "0 0 30px hsl(var(--neon-cyan) / 0.4)"
      }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: "spring", stiffness: 400, damping: 17 }}
      {...props}
    >
      {children}
    </motion.button>
  );
};
```

### Staggered List Animation
```tsx
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
};

const StaggeredList = ({ items }) => (
  <motion.ul
    variants={container}
    initial="hidden"
    animate="show"
  >
    {items.map((item, index) => (
      <motion.li key={index} variants={item}>
        {item}
      </motion.li>
    ))}
  </motion.ul>
);
```

## Testing and Debugging

### Animation Performance
```css
/* Highlight repainting elements */
* {
  outline: 1px solid red !important;
}

/* Monitor FPS */
.fps-monitor {
  position: fixed;
  top: 10px;
  right: 10px;
  background: black;
  color: lime;
  padding: 10px;
  font-family: monospace;
  z-index: 9999;
}
```

### Animation States
```tsx
// Debug animation states
const [animationState, setAnimationState] = useState('idle');

const handleAnimationStart = () => setAnimationState('animating');
const handleAnimationEnd = () => setAnimationState('complete');

<motion.div
  onAnimationStart={handleAnimationStart}
  onAnimationComplete={handleAnimationEnd}
  className={`debug-${animationState}`}
>
```

---

**Next**: Review [Responsive Patterns](./responsive-patterns.md) for mobile and desktop guidelines.