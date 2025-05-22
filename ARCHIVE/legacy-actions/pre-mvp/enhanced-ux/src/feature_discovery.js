/**
 * Feature Discovery System
 *
 * Tracks user experience level and provides progressive feature disclosure
 * to help users discover UltraAI features at an appropriate pace.
 */

// Experience levels
const EXPERIENCE_LEVELS = {
  BEGINNER: 'beginner',
  INTERMEDIATE: 'intermediate',
  ADVANCED: 'advanced',
  EXPERT: 'expert',
};

// Feature categories
const FEATURE_CATEGORIES = {
  ESSENTIAL: 'essential', // Core features everyone should know
  PRODUCTIVITY: 'productivity', // Features that improve workflow efficiency
  ADVANCED_EDITING: 'advanced_editing', // Power user editing features
  CUSTOMIZATION: 'customization', // Personalization options
  COLLABORATION: 'collaboration', // Team-based features
  EXPERIMENTAL: 'experimental', // Cutting-edge features in development
};

/**
 * Maps experience levels to feature categories that should be progressively disclosed
 */
const LEVEL_TO_FEATURE_MAP = {
  [EXPERIENCE_LEVELS.BEGINNER]: [FEATURE_CATEGORIES.ESSENTIAL],
  [EXPERIENCE_LEVELS.INTERMEDIATE]: [
    FEATURE_CATEGORIES.ESSENTIAL,
    FEATURE_CATEGORIES.PRODUCTIVITY,
  ],
  [EXPERIENCE_LEVELS.ADVANCED]: [
    FEATURE_CATEGORIES.ESSENTIAL,
    FEATURE_CATEGORIES.PRODUCTIVITY,
    FEATURE_CATEGORIES.ADVANCED_EDITING,
    FEATURE_CATEGORIES.CUSTOMIZATION,
  ],
  [EXPERIENCE_LEVELS.EXPERT]: [
    FEATURE_CATEGORIES.ESSENTIAL,
    FEATURE_CATEGORIES.PRODUCTIVITY,
    FEATURE_CATEGORIES.ADVANCED_EDITING,
    FEATURE_CATEGORIES.CUSTOMIZATION,
    FEATURE_CATEGORIES.COLLABORATION,
    FEATURE_CATEGORIES.EXPERIMENTAL,
  ],
};

// Points required to advance to each level
const LEVEL_THRESHOLDS = {
  [EXPERIENCE_LEVELS.BEGINNER]: 0,
  [EXPERIENCE_LEVELS.INTERMEDIATE]: 100,
  [EXPERIENCE_LEVELS.ADVANCED]: 300,
  [EXPERIENCE_LEVELS.EXPERT]: 750,
};

// Experience points awarded for different actions
const ACTION_POINTS = {
  FEATURE_USED: 5, // Using a feature for the first time
  FEATURE_MASTERED: 15, // Using a feature regularly (10+ times)
  WORKFLOW_COMPLETED: 25, // Completing a full workflow (e.g., commit sequence)
  SHORTCUT_USED: 3, // Using a keyboard shortcut
  SUGGESTION_ACCEPTED: 2, // Following a suggestion from the system
  FEATURE_EXPLORED: 8, // Actively exploring a feature through help/docs
  CUSTOMIZATION_APPLIED: 10, // Customizing the environment/settings
};

/**
 * Class to track user experience and manage feature discovery
 */
class ExperienceTracker {
  constructor(options = {}) {
    this.userId = options.userId || 'anonymous';
    this.storage = options.storage || window.localStorage;
    this.storageKey = `ultra_experience_${this.userId}`;
    this.callbacks = {
      onLevelUp: options.onLevelUp || (() => {}),
      onFeatureUnlocked: options.onFeatureUnlocked || (() => {}),
    };

    // Initialize user data
    this.userData = this._loadUserData();
  }

  /**
   * Load user experience data from storage
   */
  _loadUserData() {
    try {
      const savedData = this.storage.getItem(this.storageKey);
      if (savedData) {
        return JSON.parse(savedData);
      }
    } catch (error) {
      console.error('Error loading experience data:', error);
    }

    // Default user data structure
    return {
      experiencePoints: 0,
      currentLevel: EXPERIENCE_LEVELS.BEGINNER,
      featuresUsed: {},
      featureUseCounts: {},
      shortcutsUsed: {},
      completedWorkflows: {},
      suggestionsAccepted: 0,
      lastActiveDate: new Date().toISOString(),
    };
  }

  /**
   * Save user experience data to storage
   */
  _saveUserData() {
    try {
      this.storage.setItem(this.storageKey, JSON.stringify(this.userData));
    } catch (error) {
      console.error('Error saving experience data:', error);
    }
  }

  /**
   * Add experience points and check for level up
   */
  addPoints(points, reason = '') {
    const previousLevel = this.userData.currentLevel;
    this.userData.experiencePoints += points;

    // Check for level up
    const newLevel = this._calculateLevel();
    if (newLevel !== previousLevel) {
      this.userData.currentLevel = newLevel;
      this.callbacks.onLevelUp(newLevel, previousLevel);

      // Check for newly unlocked features
      const previousFeatures = LEVEL_TO_FEATURE_MAP[previousLevel] || [];
      const newFeatures = LEVEL_TO_FEATURE_MAP[newLevel] || [];

      const unlockedCategories = newFeatures.filter(
        (category) => !previousFeatures.includes(category)
      );

      if (unlockedCategories.length > 0) {
        unlockedCategories.forEach((category) => {
          this.callbacks.onFeatureUnlocked(category, newLevel);
        });
      }
    }

    this._saveUserData();
    return {
      currentPoints: this.userData.experiencePoints,
      currentLevel: this.userData.currentLevel,
      leveledUp: newLevel !== previousLevel,
    };
  }

  /**
   * Calculate current level based on experience points
   */
  _calculateLevel() {
    const points = this.userData.experiencePoints;

    if (points >= LEVEL_THRESHOLDS[EXPERIENCE_LEVELS.EXPERT]) {
      return EXPERIENCE_LEVELS.EXPERT;
    } else if (points >= LEVEL_THRESHOLDS[EXPERIENCE_LEVELS.ADVANCED]) {
      return EXPERIENCE_LEVELS.ADVANCED;
    } else if (points >= LEVEL_THRESHOLDS[EXPERIENCE_LEVELS.INTERMEDIATE]) {
      return EXPERIENCE_LEVELS.INTERMEDIATE;
    } else {
      return EXPERIENCE_LEVELS.BEGINNER;
    }
  }

  /**
   * Record a feature being used
   */
  recordFeatureUsed(featureId, category) {
    if (!this.userData.featuresUsed[featureId]) {
      // First time using this feature
      this.userData.featuresUsed[featureId] = {
        firstUsed: new Date().toISOString(),
        category: category,
      };
      this.userData.featureUseCounts[featureId] = 1;

      // Award points for first time use
      this.addPoints(ACTION_POINTS.FEATURE_USED, `First use of ${featureId}`);
    } else {
      // Increment use count
      this.userData.featureUseCounts[featureId] =
        (this.userData.featureUseCounts[featureId] || 0) + 1;

      // Check for mastery (10+ uses)
      if (this.userData.featureUseCounts[featureId] === 10) {
        this.addPoints(ACTION_POINTS.FEATURE_MASTERED, `Mastered ${featureId}`);
      }
    }

    this._saveUserData();
    return this.userData.featureUseCounts[featureId];
  }

  /**
   * Record a shortcut being used
   */
  recordShortcutUsed(shortcutId) {
    if (!this.userData.shortcutsUsed[shortcutId]) {
      this.userData.shortcutsUsed[shortcutId] = {
        firstUsed: new Date().toISOString(),
        count: 1,
      };

      // Award points for first shortcut use
      this.addPoints(
        ACTION_POINTS.SHORTCUT_USED,
        `Used shortcut ${shortcutId}`
      );
    } else {
      this.userData.shortcutsUsed[shortcutId].count += 1;
    }

    this._saveUserData();
    return this.userData.shortcutsUsed[shortcutId].count;
  }

  /**
   * Record a workflow being completed
   */
  recordWorkflowCompleted(workflowId) {
    if (!this.userData.completedWorkflows[workflowId]) {
      this.userData.completedWorkflows[workflowId] = {
        firstCompleted: new Date().toISOString(),
        count: 1,
      };

      // Award points for completing a workflow
      this.addPoints(
        ACTION_POINTS.WORKFLOW_COMPLETED,
        `Completed workflow ${workflowId}`
      );
    } else {
      this.userData.completedWorkflows[workflowId].count += 1;
    }

    this._saveUserData();
    return this.userData.completedWorkflows[workflowId].count;
  }

  /**
   * Record a suggestion being accepted
   */
  recordSuggestionAccepted(suggestionId) {
    this.userData.suggestionsAccepted += 1;
    this.addPoints(
      ACTION_POINTS.SUGGESTION_ACCEPTED,
      `Accepted suggestion ${suggestionId}`
    );

    this._saveUserData();
    return this.userData.suggestionsAccepted;
  }

  /**
   * Get current user experience data
   */
  getUserExperience() {
    return {
      userId: this.userId,
      points: this.userData.experiencePoints,
      level: this.userData.currentLevel,
      featuresUnlocked: LEVEL_TO_FEATURE_MAP[this.userData.currentLevel] || [],
      nextLevelThreshold: this._getNextLevelThreshold(),
      pointsToNextLevel: this._getPointsToNextLevel(),
    };
  }

  /**
   * Get threshold for next level
   */
  _getNextLevelThreshold() {
    const currentLevel = this.userData.currentLevel;

    switch (currentLevel) {
      case EXPERIENCE_LEVELS.BEGINNER:
        return LEVEL_THRESHOLDS[EXPERIENCE_LEVELS.INTERMEDIATE];
      case EXPERIENCE_LEVELS.INTERMEDIATE:
        return LEVEL_THRESHOLDS[EXPERIENCE_LEVELS.ADVANCED];
      case EXPERIENCE_LEVELS.ADVANCED:
        return LEVEL_THRESHOLDS[EXPERIENCE_LEVELS.EXPERT];
      case EXPERIENCE_LEVELS.EXPERT:
      default:
        return null; // No next level
    }
  }

  /**
   * Get points required to reach next level
   */
  _getPointsToNextLevel() {
    const nextThreshold = this._getNextLevelThreshold();
    if (nextThreshold === null) {
      return 0; // Already at max level
    }

    return Math.max(0, nextThreshold - this.userData.experiencePoints);
  }

  /**
   * Check if a specific feature category should be available
   * based on the user's current experience level
   */
  shouldShowFeatureCategory(category) {
    const availableCategories =
      LEVEL_TO_FEATURE_MAP[this.userData.currentLevel] || [];
    return availableCategories.includes(category);
  }

  /**
   * Reset experience data (mainly for testing)
   */
  resetExperience() {
    this.userData = {
      experiencePoints: 0,
      currentLevel: EXPERIENCE_LEVELS.BEGINNER,
      featuresUsed: {},
      featureUseCounts: {},
      shortcutsUsed: {},
      completedWorkflows: {},
      suggestionsAccepted: 0,
      lastActiveDate: new Date().toISOString(),
    };

    this._saveUserData();
    return this.userData;
  }
}

/**
 * Class to manage progressive feature disclosure
 */
class FeatureDiscovery {
  constructor(options = {}) {
    this.experienceTracker =
      options.experienceTracker || new ExperienceTracker(options);

    this.featureRegistry = {};
    this.tourRegistry = {};
    this.activeTour = null;

    // Initialize callbacks
    this.callbacks = {
      onFeatureDiscovered: options.onFeatureDiscovered || (() => {}),
      onTourStarted: options.onTourStarted || (() => {}),
      onTourCompleted: options.onTourCompleted || (() => {}),
      onTourStepCompleted: options.onTourStepCompleted || (() => {}),
    };
  }

  /**
   * Register a feature with its discovery parameters
   */
  registerFeature(featureId, options = {}) {
    this.featureRegistry[featureId] = {
      id: featureId,
      name: options.name || featureId,
      description: options.description || '',
      category: options.category || FEATURE_CATEGORIES.ESSENTIAL,
      minExperienceLevel:
        options.minExperienceLevel || EXPERIENCE_LEVELS.BEGINNER,
      discoveryMethod: options.discoveryMethod || 'hint', // hint, tour, notification
      dependsOn: options.dependsOn || [], // features that should be discovered first
      tooltipContent: options.tooltipContent || '',
      element: options.element || null, // DOM element to attach to
      position: options.position || 'auto', // tooltip position
    };

    return this.featureRegistry[featureId];
  }

  /**
   * Check if a feature should be disclosed to the user
   */
  shouldDiscloseFeature(featureId) {
    const feature = this.featureRegistry[featureId];
    if (!feature) {
      return false;
    }

    // Check if user level is sufficient
    const userExp = this.experienceTracker.getUserExperience();
    const userLevelIndex = Object.values(EXPERIENCE_LEVELS).indexOf(
      userExp.level
    );
    const requiredLevelIndex = Object.values(EXPERIENCE_LEVELS).indexOf(
      feature.minExperienceLevel
    );

    if (userLevelIndex < requiredLevelIndex) {
      return false;
    }

    // Check if category should be shown
    if (!this.experienceTracker.shouldShowFeatureCategory(feature.category)) {
      return false;
    }

    // Check dependencies
    for (const dependency of feature.dependsOn) {
      if (!this.experienceTracker.userData.featuresUsed[dependency]) {
        return false;
      }
    }

    return true;
  }

  /**
   * Get features that should be disclosed to user
   * based on their experience level and previously used features
   */
  getDiscoverableFeatures() {
    return Object.keys(this.featureRegistry)
      .filter((featureId) => this.shouldDiscloseFeature(featureId))
      .map((featureId) => this.featureRegistry[featureId]);
  }

  /**
   * Create a feature tour
   */
  registerTour(tourId, options = {}) {
    this.tourRegistry[tourId] = {
      id: tourId,
      name: options.name || tourId,
      description: options.description || '',
      category: options.category || FEATURE_CATEGORIES.ESSENTIAL,
      minExperienceLevel:
        options.minExperienceLevel || EXPERIENCE_LEVELS.BEGINNER,
      steps: options.steps || [],
      completionCallback: options.onComplete || (() => {}),
    };

    return this.tourRegistry[tourId];
  }

  /**
   * Start a feature tour
   */
  startTour(tourId) {
    const tour = this.tourRegistry[tourId];
    if (!tour) {
      console.error(`Tour ${tourId} not found`);
      return false;
    }

    // Check if user experience level is sufficient
    const userExp = this.experienceTracker.getUserExperience();
    const userLevelIndex = Object.values(EXPERIENCE_LEVELS).indexOf(
      userExp.level
    );
    const requiredLevelIndex = Object.values(EXPERIENCE_LEVELS).indexOf(
      tour.minExperienceLevel
    );

    if (userLevelIndex < requiredLevelIndex) {
      console.warn(
        `User level ${userExp.level} insufficient for tour ${tourId}`
      );
      return false;
    }

    this.activeTour = {
      tour: tour,
      currentStep: 0,
      started: new Date().toISOString(),
      completed: false,
    };

    this.callbacks.onTourStarted(tour);
    this._showCurrentTourStep();

    return true;
  }

  /**
   * Show the current step in an active tour
   */
  _showCurrentTourStep() {
    if (!this.activeTour) {
      return;
    }

    const { tour, currentStep } = this.activeTour;
    if (currentStep >= tour.steps.length) {
      this._completeTour();
      return;
    }

    const step = tour.steps[currentStep];
    // Implementation of showing the tour step would go here
    // This would typically involve creating a tooltip or overlay
    // pointing to the relevant UI element

    return step;
  }

  /**
   * Advance to the next step in the active tour
   */
  nextTourStep() {
    if (!this.activeTour) {
      return null;
    }

    const { tour, currentStep } = this.activeTour;
    const completedStep = tour.steps[currentStep];

    this.callbacks.onTourStepCompleted(completedStep, currentStep);

    this.activeTour.currentStep += 1;

    if (this.activeTour.currentStep >= tour.steps.length) {
      return this._completeTour();
    } else {
      return this._showCurrentTourStep();
    }
  }

  /**
   * Complete the active tour
   */
  _completeTour() {
    if (!this.activeTour) {
      return;
    }

    const { tour } = this.activeTour;
    this.activeTour.completed = true;

    // Award experience points for completing the tour
    this.experienceTracker.addPoints(
      ACTION_POINTS.WORKFLOW_COMPLETED,
      `Completed tour ${tour.id}`
    );

    this.callbacks.onTourCompleted(tour);
    tour.completionCallback(tour);

    const result = { ...this.activeTour };
    this.activeTour = null;

    return result;
  }

  /**
   * Create a tooltip for a feature
   */
  showFeatureTooltip(featureId) {
    const feature = this.featureRegistry[featureId];
    if (!feature) {
      console.error(`Feature ${featureId} not found`);
      return null;
    }

    if (!this.shouldDiscloseFeature(featureId)) {
      return null;
    }

    // Implementation of showing the tooltip would go here
    // This would create a tooltip pointing to the feature's UI element

    this.callbacks.onFeatureDiscovered(feature);

    return feature;
  }

  /**
   * Record a feature as been discovered/used
   */
  recordFeatureDiscovered(featureId) {
    const feature = this.featureRegistry[featureId];
    if (!feature) {
      console.error(`Feature ${featureId} not found`);
      return null;
    }

    return this.experienceTracker.recordFeatureUsed(
      featureId,
      feature.category
    );
  }

  /**
   * Get the current active tour information
   */
  getActiveTour() {
    return this.activeTour;
  }

  /**
   * Get the user's current experience information
   */
  getUserExperience() {
    return this.experienceTracker.getUserExperience();
  }
}

// Export the public API
module.exports = {
  FeatureDiscovery,
  ExperienceTracker,
  EXPERIENCE_LEVELS,
  FEATURE_CATEGORIES,
};
