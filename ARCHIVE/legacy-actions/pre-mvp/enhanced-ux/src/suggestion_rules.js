/**
 * UltraAI Suggestion Rules Engine
 *
 * This module processes context data and applies rules to generate
 * relevant suggestions for users based on their activity and experience.
 */

/**
 * Condition evaluator functions for different condition types
 */
const conditionEvaluators = {
  /**
   * Evaluates if a feature has been used at least N times
   */
  featureUsage: (condition, context) => {
    const { feature, operator, value } = condition;
    const usageCount =
      context.userContext.featureUsage?.[feature]?.usageCount || 0;
    return compareValues(usageCount, operator, value);
  },

  /**
   * Evaluates if the user's experience level meets a requirement
   */
  experienceLevel: (condition, context) => {
    const { operator, value } = condition;
    const levels = ['beginner', 'intermediate', 'advanced', 'expert'];
    const userLevel = context.userContext.experienceLevel || 'beginner';
    const userLevelIndex = levels.indexOf(userLevel);
    const valueLevelIndex = levels.indexOf(value);

    return compareValues(userLevelIndex, operator, valueLevelIndex);
  },

  /**
   * Evaluates if the user has hesitated on a feature
   */
  hesitation: (condition, context) => {
    const { feature, operator, value } = condition;
    const hesitation = context.activityContext?.hesitations?.find(
      (h) => h.feature === feature
    );
    const occurrences = hesitation?.occurrences || 0;
    return compareValues(occurrences, operator, value);
  },

  /**
   * Evaluates if an activity is currently in progress
   */
  currentActivity: (condition, context) => {
    const { value } = condition;
    return context.userContext.currentActivity === value;
  },

  /**
   * Evaluates if a feature was recently used
   */
  recentFeature: (condition, context) => {
    const { feature } = condition;
    return context.userContext.recentFeatures?.includes(feature) || false;
  },
};

/**
 * Compares two values using the specified operator
 */
function compareValues(left, operator, right) {
  switch (operator) {
    case '==':
      return left == right;
    case '===':
      return left === right;
    case '!=':
      return left != right;
    case '!==':
      return left !== right;
    case '>':
      return left > right;
    case '>=':
      return left >= right;
    case '<':
      return left < right;
    case '<=':
      return left <= right;
    default:
      throw new Error(`Unsupported operator: ${operator}`);
  }
}

/**
 * Evaluates all conditions for a rule
 */
function evaluateConditions(conditions, context) {
  return conditions.every((condition) => {
    const evaluator = conditionEvaluators[condition.type];
    if (!evaluator) {
      console.warn(`No evaluator found for condition type: ${condition.type}`);
      return false;
    }
    return evaluator(condition, context);
  });
}

/**
 * Generates a suggestion from a rule template and context
 */
function generateSuggestion(rule, context) {
  const { suggestionTemplate } = rule;
  const timestamp = new Date().toISOString();
  const id = `suggestion-${timestamp
    .split('T')[0]
    .replace(/-/g, '')}-${Math.floor(Math.random() * 1000)
    .toString()
    .padStart(3, '0')}`;

  // Extract context values for priority calculation
  const contextValues = {};
  if (suggestionTemplate.priority?.modifiers) {
    suggestionTemplate.priority.modifiers.forEach((modifier) => {
      switch (modifier.factor) {
        case 'hesitationCount':
          const feature = rule.conditions.find(
            (c) => c.type === 'hesitation'
          )?.feature;
          const hesitation =
            feature &&
            context.activityContext?.hesitations?.find(
              (h) => h.feature === feature
            );
          contextValues.hesitationCount = hesitation?.occurrences || 0;
          break;
        case 'usageCount':
          const featureForUsage = rule.conditions.find(
            (c) => c.type === 'featureUsage'
          )?.feature;
          contextValues.usageCount =
            context.userContext.featureUsage?.[featureForUsage]?.usageCount ||
            0;
          break;
        // Add more factors as needed
      }
    });
  }

  const rawScore = suggestionTemplate.priority?.base || 50;

  return {
    id,
    ruleId: rule.ruleId,
    timestamp,
    type: suggestionTemplate.type,
    title: suggestionTemplate.title,
    description: suggestionTemplate.description,
    action: suggestionTemplate.action,
    rawScore,
    context: contextValues,
    style: suggestionTemplate.style,
  };
}

/**
 * Calculates the final score for a suggestion based on context and preferences
 */
function calculateFinalScore(suggestion, userContext) {
  let score = suggestion.rawScore;

  // Apply context modifiers
  if (suggestion.priority?.modifiers) {
    suggestion.priority.modifiers.forEach((modifier) => {
      const contextValue = suggestion.context[modifier.factor] || 0;
      score += contextValue * modifier.weight;
    });
  }

  // Apply user preference adjustments (if preference system is available)
  const preferenceMultiplier = getUserPreferenceMultiplier(
    userContext?.preferences,
    suggestion.type
  );
  score *= preferenceMultiplier;

  // Apply recency decay if the suggestion has been shown before
  if (suggestion.lastShown) {
    const hoursSinceLastShown =
      (Date.now() - new Date(suggestion.lastShown)) / (1000 * 60 * 60);
    const recencyDecay = Math.min(1, hoursSinceLastShown / 24); // Full value after 24 hours
    score *= recencyDecay;
  }

  // Cap at 100
  return Math.min(100, Math.max(0, score));
}

/**
 * Gets a preference multiplier based on user preferences
 */
function getUserPreferenceMultiplier(preferences, suggestionType) {
  if (!preferences) return 1.0;

  // Default values if user hasn't specified preferences
  const defaultMultipliers = {
    featureDiscovery: 1.0,
    workflowTip: 1.0,
    errorPrevention: 1.2, // Error prevention slightly higher by default
    performanceOptimization: 1.0,
  };

  // User-specific preference adjustments (to be implemented with the preference system)
  const userMultipliers = preferences?.suggestionPreferences || {};

  return (
    userMultipliers[suggestionType] || defaultMultipliers[suggestionType] || 1.0
  );
}

/**
 * Ranks and filters suggestions based on scores and user context
 */
function rankSuggestions(suggestions, userContext) {
  // Calculate final scores
  const scoredSuggestions = suggestions.map((suggestion) => {
    const finalScore = calculateFinalScore(suggestion, userContext);
    return { ...suggestion, finalScore };
  });

  // Sort by final score, descending
  scoredSuggestions.sort((a, b) => b.finalScore - a.finalScore);

  // Filter out low-scoring suggestions
  const minScore = 30; // Configurable threshold
  const filteredSuggestions = scoredSuggestions.filter(
    (s) => s.finalScore >= minScore
  );

  // Add metadata
  const metadata = {
    generatedCount: suggestions.length,
    filteredCount: suggestions.length - filteredSuggestions.length,
    topScore: filteredSuggestions[0]?.finalScore || 0,
    currentCognitiveLoad: estimateCognitiveLoad(userContext),
  };

  return {
    timestamp: new Date().toISOString(),
    suggestions: filteredSuggestions,
    metadata,
  };
}

/**
 * Estimates the user's current cognitive load based on context
 */
function estimateCognitiveLoad(userContext) {
  // This is a simplified placeholder implementation
  // In a real system, this would use more sophisticated analysis
  const recentInteractions = userContext.activityContext?.interactions || 0;
  const sessionDuration = userContext.activityContext?.duration || 0;

  if (recentInteractions > 30 || sessionDuration > 3600) {
    return 'high';
  } else if (recentInteractions > 15 || sessionDuration > 1800) {
    return 'medium';
  } else {
    return 'low';
  }
}

/**
 * Main function that processes context and rules to generate suggestions
 */
function processSuggestions(context, rules) {
  // Filter rules to those that match the context
  const matchingRules = rules.filter((rule) =>
    evaluateConditions(rule.conditions, context)
  );

  // Generate suggestions from matching rules
  const suggestions = matchingRules.map((rule) =>
    generateSuggestion(rule, context)
  );

  // Rank and prepare the suggestions
  return rankSuggestions(suggestions, context.userContext);
}

/**
 * Exports
 */
module.exports = {
  processSuggestions,
  evaluateConditions,
  generateSuggestion,
  calculateFinalScore,
  rankSuggestions,
};
