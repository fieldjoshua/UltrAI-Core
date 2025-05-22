# Suggestion Presenter Design Document

## Overview

The Suggestion Presenter is responsible for transforming suggestion data into interactive UI components that are visually appealing, unintrusive, and aligned with the cyberpunk aesthetic of UltraAI. This component bridges the gap between the suggestion engine's data and the user interface.

## Architecture

```
┌──────────────────────┐     ┌──────────────────────┐     ┌──────────────────────┐
│                      │     │                      │     │                      │
│   Suggestion Input   │────▶│  Presenter Manager   │────▶│   UI Components      │
│                      │     │                      │     │                      │
└──────────────────────┘     └──────────────────────┘     └──────────────────────┘
         │                            │                            │
         │                            │                            │
         ▼                            ▼                            ▼
┌──────────────────────┐     ┌──────────────────────┐     ┌──────────────────────┐
│                      │     │                      │     │                      │
│   Theme Manager      │     │ Animation Controller │     │ Interaction Handler  │
│                      │     │                      │     │                      │
└──────────────────────┘     └──────────────────────┘     └──────────────────────┘
```

## Components

### 1. Suggestion Input

Receives and processes suggestion data from the Suggestion Engine.

#### Input Structure

```json
{
  "timestamp": "2025-04-29T10:15:10Z",
  "suggestions": [
    {
      "id": "suggestion-20250429-001",
      "type": "featureDiscovery",
      "title": "Unlock Advanced Time Analysis",
      "description": "You seem familiar with time horizon analysis. Did you know you can compare multiple time horizons simultaneously?",
      "action": {
        "type": "showFeature",
        "feature": "multiTimeHorizonComparison"
      },
      "finalScore": 92,
      "style": {
        "theme": "cyberpunk",
        "prominence": "medium",
        "icon": "timeline-advanced"
      }
    }
  ],
  "metadata": {
    "generatedCount": 5,
    "filteredCount": 3,
    "topScore": 92,
    "currentCognitiveLoad": "medium"
  }
}
```

### 2. Presenter Manager

Coordinates suggestion presentation, deciding when and how to display suggestions to provide the best user experience.

#### Key Features

- **Suggestion Queue**: Manages pending suggestions to avoid overwhelming the user
- **Cognitive Load Management**: Adapts presentation based on user's current cognitive load
- **Context Awareness**: Avoids interrupting critical tasks or workflows
- **Presentation Scheduling**: Determines optimal timing for showing suggestions
- **Multi-suggestion Handling**: Groups related suggestions when appropriate

#### Presentation Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| Inline | Shows suggestion within the context of the relevant feature | Feature discovery, subtle hints |
| Notification | Small popup with minimal interruption | Tips, shortcuts, optimizations |
| Dialog | Modal with detailed information | Important features, multi-step guidance |
| Ambient | Subtle highlighting or glow around relevant UI elements | Gentle discovery guidance |
| Contextual | Appears next to the relevant UI element | Feature-specific suggestions |

### 3. Theme Manager

Controls the visual appearance of suggestions based on UltraAI's cyberpunk design system.

#### Cyberpunk Design Elements

- **Neon Glow**: Subtle pulsing borders with cyberpunk color palette
- **Digital Distortion**: Glitch effects for transitions and highlights
- **Terminal Aesthetic**: Monospace fonts and command-line inspired formatting
- **Holographic Elements**: Translucent, floating UI components
- **Neural Network Visualization**: Background patterns suggesting AI processing

#### Theme Variations

- **Standard Cyberpunk**: Default UltraAI styling
- **High Contrast**: Enhanced readability version
- **Minimal**: Reduced visual elements for less distraction
- **Intense**: Maximum cyberpunk styling with advanced effects
- **Custom**: User-defined theme preferences

### 4. Animation Controller

Manages transitions, animations, and effects for suggestion components.

#### Animation Types

- **Entry Animations**: How suggestions appear (fade, glitch, slide)
- **Idle Animations**: Subtle movements during display (pulse, float, scan)
- **Exit Animations**: How suggestions disappear (dissolve, glitch out, minimize)
- **Interaction Animations**: Visual feedback for user interactions
- **Attention Animations**: Subtle effects to draw attention when needed

#### Performance Considerations

- GPU acceleration for smooth animations
- Animation throttling based on system performance
- Reduced animations for users with motion sensitivity
- Progressive enhancement approach for less powerful devices

### 5. UI Components

The actual UI elements that display suggestions to users.

#### Core Components

- **Suggestion Card**: Primary container for suggestion content
- **Icon System**: Visual indicators for suggestion types
- **Action Buttons**: Interactive elements for user response
- **Progress Indicators**: Visual feedback on multi-step suggestions
- **Dismissal Controls**: Ways to hide or postpone suggestions

#### Component Variations by Suggestion Type

| Suggestion Type | Primary Component | Visual Style | Interaction Pattern |
|-----------------|-------------------|--------------|---------------------|
| Feature Discovery | Feature Spotlight | Highlighting with directional indicator | Click to activate or learn more |
| Workflow Tip | Floating Tooltip | Minimal, non-blocking | Hover for more details, click to apply |
| Error Prevention | Warning Card | Higher contrast, attention-grabbing | Acknowledge or take preventative action |
| Performance Optimization | Status Indicator | System-status aesthetic | Toggle or activate optimization |

### 6. Interaction Handler

Manages user interactions with suggestions and communicates with the feedback system.

#### Interaction Types

- **Direct Action**: User applies the suggestion directly
- **Learn More**: User requests additional information
- **Dismiss**: User removes the suggestion
- **Postpone**: User defers the suggestion for later
- **Rate Usefulness**: User provides explicit feedback on suggestion value

#### Implementation Approach

- Event delegation for efficient handling
- Integration with suggestion feedback system
- Analytics tracking of interaction patterns
- Accessibility support for keyboard and screen reader users

## Design Considerations

### Accessibility

- High contrast mode option
- Keyboard navigation support
- Screen reader compatibility
- Reduced motion option for animations
- Multiple interaction methods (click, keyboard, voice)

### Performance

- Lightweight rendering with minimal DOM manipulation
- Lazy loading of suggestion components
- Batched updates to avoid layout thrashing
- Web Animation API for smooth animations
- Virtual DOM implementation for complex UIs

### User Experience

- Non-disruptive presentation
- Clear dismissal options
- Consistent positioning and behavior
- Appropriate timing based on user activity
- Progressive disclosure of complex suggestions

### Cyberpunk Integration

- Authentic cyberpunk aesthetic without sacrificing usability
- Thematic animations that reinforce the UltraAI brand
- Visually distinct from standard UI patterns
- Sound design integration (optional and configurable)
- Immersive but not distracting

## Implementation Phases

### Phase 1 (MVP)

- Core suggestion card component
- Basic inline and notification presentation strategies
- Simple entry/exit animations
- Standard cyberpunk theme implementation
- Basic interaction handling

### Phase 2

- Complete presentation strategy set
- Full animation system with performance optimizations
- Advanced cyberpunk styling with theme variations
- Enhanced interaction handling with analytics integration
- Suggestion grouping and prioritization

### Phase 3

- Advanced visual effects and animations
- Full accessibility implementation
- Complete theme system with user preferences
- Sound design integration (optional)
- Performance optimizations for complex suggestion UIs

## Success Metrics

- Suggestion visibility rate (>90% of suggestions should be seen)
- Interaction rate (>40% of suggestions should receive direct interaction)
- User satisfaction with presentation (target: >4/5 rating)
- Performance impact (<16ms per frame during animations)
- Accessibility compliance (WCAG 2.1 AA standard)

## Next Steps

1. Design core suggestion card component
2. Implement basic cyberpunk styling
3. Create entry/exit animations
4. Build presenter manager with simple presentation strategies
5. Integrate with suggestion feedback system

## Component Mockups

### Feature Discovery Card

```
┌───────────────────────────────────────────────────┐
│  ╔═══════════════════════════════════════════╗    │
│  ║ [ICON] Unlock Advanced Time Analysis      ║    │
│  ║                                           ║    │
│  ║ You seem familiar with time horizon       ║    │
│  ║ analysis. Did you know you can compare    ║    │
│  ║ multiple time horizons simultaneously?    ║    │
│  ║                                           ║    │
│  ║ [ SHOW ME HOW ]     [ MAYBE LATER ]       ║    │
│  ╚═══════════════════════════════════════════╝    │
└───────────────────────────────────────────────────┘
```

### Workflow Tip

```
┌───────────────────────────────┐
│  ╔═══════════════════════╗    │
│  ║ [ICON] PRODUCTIVITY   ║    │
│  ║                       ║    │
│  ║ Speed up your workflow║    │
│  ║ with keyboard shortcut║    │
│  ║ Ctrl+Shift+A          ║    │
│  ║                       ║    │
│  ║ [ GOT IT ]   [ ✕ ]    ║    │
│  ╚═══════════════════════╝    │
└───────────────────────────────┘
```

### Error Prevention Alert

```
┌─────────────────────────────────────────────┐
│  ╔═════════════════════════════════════╗    │
│  ║ [WARNING] Configuration Check        ║    │
│  ║                                      ║    │
│  ║ Validate your settings before        ║    │
│  ║ running to avoid common errors       ║    │
│  ║                                      ║    │
│  ║ [ VALIDATE NOW ]   [ DISMISS ]       ║    │
│  ╚═════════════════════════════════════╝    │
└─────────────────────────────────────────────┘
```

## Animations

### Entry Animation Sequence

1. Initial invisible state
2. Slight glitch/distortion effect (100ms)
3. Fade in with subtle scaling (200ms)
4. Border glow pulse (300ms)
5. Settle into idle state with subtle floating motion

### Exit Animation Sequence

1. Initial idle state
2. Brief highlight/flash (100ms)
3. Glitch effect intensifies (150ms)
4. Rapid fade out with slight scale down (200ms)
5. Final pixel dispersion effect (optional, 100ms)

## Technical Implementation

The Suggestion Presenter will be implemented using a component-based architecture, compatible with modern JavaScript frameworks or as a standalone library. The implementation will focus on performance, modularity, and customizability.
