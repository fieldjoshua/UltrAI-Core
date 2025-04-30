/**
 * Achievement System
 *
 * Gamifies feature discovery and user progression through achievements.
 * Provides notifications and rewards for completing tasks and discovering features.
 */

// Default configuration
const DEFAULT_CONFIG = {
  storageKey: 'ultra_achievements',
  notificationsEnabled: true,
  persistAchievements: true,
  achievementCategories: [
    'discovery',
    'mastery',
    'efficiency',
    'collaboration',
    'customization',
  ],
};

// Achievement tiers
const ACHIEVEMENT_TIERS = {
  BRONZE: {
    name: 'BRONZE',
    color: '#cd7f32',
    points: 5,
    icon: '🔶',
  },
  SILVER: {
    name: 'SILVER',
    color: '#c0c0c0',
    points: 10,
    icon: '⬜',
  },
  GOLD: {
    name: 'GOLD',
    color: '#ffd700',
    points: 20,
    icon: '🔸',
  },
  PLATINUM: {
    name: 'PLATINUM',
    color: '#e5e4e2',
    points: 30,
    icon: '⬛',
  },
  DIAMOND: {
    name: 'DIAMOND',
    color: '#b9f2ff',
    points: 50,
    icon: '💎',
  },
};

// Create and initialize the achievement system
function createAchievementSystem(customConfig = {}, experienceTracker = null) {
  // Merge default config with custom config
  const config = { ...DEFAULT_CONFIG, ...customConfig };

  // State management
  let achievements = [];
  let unlockedAchievements = new Set();
  let listeners = [];

  // Load saved achievements if persistence is enabled
  if (config.persistAchievements && typeof window !== 'undefined') {
    try {
      const savedAchievements = localStorage.getItem(config.storageKey);
      if (savedAchievements) {
        unlockedAchievements = new Set(JSON.parse(savedAchievements));
      }
    } catch (error) {
      console.error('Error loading achievement data:', error);
    }
  }

  // Save achievement data
  function saveAchievements() {
    if (config.persistAchievements && typeof window !== 'undefined') {
      try {
        localStorage.setItem(
          config.storageKey,
          JSON.stringify(Array.from(unlockedAchievements))
        );
      } catch (error) {
        console.error('Error saving achievement data:', error);
      }
    }
  }

  // Notify listeners of achievement events
  function notifyListeners(eventType, data) {
    listeners.forEach((listener) => {
      if (!listener.eventType || listener.eventType === eventType) {
        listener.callback({ type: eventType, ...data });
      }
    });
  }

  // Register an achievement definition
  function registerAchievement(achievement) {
    // Ensure achievement has required fields
    if (!achievement.id || !achievement.title || !achievement.description) {
      console.error('Invalid achievement definition:', achievement);
      return false;
    }

    // Check if achievement already registered
    const existingIndex = achievements.findIndex(
      (a) => a.id === achievement.id
    );
    if (existingIndex !== -1) {
      achievements[existingIndex] = { ...achievement };
      return true;
    }

    // Add new achievement
    achievements.push({ ...achievement });

    notifyListeners('ACHIEVEMENT_REGISTERED', { achievement });
    return true;
  }

  // Register multiple achievements at once
  function registerAchievements(achievementList) {
    if (!Array.isArray(achievementList)) {
      console.error('Achievement list must be an array');
      return false;
    }

    let success = true;
    achievementList.forEach((achievement) => {
      if (!registerAchievement(achievement)) {
        success = false;
      }
    });

    return success;
  }

  // Unlock an achievement
  function unlockAchievement(achievementId, additionalData = {}) {
    // Check if already unlocked
    if (unlockedAchievements.has(achievementId)) {
      return false;
    }

    // Find achievement definition
    const achievement = achievements.find((a) => a.id === achievementId);
    if (!achievement) {
      console.warn(`Achievement with id ${achievementId} not found`);
      return false;
    }

    // Mark as unlocked
    unlockedAchievements.add(achievementId);
    saveAchievements();

    // Record experience points if tracker available
    if (experienceTracker) {
      const tier =
        ACHIEVEMENT_TIERS[achievement.tier] || ACHIEVEMENT_TIERS.BRONZE;
      experienceTracker.recordActivity('ACHIEVEMENT_UNLOCKED', {
        achievementId,
        customScore: tier.points,
        ...additionalData,
      });
    }

    // Notify achievement unlocked
    const unlockData = {
      achievement,
      timestamp: new Date().toISOString(),
      ...additionalData,
    };

    notifyListeners('ACHIEVEMENT_UNLOCKED', unlockData);

    return true;
  }

  // Check if an achievement is unlocked
  function isAchievementUnlocked(achievementId) {
    return unlockedAchievements.has(achievementId);
  }

  // Get achievement by ID
  function getAchievement(achievementId) {
    return achievements.find((a) => a.id === achievementId);
  }

  // Get all achievements
  function getAllAchievements() {
    return achievements.map((achievement) => ({
      ...achievement,
      unlocked: unlockedAchievements.has(achievement.id),
    }));
  }

  // Get only unlocked achievements
  function getUnlockedAchievements() {
    return achievements
      .filter((a) => unlockedAchievements.has(a.id))
      .map((achievement) => ({ ...achievement, unlocked: true }));
  }

  // Get progress summary for achievements
  function getProgressSummary() {
    const total = achievements.length;
    const unlocked = unlockedAchievements.size;

    // Calculate category progress
    const categoryProgress = {};
    config.achievementCategories.forEach((category) => {
      const categoryAchievements = achievements.filter(
        (a) => a.category === category
      );
      const unlockedInCategory = categoryAchievements.filter((a) =>
        unlockedAchievements.has(a.id)
      );

      categoryProgress[category] = {
        total: categoryAchievements.length,
        unlocked: unlockedInCategory.length,
        percentage:
          categoryAchievements.length === 0
            ? 0
            : Math.round(
                (unlockedInCategory.length / categoryAchievements.length) * 100
              ),
      };
    });

    // Calculate tier progress
    const tierProgress = {};
    Object.keys(ACHIEVEMENT_TIERS).forEach((tier) => {
      const tierAchievements = achievements.filter((a) => a.tier === tier);
      const unlockedInTier = tierAchievements.filter((a) =>
        unlockedAchievements.has(a.id)
      );

      tierProgress[tier] = {
        total: tierAchievements.length,
        unlocked: unlockedInTier.length,
        percentage:
          tierAchievements.length === 0
            ? 0
            : Math.round(
                (unlockedInTier.length / tierAchievements.length) * 100
              ),
      };
    });

    return {
      total,
      unlocked,
      percentage: total === 0 ? 0 : Math.round((unlocked / total) * 100),
      categoryProgress,
      tierProgress,
    };
  }

  // Get closest achievements to unlock
  function getRecommendedAchievements(limit = 3) {
    // Prioritize achievements based on criteria (category balance, difficulty)
    const locked = achievements.filter((a) => !unlockedAchievements.has(a.id));

    // Simple sorting algorithm - prioritize lower tier achievements first
    const tierValues = {
      BRONZE: 1,
      SILVER: 2,
      GOLD: 3,
      PLATINUM: 4,
      DIAMOND: 5,
    };

    // Sort by tier and then by category with fewer unlocks
    const progressSummary = getProgressSummary();
    locked.sort((a, b) => {
      // First sort by tier
      const tierDiff = (tierValues[a.tier] || 99) - (tierValues[b.tier] || 99);
      if (tierDiff !== 0) return tierDiff;

      // Then sort by category progress (prefer categories with lower completion)
      const catA = progressSummary.categoryProgress[a.category];
      const catB = progressSummary.categoryProgress[b.category];

      if (catA && catB) {
        return catA.percentage - catB.percentage;
      }

      return 0;
    });

    return locked.slice(0, limit);
  }

  // Subscribe to achievement events
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

  // Reset all achievements (mainly for testing)
  function resetAchievements() {
    unlockedAchievements = new Set();
    saveAchievements();

    notifyListeners('ACHIEVEMENTS_RESET', {});
  }

  // Integration with experience tracker if provided
  if (experienceTracker) {
    // Listen for level ups to grant level-based achievements
    experienceTracker.subscribe((event) => {
      if (event.type === 'LEVEL_UP') {
        // Check for level-based achievements
        const levelAchievements = achievements.filter(
          (a) =>
            a.triggerType === 'LEVEL_UP' && a.triggerLevel === event.newLevel
        );

        levelAchievements.forEach((achievement) => {
          unlockAchievement(achievement.id, {
            level: event.newLevel,
            previousLevel: event.previousLevel,
          });
        });
      }

      if (event.type === 'FEATURE_DISCOVERED') {
        // Check for feature discovery achievements
        const discoveryAchievements = achievements.filter(
          (a) =>
            a.triggerType === 'FEATURE_DISCOVERED' &&
            a.featureId === event.featureId
        );

        discoveryAchievements.forEach((achievement) => {
          unlockAchievement(achievement.id, { featureId: event.featureId });
        });
      }
    });
  }

  // Initialize with default achievement definitions
  // These can be extended or replaced by the application
  const defaultAchievements = [
    {
      id: 'first_session',
      title: 'SYSTEM INITIALIZED',
      description: 'Complete your first session with UltraAI',
      tier: 'BRONZE',
      category: 'discovery',
      triggerType: 'SESSION_COMPLETED',
      icon: '🔌',
    },
    {
      id: 'power_user',
      title: 'POWER USER',
      description: 'Reach intermediate experience level',
      tier: 'SILVER',
      category: 'mastery',
      triggerType: 'LEVEL_UP',
      triggerLevel: 'intermediate',
      icon: '⚡',
    },
    {
      id: 'advanced_user',
      title: 'NEURAL NETWORK EXPERT',
      description: 'Reach advanced experience level',
      tier: 'GOLD',
      category: 'mastery',
      triggerType: 'LEVEL_UP',
      triggerLevel: 'advanced',
      icon: '🧠',
    },
    {
      id: 'shortcuts_master',
      title: 'SHORTCUTS MASTER',
      description: 'Use 10 different keyboard shortcuts',
      tier: 'SILVER',
      category: 'efficiency',
      triggerType: 'CUSTOM',
      icon: '⌨️',
    },
    {
      id: 'customization_guru',
      title: 'CUSTOMIZATION GURU',
      description: 'Customize 5 different system settings',
      tier: 'BRONZE',
      category: 'customization',
      triggerType: 'CUSTOM',
      icon: '🎨',
    },
  ];

  registerAchievements(defaultAchievements);

  // Public API
  return {
    registerAchievement,
    registerAchievements,
    unlockAchievement,
    isAchievementUnlocked,
    getAchievement,
    getAllAchievements,
    getUnlockedAchievements,
    getProgressSummary,
    getRecommendedAchievements,
    subscribe,
    resetAchievements,
    ACHIEVEMENT_TIERS,
  };
}

export { createAchievementSystem, ACHIEVEMENT_TIERS };
