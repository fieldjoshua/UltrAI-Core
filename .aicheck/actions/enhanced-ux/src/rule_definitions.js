/**
 * UltraAI Suggestion Rules Definitions
 *
 * This module contains the rule definitions that power the suggestion system.
 * Rules define when and how to provide guidance to users based on their context.
 */

/**
 * Core rules for feature discovery
 */
const featureDiscoveryRules = [
  {
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
      {
        type: 'hesitation',
        feature: 'advancedOptions',
        operator: '>',
        value: 1,
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
            factor: 'hesitationCount',
            weight: 5,
          },
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
  },
  {
    ruleId: 'feature-discovery-002',
    name: 'Confidence Scoring Guidance',
    description: 'Introduces confidence scoring to users who are ready for it',
    version: '1.0.0',
    conditions: [
      {
        type: 'experienceLevel',
        operator: '>=',
        value: 'intermediate',
      },
      {
        type: 'featureUsage',
        feature: 'basicAnalysis',
        operator: '>=',
        value: 5,
      },
    ],
    suggestionTemplate: {
      type: 'featureDiscovery',
      title: 'Understand Your Confidence Scores',
      description:
        'Ready to take your analysis deeper? Confidence scoring helps you evaluate the reliability of your insights.',
      action: {
        type: 'showTutorial',
        tutorialId: 'confidence-scoring',
      },
      priority: {
        base: 65,
        modifiers: [
          {
            factor: 'usageCount',
            weight: 1,
          },
        ],
      },
      style: {
        theme: 'cyberpunk',
        prominence: 'medium',
        icon: 'confidence-meter',
      },
    },
  },
  {
    ruleId: 'feature-discovery-003',
    name: 'Stakeholder Mapping Introduction',
    description: 'Introduces stakeholder mapping to beginners',
    version: '1.0.0',
    conditions: [
      {
        type: 'experienceLevel',
        operator: '==',
        value: 'beginner',
      },
      {
        type: 'featureUsage',
        feature: 'basicAnalysis',
        operator: '>=',
        value: 2,
      },
    ],
    suggestionTemplate: {
      type: 'featureDiscovery',
      title: 'Map Your Stakeholders',
      description:
        'Identify key stakeholders and visualize their relationships with our stakeholder mapping tool.',
      action: {
        type: 'showFeature',
        feature: 'stakeholderMapping',
      },
      priority: {
        base: 75,
        modifiers: [],
      },
      style: {
        theme: 'cyberpunk',
        prominence: 'high',
        icon: 'network-map',
      },
    },
  },
];

/**
 * Workflow optimization tips
 */
const workflowTipRules = [
  {
    ruleId: 'workflow-tip-001',
    name: 'Batch Processing Tip',
    description: 'Suggests batch processing for repetitive tasks',
    version: '1.0.0',
    conditions: [
      {
        type: 'currentActivity',
        value: 'dataSynthesis',
      },
    ],
    suggestionTemplate: {
      type: 'workflowTip',
      title: 'Streamline Your Analysis',
      description:
        'Save time by using the batch processing option for multiple datasets.',
      action: {
        type: 'showTutorial',
        tutorialId: 'batch-processing',
      },
      priority: {
        base: 40,
        modifiers: [],
      },
      style: {
        theme: 'cyberpunk',
        prominence: 'low',
        icon: 'optimize',
      },
    },
  },
  {
    ruleId: 'workflow-tip-002',
    name: 'Keyboard Shortcuts',
    description: 'Teaches keyboard shortcuts to frequent users',
    version: '1.0.0',
    conditions: [
      {
        type: 'featureUsage',
        feature: 'any',
        operator: '>=',
        value: 10,
      },
    ],
    suggestionTemplate: {
      type: 'workflowTip',
      title: 'Power User Shortcuts',
      description:
        'Speed up your workflow with these keyboard shortcuts for common actions.',
      action: {
        type: 'showTip',
        tipId: 'keyboard-shortcuts',
      },
      priority: {
        base: 45,
        modifiers: [],
      },
      style: {
        theme: 'cyberpunk',
        prominence: 'low',
        icon: 'keyboard',
      },
    },
  },
];

/**
 * Error prevention guidance
 */
const errorPreventionRules = [
  {
    ruleId: 'error-prevention-001',
    name: 'Configuration Validation',
    description: 'Warns about potential configuration errors',
    version: '1.0.0',
    conditions: [
      {
        type: 'currentActivity',
        value: 'configure',
      },
    ],
    suggestionTemplate: {
      type: 'errorPrevention',
      title: 'Validate Your Configuration',
      description:
        "Don't forget to validate your configuration before running the analysis to avoid common errors.",
      action: {
        type: 'showTip',
        tipId: 'configuration-validation',
      },
      priority: {
        base: 80,
        modifiers: [],
      },
      style: {
        theme: 'cyberpunk',
        prominence: 'medium',
        icon: 'warning',
      },
    },
  },
];

/**
 * Performance optimization tips
 */
const performanceRules = [
  {
    ruleId: 'performance-optimization-001',
    name: 'Data Caching',
    description: 'Suggests data caching for large datasets',
    version: '1.0.0',
    conditions: [
      {
        type: 'currentActivity',
        value: 'dataSynthesis',
      },
      {
        type: 'experienceLevel',
        operator: '>=',
        value: 'intermediate',
      },
    ],
    suggestionTemplate: {
      type: 'performanceOptimization',
      title: 'Optimize Large Dataset Processing',
      description:
        'Enable data caching to dramatically improve performance with large datasets.',
      action: {
        type: 'showFeature',
        feature: 'dataCaching',
      },
      priority: {
        base: 60,
        modifiers: [],
      },
      style: {
        theme: 'cyberpunk',
        prominence: 'medium',
        icon: 'speed',
      },
    },
  },
];

/**
 * Combined rules export
 */
const allRules = [
  ...featureDiscoveryRules,
  ...workflowTipRules,
  ...errorPreventionRules,
  ...performanceRules,
];

module.exports = {
  allRules,
  featureDiscoveryRules,
  workflowTipRules,
  errorPreventionRules,
  performanceRules,
};
