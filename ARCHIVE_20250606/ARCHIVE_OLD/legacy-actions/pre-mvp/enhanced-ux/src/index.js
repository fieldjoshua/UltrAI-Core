/**
 * UltraAI EnhancedUX
 *
 * Main entry point for the EnhancedUX components.
 */

const ActivityObserver = require('./activity_observer');
const UserProfile = require('./user_profile');
const { processSuggestions } = require('./suggestion_rules');
const { allRules } = require('./rule_definitions');
const {
  SuggestionFeedback,
  FeedbackAnalyzer,
  FEEDBACK_TYPES,
} = require('./suggestion_feedback');
const {
  SuggestionPresenter,
  COMPONENT_TYPES,
  ANIMATION_TYPES,
  THEMES,
} = require('./suggestion_presenter');

// Import feature discovery components
import {
  createExperienceTracker,
  ACTION_SCORES,
  createAchievementSystem,
  ACHIEVEMENT_TIERS,
  ProgressiveDisclosure,
  AchievementNotification,
} from './feature_discovery';

// Re-export UI components
module.exports.components = require('./components');

// Export individual components
module.exports.ActivityObserver = ActivityObserver;
module.exports.UserProfile = UserProfile;
module.exports.processSuggestions = processSuggestions;
module.exports.rules = allRules;
module.exports.SuggestionFeedback = SuggestionFeedback;
module.exports.FeedbackAnalyzer = FeedbackAnalyzer;
module.exports.FEEDBACK_TYPES = FEEDBACK_TYPES;
module.exports.SuggestionPresenter = SuggestionPresenter;
module.exports.COMPONENT_TYPES = COMPONENT_TYPES;
module.exports.ANIMATION_TYPES = ANIMATION_TYPES;
module.exports.THEMES = THEMES;

// Export feature discovery components
module.exports.createExperienceTracker = createExperienceTracker;
module.exports.ACTION_SCORES = ACTION_SCORES;
module.exports.createAchievementSystem = createAchievementSystem;
module.exports.ACHIEVEMENT_TIERS = ACHIEVEMENT_TIERS;
module.exports.ProgressiveDisclosure = ProgressiveDisclosure;
module.exports.AchievementNotification = AchievementNotification;

// Re-export demo components
import * as demos from './demo';
module.exports.demos = demos;

// Future exports to be added as components are implemented:
// module.exports.PatternDetector = require('./pattern_detector');
// module.exports.ContextGenerator = require('./context_generator');

/**
 * Create and initialize the suggestion system
 * @param {Object} options Configuration options
 * @returns {Object} Initialized suggestion system
 */
function createSuggestionSystem(options = {}) {
  // Create the user profile
  const userProfile = new UserProfile(options.profile);

  // Create and start activity observer
  const activityObserver = new ActivityObserver(options.observer);
  if (options.autoStart !== false) {
    activityObserver.startObserving();
  }

  // Load rules
  const rules = options.rules || allRules;

  // Create feedback system
  const suggestionFeedback = new SuggestionFeedback(options.feedback);
  const feedbackAnalyzer = new FeedbackAnalyzer(suggestionFeedback);

  // Create presenter with feedback system integration
  const suggestionPresenter = new SuggestionPresenter({
    position: options.position || 'bottom-right',
    theme: options.theme || THEMES.STANDARD,
    animationsEnabled: options.animationsEnabled !== false,
    maxVisibleSuggestions: options.maxVisibleSuggestions || 1,
    feedbackSystem: suggestionFeedback,
  });

  // Create feature discovery system
  const experienceTracker = createExperienceTracker(options.experience);
  const achievementSystem = createAchievementSystem(
    {
      ...options.achievements,
    },
    experienceTracker
  );

  // Return the suggestion system interface
  return {
    activityObserver,
    userProfile,
    rules,
    suggestionFeedback,
    feedbackAnalyzer,
    suggestionPresenter,
    experienceTracker,
    achievementSystem,

    /**
     * Start the suggestion system
     */
    start() {
      if (!activityObserver.isObserving) {
        activityObserver.startObserving();
      }
      return this;
    },

    /**
     * Stop the suggestion system
     */
    stop() {
      if (activityObserver.isObserving) {
        activityObserver.stopObserving();
      }
      return this;
    },

    /**
     * Generate suggestions based on current context
     * @returns {Object} Ranked suggestions
     */
    generateSuggestions() {
      // Get the current context from activity observer and user profile
      const context = {
        timestamp: new Date().toISOString(),
        userContext: userProfile.getUserData(),
        activityContext: activityObserver.getActivityData(),
        systemContext: {
          // This would be populated from the system state
          availableFeatures: [
            'basicAnalysis',
            'advancedOptions',
            'exportResults',
          ],
          recentUpdates: [],
        },
      };

      // Process suggestions using the rules engine
      return processSuggestions(context, this.rules);
    },

    /**
     * Generate and display suggestions to the user
     * @param {String} componentType The type of component to use (card, inline, tooltip)
     * @returns {Array} Array of rendered suggestion elements
     */
    showSuggestions(componentType = COMPONENT_TYPES.CARD) {
      const suggestions = this.generateSuggestions();
      const renderedElements = [];

      if (
        suggestions &&
        suggestions.suggestions &&
        suggestions.suggestions.length > 0
      ) {
        suggestions.suggestions.forEach((suggestion) => {
          const element = suggestionPresenter.presentSuggestion(
            suggestion,
            componentType
          );
          if (element) {
            renderedElements.push(element);
          }
        });
      }

      return renderedElements;
    },

    /**
     * Dismiss all currently visible suggestions
     * @param {String} feedbackType Optional feedback type for the dismissal
     */
    dismissAllSuggestions(feedbackType) {
      suggestionPresenter.dismissAllSuggestions(feedbackType);
    },

    /**
     * Record user feedback on a suggestion
     * @param {String} suggestionId The ID of the suggestion
     * @param {String} feedbackType The type of feedback
     * @param {Object} additionalData Additional data about the feedback
     * @returns {Object} The recorded feedback
     */
    recordFeedback(suggestionId, feedbackType, additionalData = {}) {
      return suggestionFeedback.recordFeedback(
        suggestionId,
        feedbackType,
        additionalData
      );
    },

    /**
     * Analyze suggestion performance and get recommendations
     * @returns {Object} Analysis results with recommendations
     */
    analyzePerformance() {
      return feedbackAnalyzer.analyzePerformance();
    },

    /**
     * Start a guided tour
     * @param {String} tourId ID of the tour to start
     * @returns {Boolean} Whether the tour was started successfully
     */
    startTour(tourId) {
      // For now, just log the tour start request
      // Will be implemented when the GuidedTour component is fully integrated
      console.log(`Tour requested: ${tourId}`);
      return true;
    },

    /**
     * Get the current user experience data
     * @returns {Object} User experience information
     */
    getUserExperience() {
      return experienceTracker.getExperienceSummary();
    },

    /**
     * Update system configuration
     * @param {Object} newOptions New configuration options
     */
    updateConfig(newOptions = {}) {
      if (newOptions.observer) {
        const wasObserving = activityObserver.isObserving;

        if (wasObserving) {
          activityObserver.stopObserving();
        }

        if (newOptions.observer.privacySettings) {
          activityObserver.updatePrivacySettings(
            newOptions.observer.privacySettings
          );
        }

        if (wasObserving) {
          activityObserver.startObserving();
        }
      }

      if (newOptions.profile) {
        userProfile.updatePreferences(newOptions.profile);
      }

      if (newOptions.rules) {
        this.rules = newOptions.rules;
      }

      return this;
    },
  };
}

// Module exports
module.exports.createSuggestionSystem = createSuggestionSystem;

// Default export for easier imports
module.exports.default = {
  createSuggestionSystem,
  ActivityObserver,
  UserProfile,
  processSuggestions,
  rules: allRules,
  SuggestionFeedback,
  FeedbackAnalyzer,
  FEEDBACK_TYPES,
  SuggestionPresenter,
  COMPONENT_TYPES,
  ANIMATION_TYPES,
  THEMES,
  createExperienceTracker,
  ACTION_SCORES,
  createAchievementSystem,
  ACHIEVEMENT_TIERS,
  ProgressiveDisclosure,
  AchievementNotification,
  components: module.exports.components,
};

import React from 'react';
import ReactDOM from 'react-dom';
import BasicHelpDemo from './components/BasicHelpDemo';

ReactDOM.render(
  <React.StrictMode>
    <BasicHelpDemo />
  </React.StrictMode>,
  document.getElementById('root')
);
