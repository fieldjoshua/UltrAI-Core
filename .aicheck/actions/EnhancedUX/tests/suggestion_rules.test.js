/**
 * Tests for suggestion_rules.js
 */

const {
  processSuggestions,
  evaluateConditions,
  generateSuggestion,
  calculateFinalScore,
  rankSuggestions,
} = require('../src/suggestion_rules');

describe('Suggestion Rules Engine', () => {
  // Sample rule for testing
  const sampleRule = {
    ruleId: 'feature-discovery-001',
    name: 'Time Horizon Advanced Features',
    description:
      'Suggests advanced time horizon analysis features when appropriate',
    version: '1.0.0',
    conditions: [
      {
        type: 'featureUsage',
        feature: 'timeHorizonAnalysis',
        operator: '>=',
        value: 3,
      },
      {
        type: 'experienceLevel',
        operator: '>=',
        value: 'intermediate',
      },
    ],
    suggestionTemplate: {
      type: 'featureDiscovery',
      title: 'Unlock Advanced Time Analysis',
      description:
        'You seem familiar with time horizon analysis. Did you know you can compare multiple time horizons simultaneously?',
      action: {
        type: 'showFeature',
        feature: 'multiTimeHorizonComparison',
      },
      priority: {
        base: 70,
        modifiers: [
          {
            factor: 'usageCount',
            weight: 2,
          },
        ],
      },
      style: {
        theme: 'cyberpunk',
        prominence: 'medium',
        icon: 'timeline-advanced',
      },
    },
  };

  // Sample context for testing
  const sampleContext = {
    timestamp: '2025-04-29T10:15:00Z',
    userContext: {
      userId: 'user123',
      experienceLevel: 'intermediate',
      currentActivity: 'dataSynthesis',
      activeFeatures: ['conflictAnalysis'],
      recentFeatures: ['stakeholderMapping', 'timeHorizonAnalysis'],
      featureUsage: {
        timeHorizonAnalysis: {
          usageCount: 5,
          lastUsed: '2025-04-28T14:30:00Z',
        },
      },
      preferences: {
        suggestionPreferences: {
          featureDiscovery: 1.1,
        },
      },
    },
    activityContext: {
      duration: 180,
      interactions: 15,
      sequence: ['open', 'configure', 'run', 'pause', 'modify', 'run'],
      hesitations: [
        {
          feature: 'advancedOptions',
          duration: 25,
          occurrences: 2,
        },
      ],
    },
    systemContext: {
      availableFeatures: ['basicAnalysis', 'advancedOptions', 'exportResults'],
      recentUpdates: ['timeHorizonVisualization', 'stakeholderComparison'],
    },
  };

  describe('evaluateConditions', () => {
    test('should evaluate featureUsage conditions correctly', () => {
      const conditions = [
        {
          type: 'featureUsage',
          feature: 'timeHorizonAnalysis',
          operator: '>=',
          value: 3,
        },
      ];

      expect(evaluateConditions(conditions, sampleContext)).toBe(true);

      const failingConditions = [
        {
          type: 'featureUsage',
          feature: 'timeHorizonAnalysis',
          operator: '>',
          value: 10,
        },
      ];

      expect(evaluateConditions(failingConditions, sampleContext)).toBe(false);
    });

    test('should evaluate experienceLevel conditions correctly', () => {
      const conditions = [
        {
          type: 'experienceLevel',
          operator: '>=',
          value: 'intermediate',
        },
      ];

      expect(evaluateConditions(conditions, sampleContext)).toBe(true);

      const failingConditions = [
        {
          type: 'experienceLevel',
          operator: '>=',
          value: 'expert',
        },
      ];

      expect(evaluateConditions(failingConditions, sampleContext)).toBe(false);
    });

    test('should evaluate hesitation conditions correctly', () => {
      const conditions = [
        {
          type: 'hesitation',
          feature: 'advancedOptions',
          operator: '>=',
          value: 2,
        },
      ];

      expect(evaluateConditions(conditions, sampleContext)).toBe(true);

      const failingConditions = [
        {
          type: 'hesitation',
          feature: 'advancedOptions',
          operator: '>',
          value: 2,
        },
      ];

      expect(evaluateConditions(failingConditions, sampleContext)).toBe(false);
    });

    test('should evaluate combined conditions with AND logic', () => {
      expect(evaluateConditions(sampleRule.conditions, sampleContext)).toBe(
        true
      );

      const mixedConditions = [
        {
          type: 'featureUsage',
          feature: 'timeHorizonAnalysis',
          operator: '>=',
          value: 3,
        },
        {
          type: 'experienceLevel',
          operator: '>=',
          value: 'expert', // This will fail
        },
      ];

      expect(evaluateConditions(mixedConditions, sampleContext)).toBe(false);
    });
  });

  describe('generateSuggestion', () => {
    test('should generate a suggestion from a rule and context', () => {
      const suggestion = generateSuggestion(sampleRule, sampleContext);

      expect(suggestion).toHaveProperty('id');
      expect(suggestion).toHaveProperty('ruleId', sampleRule.ruleId);
      expect(suggestion).toHaveProperty('timestamp');
      expect(suggestion).toHaveProperty('type', 'featureDiscovery');
      expect(suggestion).toHaveProperty(
        'title',
        'Unlock Advanced Time Analysis'
      );
      expect(suggestion).toHaveProperty('rawScore', 70);
      expect(suggestion).toHaveProperty('context.usageCount', 5);
    });
  });

  describe('calculateFinalScore', () => {
    test('should calculate the final score using modifiers', () => {
      const suggestion = {
        rawScore: 70,
        priority: {
          modifiers: [
            {
              factor: 'usageCount',
              weight: 2,
            },
          ],
        },
        context: {
          usageCount: 5,
        },
        type: 'featureDiscovery',
      };

      const score = calculateFinalScore(suggestion, sampleContext.userContext);

      // 70 (base) + (5 * 2) for usageCount = 80, then * 1.1 for preference = 88
      expect(score).toBeCloseTo(88, 0);
    });

    test('should apply recency decay', () => {
      const now = new Date();
      const twelveHoursAgo = new Date(now - 12 * 60 * 60 * 1000);

      const suggestion = {
        rawScore: 70,
        lastShown: twelveHoursAgo.toISOString(),
        type: 'featureDiscovery',
      };

      const score = calculateFinalScore(suggestion, sampleContext.userContext);

      // 70 * 0.5 (for 12hr decay) * 1.1 (preference)
      expect(score).toBeCloseTo(38.5, 0);
    });
  });

  describe('rankSuggestions', () => {
    test('should rank and filter suggestions', () => {
      const suggestions = [
        {
          id: 'suggestion-1',
          rawScore: 90,
          type: 'featureDiscovery',
        },
        {
          id: 'suggestion-2',
          rawScore: 20, // This should be filtered out
          type: 'workflowTip',
        },
        {
          id: 'suggestion-3',
          rawScore: 60,
          type: 'featureDiscovery',
        },
      ];

      const result = rankSuggestions(suggestions, sampleContext.userContext);

      expect(result).toHaveProperty('suggestions');
      expect(result.suggestions).toHaveLength(2);
      expect(result.suggestions[0].id).toBe('suggestion-1');
      expect(result.suggestions[1].id).toBe('suggestion-3');

      expect(result).toHaveProperty('metadata');
      expect(result.metadata.generatedCount).toBe(3);
      expect(result.metadata.filteredCount).toBe(1);
    });
  });

  describe('processSuggestions', () => {
    test('should process rules and generate ranked suggestions', () => {
      const rules = [
        sampleRule,
        {
          ruleId: 'feature-discovery-002',
          name: 'Expert Feature',
          conditions: [
            {
              type: 'experienceLevel',
              operator: '>=',
              value: 'expert', // This won't match
            },
          ],
          suggestionTemplate: {
            type: 'featureDiscovery',
            title: 'Expert Feature',
            description: 'For experts only',
            action: { type: 'showFeature', feature: 'expertFeature' },
            priority: { base: 80 },
            style: { theme: 'cyberpunk', prominence: 'high' },
          },
        },
        {
          ruleId: 'workflow-tip-001',
          name: 'Basic Tip',
          conditions: [
            {
              type: 'currentActivity',
              value: 'dataSynthesis',
            },
          ],
          suggestionTemplate: {
            type: 'workflowTip',
            title: 'Basic Tip',
            description: "Here's a helpful tip",
            action: { type: 'showTip', tipId: 'basic-tip' },
            priority: { base: 40 },
            style: { theme: 'cyberpunk', prominence: 'low' },
          },
        },
      ];

      const result = processSuggestions(sampleContext, rules);

      expect(result).toHaveProperty('suggestions');
      expect(result.suggestions).toHaveLength(2); // Only 2 rules match and score above threshold
      expect(result.suggestions[0].ruleId).toBe('feature-discovery-001');
      expect(result.suggestions[1].ruleId).toBe('workflow-tip-001');
    });
  });
});
