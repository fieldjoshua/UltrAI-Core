/**
 * Activity Observer
 *
 * Core component of the Context Analyzer that captures user interactions
 * within the UltraAI system and prepares them for pattern detection.
 */

class ActivityObserver {
  constructor(options = {}) {
    // Configuration with defaults
    this.config = {
      debounceTime: options.debounceTime || 300,
      throttleTime: options.throttleTime || 200,
      maxSessionEvents: options.maxSessionEvents || 500,
      privacySettings: options.privacySettings || {
        trackClicks: true,
        trackNavigation: true,
        trackFeatureUsage: true,
        trackDwellTime: true,
        trackErrors: true,
      },
    };

    // Internal state
    this.events = [];
    this.isObserving = false;
    this.sessionStartTime = null;
    this.lastActivityTime = null;
    this.currentRoute = null;
    this.currentFeature = null;

    // Bound event handlers (for easy removal)
    this.boundHandlers = {
      click: this._handleClick.bind(this),
      keydown: this._handleKeydown.bind(this),
      navigation: this._handleNavigation.bind(this),
      error: this._handleError.bind(this),
      feature: this._handleFeatureInteraction.bind(this),
    };

    // Throttled/debounced handlers
    this.throttledHandlers = {
      mousemove: this._throttle(
        this._handleMouseMove.bind(this),
        this.config.throttleTime
      ),
    };

    this.debouncedHandlers = {
      dwell: this._debounce(this._handleDwell.bind(this), 1000),
    };
  }

  /**
   * Start observing user activity
   */
  startObserving() {
    if (this.isObserving) return;

    this.sessionStartTime = new Date();
    this.lastActivityTime = this.sessionStartTime;

    // DOM events
    if (this.config.privacySettings.trackClicks) {
      document.addEventListener('click', this.boundHandlers.click);
      document.addEventListener('keydown', this.boundHandlers.keydown);
      document.addEventListener('mousemove', this.throttledHandlers.mousemove);
    }

    // Custom application events
    if (this.config.privacySettings.trackNavigation) {
      window.addEventListener(
        'ultraai:navigation',
        this.boundHandlers.navigation
      );
    }

    if (this.config.privacySettings.trackErrors) {
      window.addEventListener('ultraai:error', this.boundHandlers.error);
    }

    if (this.config.privacySettings.trackFeatureUsage) {
      window.addEventListener('ultraai:feature', this.boundHandlers.feature);
    }

    // Record session start
    this._recordEvent({
      type: 'session',
      action: 'start',
      route: window.location.pathname,
    });

    this.isObserving = true;

    // Start the session timer
    this._startSessionTimer();

    return this;
  }

  /**
   * Stop observing user activity
   */
  stopObserving() {
    if (!this.isObserving) return;

    // Remove DOM event listeners
    document.removeEventListener('click', this.boundHandlers.click);
    document.removeEventListener('keydown', this.boundHandlers.keydown);
    document.removeEventListener('mousemove', this.throttledHandlers.mousemove);

    // Remove custom event listeners
    window.removeEventListener(
      'ultraai:navigation',
      this.boundHandlers.navigation
    );
    window.removeEventListener('ultraai:error', this.boundHandlers.error);
    window.removeEventListener('ultraai:feature', this.boundHandlers.feature);

    // Record session end
    this._recordEvent({
      type: 'session',
      action: 'end',
      sessionDuration: new Date() - this.sessionStartTime,
    });

    this.isObserving = false;

    // Clear timers
    if (this.sessionTimer) {
      clearInterval(this.sessionTimer);
    }

    return this;
  }

  /**
   * Get current activity data
   * @returns {Object} Current session data
   */
  getActivityData() {
    return {
      sessionStartTime: this.sessionStartTime,
      lastActivityTime: this.lastActivityTime,
      eventCount: this.events.length,
      currentRoute: this.currentRoute,
      currentFeature: this.currentFeature,
      recentEvents: this.events.slice(-10), // Last 10 events
      sessionDuration: new Date() - this.sessionStartTime,
      timeSinceLastActivity: new Date() - this.lastActivityTime,
    };
  }

  /**
   * Get all recorded events
   * @returns {Array} Activity events
   */
  getEvents() {
    return [...this.events];
  }

  /**
   * Clear recorded events
   */
  clearEvents() {
    this.events = [];
    return this;
  }

  /**
   * Manually record a custom event
   * @param {Object} event Event data
   */
  recordCustomEvent(event) {
    this._recordEvent({
      type: 'custom',
      ...event,
      timestamp: new Date(),
    });
    return this;
  }

  /**
   * Update privacy settings
   * @param {Object} settings New privacy settings
   */
  updatePrivacySettings(settings) {
    // Store previous settings
    const previousSettings = { ...this.config.privacySettings };

    // Update with new settings
    this.config.privacySettings = {
      ...this.config.privacySettings,
      ...settings,
    };

    // Handle changes if already observing
    if (this.isObserving) {
      // Handle click tracking changes
      if (
        previousSettings.trackClicks !== this.config.privacySettings.trackClicks
      ) {
        if (this.config.privacySettings.trackClicks) {
          document.addEventListener('click', this.boundHandlers.click);
          document.addEventListener('keydown', this.boundHandlers.keydown);
          document.addEventListener(
            'mousemove',
            this.throttledHandlers.mousemove
          );
        } else {
          document.removeEventListener('click', this.boundHandlers.click);
          document.removeEventListener('keydown', this.boundHandlers.keydown);
          document.removeEventListener(
            'mousemove',
            this.throttledHandlers.mousemove
          );
        }
      }

      // Handle navigation tracking changes
      if (
        previousSettings.trackNavigation !==
        this.config.privacySettings.trackNavigation
      ) {
        if (this.config.privacySettings.trackNavigation) {
          window.addEventListener(
            'ultraai:navigation',
            this.boundHandlers.navigation
          );
        } else {
          window.removeEventListener(
            'ultraai:navigation',
            this.boundHandlers.navigation
          );
        }
      }

      // Handle error tracking changes
      if (
        previousSettings.trackErrors !== this.config.privacySettings.trackErrors
      ) {
        if (this.config.privacySettings.trackErrors) {
          window.addEventListener('ultraai:error', this.boundHandlers.error);
        } else {
          window.removeEventListener('ultraai:error', this.boundHandlers.error);
        }
      }

      // Handle feature usage tracking changes
      if (
        previousSettings.trackFeatureUsage !==
        this.config.privacySettings.trackFeatureUsage
      ) {
        if (this.config.privacySettings.trackFeatureUsage) {
          window.addEventListener(
            'ultraai:feature',
            this.boundHandlers.feature
          );
        } else {
          window.removeEventListener(
            'ultraai:feature',
            this.boundHandlers.feature
          );
        }
      }
    }

    return this;
  }

  // Private methods

  /**
   * Record an event with timestamp and sequence info
   * @private
   */
  _recordEvent(eventData) {
    const timestamp = new Date();
    const event = {
      ...eventData,
      timestamp,
      sequence: this.events.length,
      timeSinceLastActivity: this.lastActivityTime
        ? timestamp - this.lastActivityTime
        : 0,
    };

    this.events.push(event);
    this.lastActivityTime = timestamp;

    // Trim events if exceeding maximum
    if (this.events.length > this.config.maxSessionEvents) {
      this.events = this.events.slice(-this.config.maxSessionEvents);
    }

    // Dispatch event for other systems (like Pattern Detector)
    const customEvent = new CustomEvent('ultraai:activityRecorded', {
      detail: { event },
    });
    window.dispatchEvent(customEvent);

    return event;
  }

  /**
   * Handle click events
   * @private
   */
  _handleClick(event) {
    // Get clicked element
    const element = event.target;

    // Extract element info
    const elementInfo = this._getElementInfo(element);

    // Record click event
    this._recordEvent({
      type: 'interaction',
      action: 'click',
      element: elementInfo,
    });

    // Check for dwell time
    this.debouncedHandlers.dwell(elementInfo);
  }

  /**
   * Handle keydown events
   * @private
   */
  _handleKeydown(event) {
    // Don't log actual keystrokes for privacy, just the fact that keys were pressed
    this._recordEvent({
      type: 'interaction',
      action: 'keydown',
      isModifier:
        event.ctrlKey || event.altKey || event.shiftKey || event.metaKey,
      target: this._getElementInfo(event.target),
    });
  }

  /**
   * Handle mouse movement
   * @private
   */
  _handleMouseMove(event) {
    // We don't need to record every move, just occasionally update activity time
    this.lastActivityTime = new Date();
  }

  /**
   * Handle navigation events
   * @private
   */
  _handleNavigation(event) {
    const { from, to, params } = event.detail;

    this.currentRoute = to;

    this._recordEvent({
      type: 'navigation',
      action: 'route_change',
      from,
      to,
      params: params || {},
    });
  }

  /**
   * Handle error events
   * @private
   */
  _handleError(event) {
    const { error, context } = event.detail;

    this._recordEvent({
      type: 'error',
      errorType: error.type || 'unknown',
      errorCode: error.code,
      context: context || {},
      recoverable: error.recoverable || false,
    });
  }

  /**
   * Handle feature interaction events
   * @private
   */
  _handleFeatureInteraction(event) {
    const { feature, action, context } = event.detail;

    this.currentFeature = feature;

    this._recordEvent({
      type: 'feature',
      feature,
      action,
      context: context || {},
    });
  }

  /**
   * Handle dwell time on elements
   * @private
   */
  _handleDwell(elementInfo) {
    // Only track dwell if enabled
    if (!this.config.privacySettings.trackDwellTime) return;

    this._recordEvent({
      type: 'interaction',
      action: 'dwell',
      element: elementInfo,
      duration: 1000, // The debounce time used
    });
  }

  /**
   * Extract useful information from a DOM element
   * @private
   */
  _getElementInfo(element) {
    if (!element) return null;

    return {
      tag: element.tagName?.toLowerCase(),
      id: element.id || null,
      classes: Array.from(element.classList || []),
      type: element.type || null,
      dataAction: element.dataset?.action || null,
      dataFeature: element.dataset?.feature || null,
      ariaLabel: element.getAttribute('aria-label') || null,
      text: element.textContent?.substring(0, 20) || null,
    };
  }

  /**
   * Start session timer for periodic checks
   * @private
   */
  _startSessionTimer() {
    // Check for inactivity every minute
    this.sessionTimer = setInterval(() => {
      const now = new Date();
      const inactiveTime = now - this.lastActivityTime;

      // If inactive for more than 5 minutes, record inactivity event
      if (inactiveTime > 5 * 60 * 1000) {
        this._recordEvent({
          type: 'session',
          action: 'inactive',
          duration: inactiveTime,
        });
      }
    }, 60 * 1000);
  }

  /**
   * Create a debounced function
   * @private
   */
  _debounce(func, wait) {
    let timeout;
    return function (...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  }

  /**
   * Create a throttled function
   * @private
   */
  _throttle(func, limit) {
    let lastCall = 0;
    return function (...args) {
      const now = Date.now();
      if (now - lastCall >= limit) {
        lastCall = now;
        func.apply(this, args);
      }
    };
  }
}

// Export the ActivityObserver class
export default ActivityObserver;
