# Suggestion Rules Engine Design Document

## Overview

The Suggestion Rules Engine is a key component of the UltraAI Suggestion System that processes user context and activity data to generate relevant, timely, and helpful suggestions. It serves as the "brain" of the guidance system, applying rules to determine what suggestions would benefit the user at any given moment.

## Architecture

```
┌──────────────────────┐     ┌──────────────────────┐     ┌──────────────────────┐
│                      │     │                      │     │                      │
│   Context Input      │────▶│   Rules Processor    │────▶│   Ranking Engine     │
│                      │     │                      │     │                      │
└──────────────────────┘     └──────────────────────┘     └──────────────────────┘
         │                            │                            │
         │                            │                            │
         ▼                            ▼                            ▼
┌──────────────────────┐     ┌──────────────────────┐     ┌──────────────────────┐
│                      │     │                      │     │                      │
│   Rule Definition    │     │   Suggestion Pool    │     │ Suggestion Output    │
│   Repository         │     │                      │     │                      │
└──────────────────────┘     └──────────────────────┘     └──────────────────────┘
```

## Components

### 1. Context Input

Receives and normalizes context data from the Context Analyzer, making it ready for rule processing.

#### Input Structure

```json
{
  "timestamp": "2025-04-29T10:15:00Z",
  "userContext": {
    "userId": "user123",
    "experienceLevel": "intermediate",
    "currentActivity": "dataSynthesis",
    "activeFeatures": ["conflictAnalysis"],
    "recentFeatures": ["stakeholderMapping", "timeHorizonAnalysis"]
  },
  "activityContext": {
    "duration": 180,
    "interactions": 15,
    "sequence": ["open", "configure", "run", "pause", "modify", "run"],
    "hesitations": [
      {
        "feature": "advancedOptions",
        "duration": 25,
        "occurrences": 2
      }
    ]
  },
  "systemContext": {
    "availableFeatures": ["basicAnalysis", "advancedOptions", "exportResults"],
    "recentUpdates": ["timeHorizonVisualization", "stakeholderComparison"]
  }
}
```

### 2. Rule Definition Repository

Stores and manages the rules that power the suggestion system.

#### Rule Structure

```json
{
  "ruleId": "feature-discovery-001",
  "name": "Time Horizon Advanced Features",
  "description": "Suggests advanced time horizon analysis features when appropriate",
  "version": "1.0.0",
  "conditions": [
    {
      "type": "featureUsage",
      "feature": "timeHorizonAnalysis",
      "operator": ">=",
      "value": 3
    },
    {
      "type": "experienceLevel",
      "operator": ">=",
      "value": "intermediate"
    },
    {
      "type": "hesitation",
      "feature": "advancedOptions",
      "operator": ">",
      "value": 1
    }
  ],
  "suggestionTemplate": {
    "type": "featureDiscovery",
    "title": "Unlock Advanced Time Analysis",
    "description": "You seem familiar with time horizon analysis. Did you know you can compare multiple time horizons simultaneously?",
    "action": {
      "type": "showFeature",
      "feature": "multiTimeHorizonComparison"
    },
    "priority": {
      "base": 70,
      "modifiers": [
        {
          "factor": "hesitationCount",
          "weight": 5
        },
        {
          "factor": "usageCount",
          "weight": 2
        }
      ]
    },
    "style": {
      "theme": "cyberpunk",
      "prominence": "medium",
      "icon": "timeline-advanced"
    }
  }
}
```

### 3. Rules Processor

Evaluates context against defined rules to generate applicable suggestions.

#### Processing Flow

1. Load relevant rules based on initial context filtering
2. Apply condition evaluations to each rule
3. Generate suggestion candidates from matching rules
4. Enrich suggestions with context-specific values
5. Pass qualified suggestions to the ranking engine

#### Implementation Approach

- Rule indexing for efficient lookup
- Condition evaluation optimization
- Support for complex conditions with AND/OR logic
- Real-time rule updates without service restart

### 4. Suggestion Pool

Temporary storage of generated suggestions before ranking and filtering.

#### Data Structure

```json
[
  {
    "id": "suggestion-20250429-001",
    "ruleId": "feature-discovery-001",
    "timestamp": "2025-04-29T10:15:05Z",
    "type": "featureDiscovery",
    "title": "Unlock Advanced Time Analysis",
    "description": "You seem familiar with time horizon analysis. Did you know you can compare multiple time horizons simultaneously?",
    "action": {
      "type": "showFeature",
      "feature": "multiTimeHorizonComparison"
    },
    "rawScore": 85,
    "context": {
      "hesitationCount": 3,
      "usageCount": 5
    },
    "style": {
      "theme": "cyberpunk",
      "prominence": "medium",
      "icon": "timeline-advanced"
    }
  },
  {
    "id": "suggestion-20250429-002",
    "ruleId": "workflow-optimization-003",
    "timestamp": "2025-04-29T10:15:05Z",
    "type": "workflowTip",
    "title": "Streamline Your Analysis",
    "description": "Save time by using the batch processing option for multiple datasets.",
    "action": {
      "type": "showTutorial",
      "tutorialId": "batch-processing"
    },
    "rawScore": 65,
    "context": {
      "repetitiveActions": 4,
      "timeSpent": 120
    },
    "style": {
      "theme": "cyberpunk",
      "prominence": "low",
      "icon": "optimize"
    }
  }
]
```

### 5. Ranking Engine

Prioritizes suggestions based on relevance, timing, and user preferences.

#### Ranking Factors

- Base priority from rule definition
- Context-specific modifiers
- User preference alignment
- Suggestion freshness
- Previous interaction with similar suggestions
- Current user cognitive load estimate

#### Ranking Algorithm

```javascript
function calculateFinalScore(suggestion, userContext) {
  let score = suggestion.rawScore;

  // Apply context modifiers
  suggestion.priority.modifiers.forEach(modifier => {
    const contextValue = suggestion.context[modifier.factor] || 0;
    score += contextValue * modifier.weight;
  });

  // Apply user preference adjustments
  const preferenceMultiplier = getUserPreferenceMultiplier(
    userContext.preferences,
    suggestion.type
  );
  score *= preferenceMultiplier;

  // Apply recency decay if the suggestion has been shown before
  if (suggestion.lastShown) {
    const hoursSinceLastShown = (Date.now() - new Date(suggestion.lastShown)) / (1000 * 60 * 60);
    const recencyDecay = Math.min(1, hoursSinceLastShown / 24); // Full value after 24 hours
    score *= recencyDecay;
  }

  // Cap at 100
  return Math.min(100, Math.max(0, score));
}
```

### 6. Suggestion Output

Finalizes and delivers ranked suggestions to the presentation layer.

#### Output Structure

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

## Design Considerations

### Performance

- Efficient rule evaluation for real-time suggestions
- Lazy loading of rule definitions
- Caching of frequently used rules
- Background processing for non-urgent suggestions

### Flexibility

- Rule templates for common suggestion patterns
- Dynamic rule updates without system restart
- Pluggable condition evaluators
- Custom scoring modifiers

### User Experience

- Anti-annoyance protection (frequency limits, do-not-disturb options)
- Adaptive suggestion frequency based on user engagement
- Suggestion dismissal learning
- Progressive suggestion complexity based on user experience

### Cyberpunk Integration

- Terminal-inspired suggestion formatting
- "Neural network" theming for rule visualization
- Digital distortion effects on hover/interaction
- Suggestion delivery with subtle glitch animation

## Implementation Phases

### Phase 1 (MVP)

- Basic rule structure and evaluation
- Simple scoring algorithm
- Core rule templates
- Minimal UI integration

### Phase 2

- Advanced condition types
- Improved ranking algorithm
- User preference integration
- Suggestion analytics

### Phase 3

- Machine learning enhancements
- Dynamic rule generation
- A/B testing framework
- Full cyberpunk styling

## Success Metrics

- Suggestion acceptance rate (target: >30%)
- Feature discovery improvements (target: 40% reduction in time to discover)
- User rating of suggestions (target: >4/5 average)
- Performance impact (target: <50ms per suggestion generation)

## Next Steps

1. Define core rule templates
2. Implement rule evaluation engine
3. Create basic scoring algorithm
4. Design suggestion presentation components
5. Develop analytics for measuring effectiveness
