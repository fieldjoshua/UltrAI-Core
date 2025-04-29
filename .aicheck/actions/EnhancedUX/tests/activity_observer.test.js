/**
 * Tests for ActivityObserver
 */

import ActivityObserver from '../src/activity_observer';

// Mock DOM event classes that may not exist in test environment
global.CustomEvent =
  global.CustomEvent ||
  class CustomEvent {
    constructor(type, options) {
      this.type = type;
      this.detail = options?.detail;
      this.timeStamp = Date.now();
    }
  };

describe('ActivityObserver', () => {
  let observer;
  let originalAddEventListener;
  let originalRemoveEventListener;
  let originalDispatchEvent;
  let addedEventListeners = [];
  let removedEventListeners = [];
  let dispatchedEvents = [];

  // Setup mocks
  beforeEach(() => {
    jest.useFakeTimers();

    // Track added/removed event listeners
    addedEventListeners = [];
    removedEventListeners = [];
    dispatchedEvents = [];

    originalAddEventListener = window.addEventListener;
    originalRemoveEventListener = window.removeEventListener;
    originalDispatchEvent = window.dispatchEvent;

    // Mock document event listeners
    document.addEventListener = jest.fn((event, handler) => {
      addedEventListeners.push({ target: 'document', event, handler });
    });

    document.removeEventListener = jest.fn((event, handler) => {
      removedEventListeners.push({ target: 'document', event, handler });
    });

    // Mock window event listeners
    window.addEventListener = jest.fn((event, handler) => {
      addedEventListeners.push({ target: 'window', event, handler });
    });

    window.removeEventListener = jest.fn((event, handler) => {
      removedEventListeners.push({ target: 'window', event, handler });
    });

    // Mock dispatch event
    window.dispatchEvent = jest.fn((event) => {
      dispatchedEvents.push(event);
      return true;
    });

    // Create observer instance with default settings
    observer = new ActivityObserver();
  });

  // Clean up mocks
  afterEach(() => {
    jest.clearAllTimers();
    document.addEventListener = originalAddEventListener;
    document.removeEventListener = originalRemoveEventListener;
    window.addEventListener = originalAddEventListener;
    window.removeEventListener = originalRemoveEventListener;
    window.dispatchEvent = originalDispatchEvent;
  });

  describe('initialization', () => {
    test('should initialize with default settings', () => {
      expect(observer.config).toBeDefined();
      expect(observer.config.privacySettings.trackClicks).toBe(true);
      expect(observer.events).toEqual([]);
      expect(observer.isObserving).toBe(false);
    });

    test('should accept custom settings', () => {
      const customObserver = new ActivityObserver({
        debounceTime: 500,
        maxSessionEvents: 1000,
        privacySettings: {
          trackClicks: false,
          trackNavigation: true,
        },
      });

      expect(customObserver.config.debounceTime).toBe(500);
      expect(customObserver.config.maxSessionEvents).toBe(1000);
      expect(customObserver.config.privacySettings.trackClicks).toBe(false);
      expect(customObserver.config.privacySettings.trackNavigation).toBe(true);
      // Should keep defaults for unspecified settings
      expect(customObserver.config.privacySettings.trackErrors).toBe(true);
    });
  });

  describe('startObserving', () => {
    test('should setup event listeners based on privacy settings', () => {
      observer.startObserving();

      // Should have setup DOM event listeners
      expect(document.addEventListener).toHaveBeenCalledWith(
        'click',
        expect.any(Function)
      );
      expect(document.addEventListener).toHaveBeenCalledWith(
        'keydown',
        expect.any(Function)
      );
      expect(document.addEventListener).toHaveBeenCalledWith(
        'mousemove',
        expect.any(Function)
      );

      // Should have setup custom event listeners
      expect(window.addEventListener).toHaveBeenCalledWith(
        'ultraai:navigation',
        expect.any(Function)
      );
      expect(window.addEventListener).toHaveBeenCalledWith(
        'ultraai:error',
        expect.any(Function)
      );
      expect(window.addEventListener).toHaveBeenCalledWith(
        'ultraai:feature',
        expect.any(Function)
      );

      expect(observer.isObserving).toBe(true);
      expect(observer.sessionStartTime).toBeInstanceOf(Date);
      expect(observer.events.length).toBe(1);
      expect(observer.events[0].type).toBe('session');
      expect(observer.events[0].action).toBe('start');
    });

    test('should not add event listeners if already observing', () => {
      observer.startObserving();
      document.addEventListener.mockClear();
      window.addEventListener.mockClear();

      // Call again
      observer.startObserving();

      // Should not have added listeners again
      expect(document.addEventListener).not.toHaveBeenCalled();
      expect(window.addEventListener).not.toHaveBeenCalled();
    });

    test('should respect privacy settings', () => {
      observer.updatePrivacySettings({
        trackClicks: false,
        trackNavigation: false,
      });

      observer.startObserving();

      // Should not have set up click listeners
      expect(document.addEventListener).not.toHaveBeenCalledWith(
        'click',
        expect.any(Function)
      );
      expect(document.addEventListener).not.toHaveBeenCalledWith(
        'keydown',
        expect.any(Function)
      );
      expect(document.addEventListener).not.toHaveBeenCalledWith(
        'mousemove',
        expect.any(Function)
      );

      // Should not have set up navigation listener
      expect(window.addEventListener).not.toHaveBeenCalledWith(
        'ultraai:navigation',
        expect.any(Function)
      );

      // Should still have set up other listeners
      expect(window.addEventListener).toHaveBeenCalledWith(
        'ultraai:error',
        expect.any(Function)
      );
      expect(window.addEventListener).toHaveBeenCalledWith(
        'ultraai:feature',
        expect.any(Function)
      );
    });
  });

  describe('stopObserving', () => {
    test('should remove event listeners and record session end', () => {
      observer.startObserving();
      document.removeEventListener.mockClear();
      window.removeEventListener.mockClear();

      observer.stopObserving();

      // Should have removed all event listeners
      expect(document.removeEventListener).toHaveBeenCalledWith(
        'click',
        expect.any(Function)
      );
      expect(document.removeEventListener).toHaveBeenCalledWith(
        'keydown',
        expect.any(Function)
      );
      expect(document.removeEventListener).toHaveBeenCalledWith(
        'mousemove',
        expect.any(Function)
      );

      expect(window.removeEventListener).toHaveBeenCalledWith(
        'ultraai:navigation',
        expect.any(Function)
      );
      expect(window.removeEventListener).toHaveBeenCalledWith(
        'ultraai:error',
        expect.any(Function)
      );
      expect(window.removeEventListener).toHaveBeenCalledWith(
        'ultraai:feature',
        expect.any(Function)
      );

      expect(observer.isObserving).toBe(false);
      expect(observer.events.length).toBe(2); // Start + End
      expect(observer.events[1].type).toBe('session');
      expect(observer.events[1].action).toBe('end');
    });

    test('should not remove listeners if not observing', () => {
      observer.stopObserving();

      expect(document.removeEventListener).not.toHaveBeenCalled();
      expect(window.removeEventListener).not.toHaveBeenCalled();
    });
  });

  describe('updatePrivacySettings', () => {
    test('should update settings and adjust listeners if observing', () => {
      observer.startObserving();
      document.addEventListener.mockClear();
      document.removeEventListener.mockClear();
      window.addEventListener.mockClear();
      window.removeEventListener.mockClear();

      observer.updatePrivacySettings({
        trackClicks: false,
        trackNavigation: false,
      });

      // Should have removed click listeners
      expect(document.removeEventListener).toHaveBeenCalledWith(
        'click',
        expect.any(Function)
      );
      expect(document.removeEventListener).toHaveBeenCalledWith(
        'keydown',
        expect.any(Function)
      );
      expect(document.removeEventListener).toHaveBeenCalledWith(
        'mousemove',
        expect.any(Function)
      );

      // Should have removed navigation listener
      expect(window.removeEventListener).toHaveBeenCalledWith(
        'ultraai:navigation',
        expect.any(Function)
      );

      // Should not have affected other listeners
      expect(window.removeEventListener).not.toHaveBeenCalledWith(
        'ultraai:error',
        expect.any(Function)
      );
      expect(window.removeEventListener).not.toHaveBeenCalledWith(
        'ultraai:feature',
        expect.any(Function)
      );
    });

    test('should not adjust listeners if settings unchanged', () => {
      observer.startObserving();
      document.addEventListener.mockClear();
      document.removeEventListener.mockClear();

      observer.updatePrivacySettings({
        trackClicks: true, // Already true by default
      });

      // Should not have modified listeners
      expect(document.addEventListener).not.toHaveBeenCalled();
      expect(document.removeEventListener).not.toHaveBeenCalled();
    });
  });

  describe('event recording', () => {
    test('should record custom events', () => {
      observer.recordCustomEvent({
        action: 'test',
        detail: 'custom data',
      });

      expect(observer.events.length).toBe(1);
      expect(observer.events[0].type).toBe('custom');
      expect(observer.events[0].action).toBe('test');
      expect(observer.events[0].detail).toBe('custom data');
      expect(observer.events[0].timestamp).toBeInstanceOf(Date);
    });

    test('should dispatch activity recorded events', () => {
      observer.recordCustomEvent({ action: 'test' });

      expect(window.dispatchEvent).toHaveBeenCalled();
      expect(dispatchedEvents.length).toBe(1);
      expect(dispatchedEvents[0].type).toBe('ultraai:activityRecorded');
      expect(dispatchedEvents[0].detail.event.action).toBe('test');
    });

    test('should limit number of events stored', () => {
      // Set a small max events limit
      observer.config.maxSessionEvents = 3;

      // Record more than the limit
      observer.recordCustomEvent({ id: 1 });
      observer.recordCustomEvent({ id: 2 });
      observer.recordCustomEvent({ id: 3 });
      observer.recordCustomEvent({ id: 4 });
      observer.recordCustomEvent({ id: 5 });

      // Should only keep the most recent
      expect(observer.events.length).toBe(3);
      expect(observer.events[0].id).toBe(3);
      expect(observer.events[1].id).toBe(4);
      expect(observer.events[2].id).toBe(5);
    });
  });

  describe('event handling', () => {
    let mockClickEvent;
    let mockKeyEvent;
    let mockNavigationEvent;
    let mockErrorEvent;
    let mockFeatureEvent;

    beforeEach(() => {
      // Set up mock events
      mockClickEvent = {
        target: {
          tagName: 'BUTTON',
          id: 'test-btn',
          classList: ['btn', 'primary'],
          dataset: { action: 'submit' },
          getAttribute: jest.fn((attr) =>
            attr === 'aria-label' ? 'Submit Form' : null
          ),
          textContent: 'Submit',
        },
      };

      mockKeyEvent = {
        target: {
          tagName: 'INPUT',
          type: 'text',
          id: 'search',
          classList: ['search-input'],
          getAttribute: jest.fn(() => null),
        },
        ctrlKey: true,
      };

      mockNavigationEvent = {
        detail: {
          from: '/dashboard',
          to: '/reports',
          params: { id: '123' },
        },
      };

      mockErrorEvent = {
        detail: {
          error: {
            type: 'api',
            code: 'ERR_API_TIMEOUT',
            recoverable: true,
          },
          context: {
            endpoint: '/data',
            method: 'GET',
          },
        },
      };

      mockFeatureEvent = {
        detail: {
          feature: 'confidenceAnalysis',
          action: 'start',
          context: {
            dataSize: 'large',
          },
        },
      };

      // Start observing
      observer.startObserving();
      // Clear initial event
      observer.events = [];
    });

    test('should handle click events', () => {
      // Find the click handler
      const clickHandler = addedEventListeners.find(
        (l) => l.target === 'document' && l.event === 'click'
      ).handler;

      clickHandler(mockClickEvent);

      expect(observer.events.length).toBe(1);
      expect(observer.events[0].type).toBe('interaction');
      expect(observer.events[0].action).toBe('click');
      expect(observer.events[0].element.tag).toBe('button');
      expect(observer.events[0].element.id).toBe('test-btn');
      expect(observer.events[0].element.dataAction).toBe('submit');
    });

    test('should handle keydown events', () => {
      const keyHandler = addedEventListeners.find(
        (l) => l.target === 'document' && l.event === 'keydown'
      ).handler;

      keyHandler(mockKeyEvent);

      expect(observer.events.length).toBe(1);
      expect(observer.events[0].type).toBe('interaction');
      expect(observer.events[0].action).toBe('keydown');
      expect(observer.events[0].isModifier).toBe(true);
      expect(observer.events[0].target.tag).toBe('input');
    });

    test('should handle navigation events', () => {
      const navHandler = addedEventListeners.find(
        (l) => l.target === 'window' && l.event === 'ultraai:navigation'
      ).handler;

      navHandler(mockNavigationEvent);

      expect(observer.events.length).toBe(1);
      expect(observer.events[0].type).toBe('navigation');
      expect(observer.events[0].from).toBe('/dashboard');
      expect(observer.events[0].to).toBe('/reports');
      expect(observer.events[0].params.id).toBe('123');
      expect(observer.currentRoute).toBe('/reports');
    });

    test('should handle error events', () => {
      const errorHandler = addedEventListeners.find(
        (l) => l.target === 'window' && l.event === 'ultraai:error'
      ).handler;

      errorHandler(mockErrorEvent);

      expect(observer.events.length).toBe(1);
      expect(observer.events[0].type).toBe('error');
      expect(observer.events[0].errorType).toBe('api');
      expect(observer.events[0].errorCode).toBe('ERR_API_TIMEOUT');
      expect(observer.events[0].recoverable).toBe(true);
      expect(observer.events[0].context.endpoint).toBe('/data');
    });

    test('should handle feature events', () => {
      const featureHandler = addedEventListeners.find(
        (l) => l.target === 'window' && l.event === 'ultraai:feature'
      ).handler;

      featureHandler(mockFeatureEvent);

      expect(observer.events.length).toBe(1);
      expect(observer.events[0].type).toBe('feature');
      expect(observer.events[0].feature).toBe('confidenceAnalysis');
      expect(observer.events[0].action).toBe('start');
      expect(observer.events[0].context.dataSize).toBe('large');
      expect(observer.currentFeature).toBe('confidenceAnalysis');
    });

    test('should handle dwell events', () => {
      // Find the click handler which triggers dwell
      const clickHandler = addedEventListeners.find(
        (l) => l.target === 'document' && l.event === 'click'
      ).handler;

      clickHandler(mockClickEvent);

      // Fast forward past debounce time
      jest.advanceTimersByTime(1001);

      // Should have recorded click + dwell
      expect(observer.events.length).toBe(2);
      expect(observer.events[1].type).toBe('interaction');
      expect(observer.events[1].action).toBe('dwell');
      expect(observer.events[1].element.tag).toBe('button');
    });

    test('should not track dwell if disabled', () => {
      observer.updatePrivacySettings({
        trackDwellTime: false,
      });

      const clickHandler = addedEventListeners.find(
        (l) => l.target === 'document' && l.event === 'click'
      ).handler;

      clickHandler(mockClickEvent);

      // Fast forward past debounce time
      jest.advanceTimersByTime(1001);

      // Should only have recorded click, not dwell
      expect(observer.events.length).toBe(1);
      expect(observer.events[0].action).toBe('click');
    });
  });

  describe('session timer', () => {
    test('should record inactivity events', () => {
      observer.startObserving();
      observer.events = []; // Clear initial event

      // Forward time to trigger inactivity check (5min + 1min for timer interval)
      jest.advanceTimersByTime(6 * 60 * 1000);

      expect(observer.events.length).toBe(1);
      expect(observer.events[0].type).toBe('session');
      expect(observer.events[0].action).toBe('inactive');
    });
  });

  describe('utility methods', () => {
    test('getActivityData should return current session data', () => {
      observer.startObserving();
      const data = observer.getActivityData();

      expect(data.sessionStartTime).toBeInstanceOf(Date);
      expect(data.eventCount).toBe(1); // The start event
      expect(data.sessionDuration).toBeGreaterThanOrEqual(0);
    });

    test('getEvents should return a copy of the events array', () => {
      observer.startObserving();
      const events = observer.getEvents();

      expect(events.length).toBe(1);

      // Modifying the returned array should not affect the original
      events.push({ type: 'test' });
      expect(observer.events.length).toBe(1);
    });

    test('clearEvents should empty the events array', () => {
      observer.startObserving();
      observer.clearEvents();

      expect(observer.events.length).toBe(0);
    });
  });
});
