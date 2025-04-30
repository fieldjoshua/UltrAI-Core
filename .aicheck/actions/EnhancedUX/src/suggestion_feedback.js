/**
 * UltraAI Suggestion Feedback System
 *
 * This module collects and analyzes user feedback on suggestions
 * to improve future suggestion relevance and timing.
 */

/**
 * Types of feedback a user can provide on a suggestion
 */
const FEEDBACK_TYPES = {
  ACCEPTED: 'accepted', // User acted on the suggestion
  DISMISSED: 'dismissed', // User explicitly dismissed the suggestion
  IGNORED: 'ignored', // User did not interact with the suggestion
  HELPFUL: 'helpful', // User marked the suggestion as helpful
  NOT_HELPFUL: 'not_helpful', // User marked the suggestion as not helpful
};

/**
 * Manages feedback collection and storage
 */
class SuggestionFeedback {
  constructor(options = {}) {
    this.storageKey = options.storageKey || 'ultra_suggestion_feedback';
    this.maxStorageItems = options.maxStorageItems || 100;
    this.feedbackData = this._loadFeedbackData();
    this.analyticsEnabled = options.analyticsEnabled !== false;
    this.feedbackCallback = options.feedbackCallback || null;
  }

  /**
   * Record user feedback for a suggestion
   * @param {String} suggestionId ID of the suggestion
   * @param {String} feedbackType Type of feedback (from FEEDBACK_TYPES)
   * @param {Object} additionalData Any additional data to store with feedback
   * @returns {Object} The recorded feedback entry
   */
  recordFeedback(suggestionId, feedbackType, additionalData = {}) {
    if (!Object.values(FEEDBACK_TYPES).includes(feedbackType)) {
      throw new Error(`Invalid feedback type: ${feedbackType}`);
    }

    const timestamp = new Date().toISOString();
    const feedbackEntry = {
      suggestionId,
      feedbackType,
      timestamp,
      ...additionalData,
    };

    // Add to in-memory storage
    if (!this.feedbackData[suggestionId]) {
      this.feedbackData[suggestionId] = [];
    }
    this.feedbackData[suggestionId].push(feedbackEntry);

    // Persist the feedback
    this._saveFeedbackData();

    // Send to analytics if enabled
    if (this.analyticsEnabled) {
      this._sendAnalytics(feedbackEntry);
    }

    // Call feedback callback if provided
    if (this.feedbackCallback) {
      this.feedbackCallback(feedbackEntry);
    }

    return feedbackEntry;
  }

  /**
   * Record that a suggestion was accepted
   * @param {String} suggestionId ID of the suggestion
   * @param {Object} actionData Data about the action taken
   */
  recordAccepted(suggestionId, actionData = {}) {
    return this.recordFeedback(suggestionId, FEEDBACK_TYPES.ACCEPTED, {
      actionData,
    });
  }

  /**
   * Record that a suggestion was dismissed
   * @param {String} suggestionId ID of the suggestion
   * @param {Object} dismissData Data about the dismissal
   */
  recordDismissed(suggestionId, dismissData = {}) {
    return this.recordFeedback(suggestionId, FEEDBACK_TYPES.DISMISSED, {
      dismissData,
    });
  }

  /**
   * Record that a suggestion was helpful
   * @param {String} suggestionId ID of the suggestion
   * @param {Number} rating Optional rating value (1-5)
   */
  recordHelpful(suggestionId, rating) {
    return this.recordFeedback(suggestionId, FEEDBACK_TYPES.HELPFUL, {
      rating,
    });
  }

  /**
   * Record that a suggestion was not helpful
   * @param {String} suggestionId ID of the suggestion
   * @param {String} reason Optional reason why it wasn't helpful
   */
  recordNotHelpful(suggestionId, reason) {
    return this.recordFeedback(suggestionId, FEEDBACK_TYPES.NOT_HELPFUL, {
      reason,
    });
  }

  /**
   * Get all feedback for a specific suggestion
   * @param {String} suggestionId ID of the suggestion
   * @returns {Array} Array of feedback entries
   */
  getFeedbackForSuggestion(suggestionId) {
    return this.feedbackData[suggestionId] || [];
  }

  /**
   * Get all feedback of a specific type
   * @param {String} feedbackType Type of feedback
   * @returns {Array} Array of feedback entries
   */
  getFeedbackByType(feedbackType) {
    if (!Object.values(FEEDBACK_TYPES).includes(feedbackType)) {
      throw new Error(`Invalid feedback type: ${feedbackType}`);
    }

    const result = [];
    Object.values(this.feedbackData).forEach((entries) => {
      entries
        .filter((entry) => entry.feedbackType === feedbackType)
        .forEach((entry) => result.push(entry));
    });

    return result;
  }

  /**
   * Get feedback statistics for analysis
   * @returns {Object} Statistics about collected feedback
   */
  getStatistics() {
    const stats = {
      totalSuggestions: Object.keys(this.feedbackData).length,
      totalFeedbackEntries: 0,
      byType: {},
    };

    // Initialize counts for each feedback type
    Object.values(FEEDBACK_TYPES).forEach((type) => {
      stats.byType[type] = 0;
    });

    // Count feedback entries
    Object.values(this.feedbackData).forEach((entries) => {
      stats.totalFeedbackEntries += entries.length;

      // Count by type
      entries.forEach((entry) => {
        stats.byType[entry.feedbackType]++;
      });
    });

    // Calculate acceptance rate
    const acceptedCount = stats.byType[FEEDBACK_TYPES.ACCEPTED] || 0;
    const dismissedCount = stats.byType[FEEDBACK_TYPES.DISMISSED] || 0;
    const ignoredCount = stats.byType[FEEDBACK_TYPES.IGNORED] || 0;

    const totalInteractions = acceptedCount + dismissedCount + ignoredCount;
    stats.acceptanceRate =
      totalInteractions > 0 ? acceptedCount / totalInteractions : 0;

    return stats;
  }

  /**
   * Clear all feedback data
   */
  clearAllFeedback() {
    this.feedbackData = {};
    this._saveFeedbackData();
  }

  /**
   * Load feedback data from storage
   * @private
   */
  _loadFeedbackData() {
    try {
      if (typeof localStorage !== 'undefined') {
        const storedData = localStorage.getItem(this.storageKey);
        return storedData ? JSON.parse(storedData) : {};
      }
      return {};
    } catch (error) {
      console.warn('Failed to load suggestion feedback data:', error);
      return {};
    }
  }

  /**
   * Save feedback data to storage
   * @private
   */
  _saveFeedbackData() {
    try {
      if (typeof localStorage !== 'undefined') {
        // Enforce size limits by removing oldest feedback if needed
        this._enforceSizeLimit();
        localStorage.setItem(
          this.storageKey,
          JSON.stringify(this.feedbackData)
        );
      }
    } catch (error) {
      console.warn('Failed to save suggestion feedback data:', error);
    }
  }

  /**
   * Send feedback data to analytics
   * @param {Object} feedbackEntry The feedback entry to send
   * @private
   */
  _sendAnalytics(feedbackEntry) {
    // This would integrate with an analytics system
    // Implementation depends on the analytics platform used
    if (typeof window !== 'undefined' && window.analyticsTracker) {
      window.analyticsTracker.trackEvent('suggestion_feedback', {
        suggestionId: feedbackEntry.suggestionId,
        feedbackType: feedbackEntry.feedbackType,
        timestamp: feedbackEntry.timestamp,
      });
    }
  }

  /**
   * Enforce storage size limits by removing oldest feedback
   * @private
   */
  _enforceSizeLimit() {
    let totalEntries = 0;

    // Count total entries
    Object.values(this.feedbackData).forEach((entries) => {
      totalEntries += entries.length;
    });

    if (totalEntries <= this.maxStorageItems) {
      return;
    }

    // Need to remove oldest entries
    const entriesToRemove = totalEntries - this.maxStorageItems;

    // Flatten all entries with their suggestion IDs
    let allEntries = [];
    Object.entries(this.feedbackData).forEach(([suggestionId, entries]) => {
      entries.forEach((entry) => {
        allEntries.push({
          suggestionId,
          entry,
          timestamp: new Date(entry.timestamp).getTime(),
        });
      });
    });

    // Sort by timestamp (oldest first)
    allEntries.sort((a, b) => a.timestamp - b.timestamp);

    // Remove oldest entries
    const entriesForRemoval = allEntries.slice(0, entriesToRemove);
    entriesForRemoval.forEach((item) => {
      const entries = this.feedbackData[item.suggestionId];
      const index = entries.findIndex(
        (e) => e.timestamp === item.entry.timestamp
      );
      if (index >= 0) {
        entries.splice(index, 1);
      }

      // Remove empty suggestion arrays
      if (entries.length === 0) {
        delete this.feedbackData[item.suggestionId];
      }
    });
  }
}

/**
 * Feedback analyzer for improving suggestion quality
 */
class FeedbackAnalyzer {
  constructor(suggestionFeedback) {
    this.suggestionFeedback = suggestionFeedback;
  }

  /**
   * Analyze suggestion performance to suggest rule adjustments
   * @returns {Object} Analysis results with recommendations
   */
  analyzePerformance() {
    const stats = this.suggestionFeedback.getStatistics();
    const acceptedFeedback = this.suggestionFeedback.getFeedbackByType(
      FEEDBACK_TYPES.ACCEPTED
    );
    const dismissedFeedback = this.suggestionFeedback.getFeedbackByType(
      FEEDBACK_TYPES.DISMISSED
    );

    // Group by rule ID
    const rulePerformance = {};
    this._processPerformanceByRule(
      acceptedFeedback,
      dismissedFeedback,
      rulePerformance
    );

    return {
      overallStats: stats,
      rulePerformance,
      recommendations: this._generateRecommendations(rulePerformance, stats),
    };
  }

  /**
   * Process feedback to determine performance by rule
   * @param {Array} acceptedFeedback Accepted suggestions
   * @param {Array} dismissedFeedback Dismissed suggestions
   * @param {Object} rulePerformance Output parameter for rule performance
   * @private
   */
  _processPerformanceByRule(
    acceptedFeedback,
    dismissedFeedback,
    rulePerformance
  ) {
    // Process accepted suggestions
    acceptedFeedback.forEach((feedback) => {
      const ruleId = feedback.ruleId;
      if (!ruleId) return;

      if (!rulePerformance[ruleId]) {
        rulePerformance[ruleId] = { accepted: 0, dismissed: 0, total: 0 };
      }

      rulePerformance[ruleId].accepted++;
      rulePerformance[ruleId].total++;
    });

    // Process dismissed suggestions
    dismissedFeedback.forEach((feedback) => {
      const ruleId = feedback.ruleId;
      if (!ruleId) return;

      if (!rulePerformance[ruleId]) {
        rulePerformance[ruleId] = { accepted: 0, dismissed: 0, total: 0 };
      }

      rulePerformance[ruleId].dismissed++;
      rulePerformance[ruleId].total++;
    });

    // Calculate acceptance rate for each rule
    Object.values(rulePerformance).forEach((ruleStat) => {
      ruleStat.acceptanceRate =
        ruleStat.total > 0 ? ruleStat.accepted / ruleStat.total : 0;
    });
  }

  /**
   * Generate recommendations based on performance analysis
   * @param {Object} rulePerformance Performance metrics by rule
   * @param {Object} stats Overall statistics
   * @returns {Array} Recommendations for improving suggestion quality
   * @private
   */
  _generateRecommendations(rulePerformance, stats) {
    const recommendations = [];
    const LOW_ACCEPTANCE_THRESHOLD = 0.2; // 20% acceptance rate
    const HIGH_ACCEPTANCE_THRESHOLD = 0.8; // 80% acceptance rate

    // Check for low-performing rules
    Object.entries(rulePerformance).forEach(([ruleId, performance]) => {
      if (performance.total < 5) {
        // Not enough data for this rule
        return;
      }

      if (performance.acceptanceRate < LOW_ACCEPTANCE_THRESHOLD) {
        recommendations.push({
          type: 'rule_adjustment',
          ruleId,
          severity: 'high',
          recommendation:
            'Consider adjusting rule conditions or reducing priority as it has low acceptance',
          metrics: performance,
        });
      } else if (performance.acceptanceRate > HIGH_ACCEPTANCE_THRESHOLD) {
        recommendations.push({
          type: 'rule_promotion',
          ruleId,
          severity: 'low',
          recommendation:
            'This rule performs very well. Consider increasing its priority or broadening conditions',
          metrics: performance,
        });
      }
    });

    // Overall system recommendations
    if (stats.acceptanceRate < 0.3 && stats.totalSuggestions > 20) {
      recommendations.push({
        type: 'system_adjustment',
        severity: 'high',
        recommendation:
          'Overall suggestion acceptance is low. Consider reducing suggestion frequency or improving targeting',
        metrics: { acceptanceRate: stats.acceptanceRate },
      });
    }

    return recommendations;
  }
}

module.exports = {
  SuggestionFeedback,
  FeedbackAnalyzer,
  FEEDBACK_TYPES,
};
