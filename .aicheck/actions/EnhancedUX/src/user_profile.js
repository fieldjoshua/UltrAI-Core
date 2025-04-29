/**
 * User Profile
 *
 * Manages user preferences, feature usage history, and experience level tracking
 * as part of the Context Analyzer system.
 */

class UserProfile {
  constructor(options = {}) {
    // Default user profile structure
    this.profile = {
      userId: options.userId || this._generateUserId(),
      created: new Date(),
      lastUpdated: new Date(),
      experienceLevel: options.experienceLevel || 'novice', // novice, intermediate, advanced, expert
      featureUsage: {},
      preferences: {
        theme: options.theme || 'neonNight',
        animationLevel: options.animationLevel || 'medium', // none, low, medium, high
        suggestionFrequency: options.suggestionFrequency || 'medium', // none, low, medium, high
        privacySettings: {
          trackActivity: true,
          storePreferences: true,
          syncWithCloud: false,
        },
      },
      recentActivity: [],
      stats: {
        totalSessions: 0,
        totalFeatureUses: 0,
        totalTimeSpent: 0,
        lastSessionDate: null,
      },
    };

    // Storage configuration
    this.storageConfig = {
      useLocalStorage: options.useLocalStorage !== false,
      useIndexedDB: options.useIndexedDB !== false,
      dbName: options.dbName || 'ultraAI_userProfile',
      dbVersion: options.dbVersion || 1,
      storeName: options.storeName || 'userProfiles',
      syncWithCloud: options.syncWithCloud || false,
    };

    // IndexedDB connection
    this.db = null;

    // Initialize storage
    if (this.storageConfig.useIndexedDB) {
      this._initIndexedDB();
    }

    // Load existing profile if available
    this._loadProfile();
  }

  /**
   * Get current user experience level
   * @returns {string} Experience level (novice, intermediate, advanced, expert)
   */
  getExperienceLevel() {
    return this.profile.experienceLevel;
  }

  /**
   * Update user experience level
   * @param {string} level New experience level
   */
  setExperienceLevel(level) {
    const validLevels = ['novice', 'intermediate', 'advanced', 'expert'];

    if (!validLevels.includes(level)) {
      throw new Error(
        `Invalid experience level: ${level}. Must be one of: ${validLevels.join(
          ', '
        )}`
      );
    }

    this.profile.experienceLevel = level;
    this.profile.lastUpdated = new Date();

    this._saveProfile();
    return this;
  }

  /**
   * Auto-calculate experience level based on feature usage
   * @returns {string} Calculated experience level
   */
  calculateExperienceLevel() {
    const { totalSessions, totalFeatureUses } = this.profile.stats;
    const featureCount = Object.keys(this.profile.featureUsage).length;
    const advancedFeatureCount = Object.values(
      this.profile.featureUsage
    ).filter((f) => f.proficiency === 'advanced').length;

    // Simple heuristic, can be refined
    if (totalSessions > 50 && featureCount > 15 && advancedFeatureCount > 5) {
      this.profile.experienceLevel = 'expert';
    } else if (
      totalSessions > 20 &&
      featureCount > 10 &&
      advancedFeatureCount > 2
    ) {
      this.profile.experienceLevel = 'advanced';
    } else if (totalSessions > 5 && featureCount > 5) {
      this.profile.experienceLevel = 'intermediate';
    } else {
      this.profile.experienceLevel = 'novice';
    }

    this.profile.lastUpdated = new Date();
    this._saveProfile();

    return this.profile.experienceLevel;
  }

  /**
   * Get user preferences
   * @returns {Object} User preferences
   */
  getPreferences() {
    return { ...this.profile.preferences };
  }

  /**
   * Update user preferences
   * @param {Object} preferences New preference values
   */
  updatePreferences(preferences) {
    this.profile.preferences = {
      ...this.profile.preferences,
      ...preferences,
    };

    this.profile.lastUpdated = new Date();
    this._saveProfile();

    return this;
  }

  /**
   * Record usage of a feature
   * @param {string} featureName Name of the feature
   * @param {Object} usageData Additional data about usage
   */
  recordFeatureUsage(featureName, usageData = {}) {
    const now = new Date();

    // Initialize feature if not exists
    if (!this.profile.featureUsage[featureName]) {
      this.profile.featureUsage[featureName] = {
        usageCount: 0,
        firstUsed: now,
        lastUsed: now,
        proficiency: 'beginner', // beginner, intermediate, advanced
        usageHistory: [],
      };
    }

    // Update feature stats
    const feature = this.profile.featureUsage[featureName];
    feature.usageCount++;
    feature.lastUsed = now;

    // Add to usage history (limited to last 10)
    feature.usageHistory.push({
      timestamp: now,
      ...usageData,
    });

    if (feature.usageHistory.length > 10) {
      feature.usageHistory = feature.usageHistory.slice(-10);
    }

    // Update proficiency based on usage count
    // This is a simple heuristic that could be refined
    if (feature.usageCount > 20) {
      feature.proficiency = 'advanced';
    } else if (feature.usageCount > 5) {
      feature.proficiency = 'intermediate';
    } else {
      feature.proficiency = 'beginner';
    }

    // Update global stats
    this.profile.stats.totalFeatureUses++;

    // Add to recent activity
    this._addRecentActivity('feature', {
      feature: featureName,
      ...usageData,
    });

    this.profile.lastUpdated = now;
    this._saveProfile();

    return this;
  }

  /**
   * Get usage data for a specific feature
   * @param {string} featureName Feature name
   * @returns {Object|null} Feature usage data or null if not used
   */
  getFeatureUsage(featureName) {
    return this.profile.featureUsage[featureName]
      ? { ...this.profile.featureUsage[featureName] }
      : null;
  }

  /**
   * Get all feature usage data
   * @returns {Object} Map of feature usage data
   */
  getAllFeatureUsage() {
    return { ...this.profile.featureUsage };
  }

  /**
   * Get most used features
   * @param {number} limit Number of features to return
   * @returns {Array} Sorted array of [featureName, usageData]
   */
  getMostUsedFeatures(limit = 5) {
    return Object.entries(this.profile.featureUsage)
      .sort((a, b) => b[1].usageCount - a[1].usageCount)
      .slice(0, limit);
  }

  /**
   * Record a new user session
   * @param {Object} sessionData Optional session metadata
   */
  recordSession(sessionData = {}) {
    const now = new Date();

    this.profile.stats.totalSessions++;
    this.profile.stats.lastSessionDate = now;

    this._addRecentActivity('session', {
      action: 'start',
      timestamp: now,
      ...sessionData,
    });

    this.profile.lastUpdated = now;
    this._saveProfile();

    return this;
  }

  /**
   * Get recent user activity
   * @param {number} limit Number of recent activities to retrieve
   * @returns {Array} Recent activities
   */
  getRecentActivity(limit = 10) {
    return this.profile.recentActivity.slice(-limit);
  }

  /**
   * Reset user profile (for testing or user request)
   * @param {boolean} preserveUserId Whether to keep the userId
   */
  resetProfile(preserveUserId = true) {
    const userId = this.profile.userId;

    this.profile = {
      userId: preserveUserId ? userId : this._generateUserId(),
      created: new Date(),
      lastUpdated: new Date(),
      experienceLevel: 'novice',
      featureUsage: {},
      preferences: {
        theme: 'neonNight',
        animationLevel: 'medium',
        suggestionFrequency: 'medium',
        privacySettings: {
          trackActivity: true,
          storePreferences: true,
          syncWithCloud: false,
        },
      },
      recentActivity: [],
      stats: {
        totalSessions: 0,
        totalFeatureUses: 0,
        totalTimeSpent: 0,
        lastSessionDate: null,
      },
    };

    this._saveProfile();
    return this;
  }

  /**
   * Export user profile as JSON
   * @returns {Object} User profile data
   */
  exportProfile() {
    return JSON.parse(JSON.stringify(this.profile));
  }

  /**
   * Import user profile from JSON
   * @param {Object} profileData Profile data to import
   */
  importProfile(profileData) {
    // Validate required structure
    if (!profileData || !profileData.userId || !profileData.experienceLevel) {
      throw new Error('Invalid profile data structure');
    }

    this.profile = {
      ...profileData,
      lastUpdated: new Date(),
    };

    this._saveProfile();
    return this;
  }

  // Private methods

  /**
   * Generate a unique user ID
   * @private
   */
  _generateUserId() {
    return (
      'user_' +
      Math.random().toString(36).substring(2, 15) +
      Math.random().toString(36).substring(2, 15)
    );
  }

  /**
   * Add an activity to recent activity list
   * @private
   */
  _addRecentActivity(type, data) {
    const activity = {
      type,
      timestamp: new Date(),
      ...data,
    };

    this.profile.recentActivity.push(activity);

    // Keep only the last 50 activities
    if (this.profile.recentActivity.length > 50) {
      this.profile.recentActivity = this.profile.recentActivity.slice(-50);
    }
  }

  /**
   * Initialize IndexedDB for profile storage
   * @private
   */
  _initIndexedDB() {
    if (!window.indexedDB) {
      console.warn('IndexedDB not supported, falling back to localStorage');
      return;
    }

    const request = indexedDB.open(
      this.storageConfig.dbName,
      this.storageConfig.dbVersion
    );

    request.onerror = (event) => {
      console.error('IndexedDB error:', event.target.error);
    };

    request.onupgradeneeded = (event) => {
      const db = event.target.result;

      // Create object store for user profiles if it doesn't exist
      if (!db.objectStoreNames.contains(this.storageConfig.storeName)) {
        const store = db.createObjectStore(this.storageConfig.storeName, {
          keyPath: 'userId',
        });
        store.createIndex('userId', 'userId', { unique: true });
      }
    };

    request.onsuccess = (event) => {
      this.db = event.target.result;

      // Try to load existing profile now that DB is ready
      this._loadFromIndexedDB();
    };
  }

  /**
   * Save profile to storage
   * @private
   */
  _saveProfile() {
    // Don't save if user opted out
    if (!this.profile.preferences.privacySettings.storePreferences) {
      return;
    }

    if (this.storageConfig.useLocalStorage) {
      this._saveToLocalStorage();
    }

    if (this.storageConfig.useIndexedDB && this.db) {
      this._saveToIndexedDB();
    }

    if (
      this.storageConfig.syncWithCloud &&
      this.profile.preferences.privacySettings.syncWithCloud
    ) {
      this._syncWithCloud();
    }
  }

  /**
   * Load profile from storage
   * @private
   */
  _loadProfile() {
    let profileLoaded = false;

    // Try IndexedDB first (better for large data)
    if (this.storageConfig.useIndexedDB && window.indexedDB) {
      // If DB is already connected, load immediately
      if (this.db) {
        profileLoaded = this._loadFromIndexedDB();
      }
      // Otherwise it will be loaded when DB connection is established
    }

    // Fall back to localStorage if needed
    if (!profileLoaded && this.storageConfig.useLocalStorage) {
      profileLoaded = this._loadFromLocalStorage();
    }

    // If nothing was loaded, this is a new user
    if (!profileLoaded) {
      // Record this as the first session
      this.recordSession({ isFirstSession: true });
    }
  }

  /**
   * Save profile to localStorage
   * @private
   */
  _saveToLocalStorage() {
    try {
      localStorage.setItem(
        `ultraAI_profile_${this.profile.userId}`,
        JSON.stringify(this.profile)
      );
      return true;
    } catch (e) {
      console.error('Error saving to localStorage:', e);
      return false;
    }
  }

  /**
   * Load profile from localStorage
   * @private
   */
  _loadFromLocalStorage() {
    try {
      // Try to load existing user ID
      const storedUserId = localStorage.getItem('ultraAI_currentUserId');

      if (storedUserId) {
        const storedProfile = localStorage.getItem(
          `ultraAI_profile_${storedUserId}`
        );

        if (storedProfile) {
          this.profile = JSON.parse(storedProfile);
          return true;
        }
      }

      // If no existing profile, save the current user ID for next time
      localStorage.setItem('ultraAI_currentUserId', this.profile.userId);
      return false;
    } catch (e) {
      console.error('Error loading from localStorage:', e);
      return false;
    }
  }

  /**
   * Save profile to IndexedDB
   * @private
   */
  _saveToIndexedDB() {
    if (!this.db) return false;

    try {
      const transaction = this.db.transaction(
        [this.storageConfig.storeName],
        'readwrite'
      );
      const store = transaction.objectStore(this.storageConfig.storeName);

      store.put(this.profile);

      transaction.oncomplete = () => {
        // Success, but we don't need to do anything
      };

      transaction.onerror = (event) => {
        console.error('Error saving to IndexedDB:', event.target.error);
      };

      return true;
    } catch (e) {
      console.error('Error in IndexedDB transaction:', e);
      return false;
    }
  }

  /**
   * Load profile from IndexedDB
   * @private
   */
  _loadFromIndexedDB() {
    if (!this.db) return false;

    try {
      const transaction = this.db.transaction(
        [this.storageConfig.storeName],
        'readonly'
      );
      const store = transaction.objectStore(this.storageConfig.storeName);
      const request = store.get(this.profile.userId);

      request.onsuccess = (event) => {
        if (event.target.result) {
          this.profile = event.target.result;
          return true;
        }
        return false;
      };

      request.onerror = (event) => {
        console.error('Error loading from IndexedDB:', event.target.error);
        return false;
      };
    } catch (e) {
      console.error('Error in IndexedDB transaction:', e);
      return false;
    }
  }

  /**
   * Sync profile with cloud service
   * @private
   */
  _syncWithCloud() {
    // This would be implemented based on the specific cloud service integration
    console.log('Cloud sync not yet implemented');
  }
}

// Export the UserProfile class
export default UserProfile;
