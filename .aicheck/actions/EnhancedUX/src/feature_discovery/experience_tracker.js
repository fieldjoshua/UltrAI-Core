/**
 * Experience Tracker
 *
 * Tracks user experience levels and progression through the system.
 * Manages feature discovery and unlocks based on activity and engagement.
 */

// Default configuration
const DEFAULT_CONFIG = {
  storageKey: 'ultra_user_experience',
  initialLevel: 'beginner',
  levels: ['beginner', 'intermediate', 'advanced', 'expert'],
  thresholds: {
    intermediate: 50,
    advanced: 100,
    expert: 200,
  },
  trackingEnabled: true,
  persistExperience: true,
};

// Base score for different actions
const ACTION_SCORES = {
  FEATURE_USED: 5, // User used a feature
  COMPLEX_TASK: 10, // User completed a complex task
  HELP_VIEWED: 1, // User viewed help content
  SETTINGS_CHANGED: 2, // User changed settings
  GUIDE_COMPLETED: 15, // User completed a guide
  SHORTCUT_USED: 3, // User used a keyboard shortcut
  FEATURE_DISCOVERED: 8, // User discovered a feature
  SESSION_COMPLETED: 5, // User completed a session
  ADVANCED_FEATURE_USED: 12, // User used an advanced feature
  FEEDBACK_PROVIDED: 7, // User provided feedback
};

// Create and initialize the experience tracker
function createExperienceTracker(customConfig = {}) {
  // Merge default config with custom config
  const config = { ...DEFAULT_CONFIG, ...customConfig };

  // State management
  let totalScore = 0;
  let currentLevel = config.initialLevel;
  let discoveredFeatures = new Set();
  let activityHistory = [];
  let listeners = [];

  // Load saved experience if persistence is enabled
  if (config.persistExperience && typeof window !== 'undefined') {
    try {
      const savedExperience = localStorage.getItem(config.storageKey);
      if (savedExperience) {
        const parsed = JSON.parse(savedExperience);
        totalScore = parsed.totalScore || 0;
        currentLevel = parsed.currentLevel || config.initialLevel;
        discoveredFeatures = new Set(parsed.discoveredFeatures || []);
        activityHistory = parsed.activityHistory || [];
      }
    } catch (error) {
      console.error('Error loading experience data:', error);
    }
  }

  // Calculate level based on score
  function calculateLevel(score) {
    for (let i = config.levels.length - 1; i > 0; i--) {
      const level = config.levels[i];
      if (score >= config.thresholds[level]) {
        return level;
      }
    }
    return config.levels[0]; // Default to first level
  }

  // Save experience data
  function saveExperience() {
    if (config.persistExperience && typeof window !== 'undefined') {
      try {
        localStorage.setItem(
          config.storageKey,
          JSON.stringify({
            totalScore,
            currentLevel,
            discoveredFeatures: Array.from(discoveredFeatures),
            activityHistory,
          })
        );
      } catch (error) {
        console.error('Error saving experience data:', error);
      }
    }
  }

  // Notify listeners of experience changes
  function notifyListeners(eventType, data) {
    listeners.forEach((listener) => {
      if (!listener.eventType || listener.eventType === eventType) {
        listener.callback({ type: eventType, ...data });
      }
    });
  }

  // Check if level up occurred and notify if it did
  function checkLevelUp(previousLevel, newLevel) {
    if (previousLevel !== newLevel) {
      notifyListeners('LEVEL_UP', {
        previousLevel,
        newLevel,
        score: totalScore,
      });
      return true;
    }
    return false;
  }

  // Record user activity and update experience
  function recordActivity(actionType, details = {}) {
    if (!config.trackingEnabled) return;

    // Ensure action type is valid
    const score = ACTION_SCORES[actionType] || 0;
    if (score === 0 && !details.customScore) {
      console.warn(`Unknown action type: ${actionType}`);
      return;
    }

    // Calculate score to add
    const previousLevel = currentLevel;
    const pointsToAdd = details.customScore || score;

    // Update totals
    totalScore += pointsToAdd;

    // Record activity
    const timestamp = new Date().toISOString();
    const activity = {
      actionType,
      timestamp,
      score: pointsToAdd,
      details: { ...details },
    };

    activityHistory.push(activity);

    // Trim history if it gets too large
    if (activityHistory.length > 100) {
      activityHistory = activityHistory.slice(-100);
    }

    // Update level
    const newLevel = calculateLevel(totalScore);
    currentLevel = newLevel;

    // Check for level up
    const leveledUp = checkLevelUp(previousLevel, newLevel);

    // Save updated experience
    saveExperience();

    // Notify listeners of activity
    notifyListeners('ACTIVITY_RECORDED', {
      activity,
      newScore: totalScore,
      currentLevel: newLevel,
      leveledUp,
    });

    return {
      score: totalScore,
      level: newLevel,
      leveledUp,
    };
  }

  // Register a feature as discovered
  function discoverFeature(featureId, requiredLevel) {
    if (discoveredFeatures.has(featureId)) {
      return false;
    }

    discoveredFeatures.add(featureId);
    saveExperience();

    // Record the discovery with bonus points if it's an advanced feature
    const isAdvancedFeature = requiredLevel && requiredLevel !== 'beginner';
    recordActivity(
      isAdvancedFeature ? 'ADVANCED_FEATURE_USED' : 'FEATURE_DISCOVERED',
      { featureId, requiredLevel }
    );

    notifyListeners('FEATURE_DISCOVERED', {
      featureId,
      requiredLevel,
      totalDiscovered: discoveredFeatures.size,
    });

    return true;
  }

  // Check if a feature has been discovered
  function hasDiscoveredFeature(featureId) {
    return discoveredFeatures.has(featureId);
  }

  // Subscribe to experience events
  function subscribe(callback, eventType = null) {
    const listener = { callback, eventType };
    listeners.push(listener);

    // Return unsubscribe function
    return () => {
      const index = listeners.indexOf(listener);
      if (index !== -1) {
        listeners.splice(index, 1);
      }
    };
  }

  // Reset experience data (mainly for testing)
  function resetExperience() {
    totalScore = 0;
    currentLevel = config.initialLevel;
    discoveredFeatures = new Set();
    activityHistory = [];
    saveExperience();

    notifyListeners('EXPERIENCE_RESET', {
      newLevel: currentLevel,
      score: totalScore,
    });
  }

  // Get experience summary
  function getExperienceSummary() {
    return {
      level: currentLevel,
      score: totalScore,
      discoveredFeatures: Array.from(discoveredFeatures),
      nextLevel: getNextLevel(),
      progress: getProgressToNextLevel(),
    };
  }

  // Get the next level information
  function getNextLevel() {
    const currentLevelIndex = config.levels.indexOf(currentLevel);
    if (currentLevelIndex >= config.levels.length - 1) {
      return null; // Already at max level
    }

    const nextLevel = config.levels[currentLevelIndex + 1];
    const threshold = config.thresholds[nextLevel];

    return {
      name: nextLevel,
      pointsNeeded: threshold - totalScore,
      threshold,
    };
  }

  // Get progress percentage to next level
  function getProgressToNextLevel() {
    const nextLevel = getNextLevel();
    if (!nextLevel) {
      return 100; // Already at max level
    }

    const currentLevelIndex = config.levels.indexOf(currentLevel);
    const currentThreshold =
      currentLevelIndex === 0 ? 0 : config.thresholds[currentLevel];
    const pointsInCurrentLevel = totalScore - currentThreshold;
    const pointsRequiredForNextLevel = nextLevel.threshold - currentThreshold;

    return Math.min(
      100,
      Math.round((pointsInCurrentLevel / pointsRequiredForNextLevel) * 100)
    );
  }

  // Public API
  return {
    recordActivity,
    discoverFeature,
    hasDiscoveredFeature,
    subscribe,
    resetExperience,
    getExperienceSummary,
    getLevel: () => currentLevel,
    getScore: () => totalScore,
    getDiscoveredFeatures: () => Array.from(discoveredFeatures),
    getNextLevel,
    getProgressToNextLevel,
    getHistory: () => [...activityHistory],
    ACTION_SCORES,
  };
}

export { createExperienceTracker, ACTION_SCORES };
