/**
 * UltraAI EnhancedUX
 *
 * Main entry point for the EnhancedUX components.
 */

import ActivityObserver from './activity_observer';
import UserProfile from './user_profile';

// Export individual components
export { ActivityObserver, UserProfile };

// Future exports to be added as components are implemented:
// export { default as PatternDetector } from './pattern_detector';
// export { default as ContextGenerator } from './context_generator';
// export { default as SuggestionRules } from './suggestion_rules';
// export { default as SuggestionRanking } from './suggestion_ranking';
// export { default as SuggestionPresenter } from './suggestion_presenter';

/**
 * Create and initialize the suggestion system
 * @param {Object} options Configuration options
 * @returns {Object} Initialized suggestion system
 */
export function createSuggestionSystem(options = {}) {
  // Create the user profile
  const userProfile = new UserProfile(options.profile);

  // Create and start activity observer
  const activityObserver = new ActivityObserver(options.observer);
  if (options.autoStart !== false) {
    activityObserver.startObserving();
  }

  // Return the suggestion system interface
  return {
    activityObserver,
    userProfile,

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

      return this;
    },
  };
}

// Default export for easier imports
export default {
  createSuggestionSystem,
  ActivityObserver,
  UserProfile,
};
