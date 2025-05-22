/**
 * Tests for suggestion_feedback.js
 */

const {
  SuggestionFeedback,
  FeedbackAnalyzer,
  FEEDBACK_TYPES,
} = require('../src/suggestion_feedback');

// Mock localStorage for testing
const mockLocalStorage = (() => {
  let store = {};
  return {
    getItem: jest.fn((key) => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    clear: jest.fn(() => {
      store = {};
    }),
    removeItem: jest.fn((key) => {
      delete store[key];
    }),
    getStore: () => store,
  };
})();

// Mock analytics
const mockAnalyticsTracker = {
  trackEvent: jest.fn(),
};

describe('SuggestionFeedback', () => {
  let suggestionFeedback;

  beforeEach(() => {
    // Setup mocks
    global.localStorage = mockLocalStorage;
    global.window = { analyticsTracker: mockAnalyticsTracker };

    // Clear mocks between tests
    mockLocalStorage.clear();
    mockAnalyticsTracker.trackEvent.mockClear();

    // Create feedback instance with test options
    suggestionFeedback = new SuggestionFeedback({
      storageKey: 'test_feedback',
      maxStorageItems: 10,
    });
  });

  describe('recordFeedback', () => {
    test('should record valid feedback', () => {
      const result = suggestionFeedback.recordFeedback(
        'suggestion-123',
        FEEDBACK_TYPES.ACCEPTED,
        { test: 'data' }
      );

      expect(result).toHaveProperty('suggestionId', 'suggestion-123');
      expect(result).toHaveProperty('feedbackType', FEEDBACK_TYPES.ACCEPTED);
      expect(result).toHaveProperty('test', 'data');
      expect(result).toHaveProperty('timestamp');

      // Should be added to feedback data
      expect(suggestionFeedback.feedbackData['suggestion-123']).toHaveLength(1);

      // Should be saved to localStorage
      expect(mockLocalStorage.setItem).toHaveBeenCalled();
    });

    test('should throw error for invalid feedback type', () => {
      expect(() => {
        suggestionFeedback.recordFeedback('suggestion-123', 'invalid-type');
      }).toThrow();
    });

    test('should send analytics', () => {
      suggestionFeedback.recordFeedback(
        'suggestion-123',
        FEEDBACK_TYPES.ACCEPTED
      );

      expect(mockAnalyticsTracker.trackEvent).toHaveBeenCalledWith(
        'suggestion_feedback',
        expect.objectContaining({
          suggestionId: 'suggestion-123',
          feedbackType: FEEDBACK_TYPES.ACCEPTED,
        })
      );
    });

    test('should call feedback callback if provided', () => {
      const callback = jest.fn();
      suggestionFeedback.feedbackCallback = callback;

      suggestionFeedback.recordFeedback(
        'suggestion-123',
        FEEDBACK_TYPES.ACCEPTED
      );

      expect(callback).toHaveBeenCalled();
    });
  });

  describe('convenience methods', () => {
    test('recordAccepted should set correct feedback type', () => {
      const result = suggestionFeedback.recordAccepted('suggestion-123', {
        action: 'clicked',
      });
      expect(result.feedbackType).toBe(FEEDBACK_TYPES.ACCEPTED);
      expect(result.actionData).toEqual({ action: 'clicked' });
    });

    test('recordDismissed should set correct feedback type', () => {
      const result = suggestionFeedback.recordDismissed('suggestion-123');
      expect(result.feedbackType).toBe(FEEDBACK_TYPES.DISMISSED);
    });

    test('recordHelpful should set correct feedback type and rating', () => {
      const result = suggestionFeedback.recordHelpful('suggestion-123', 5);
      expect(result.feedbackType).toBe(FEEDBACK_TYPES.HELPFUL);
      expect(result.rating).toBe(5);
    });

    test('recordNotHelpful should set correct feedback type and reason', () => {
      const result = suggestionFeedback.recordNotHelpful(
        'suggestion-123',
        'Not relevant'
      );
      expect(result.feedbackType).toBe(FEEDBACK_TYPES.NOT_HELPFUL);
      expect(result.reason).toBe('Not relevant');
    });
  });

  describe('getFeedbackForSuggestion', () => {
    test('should return all feedback for a suggestion', () => {
      suggestionFeedback.recordAccepted('suggestion-123');
      suggestionFeedback.recordHelpful('suggestion-123', 5);
      suggestionFeedback.recordAccepted('suggestion-456');

      const feedback =
        suggestionFeedback.getFeedbackForSuggestion('suggestion-123');

      expect(feedback).toHaveLength(2);
      expect(feedback[0].suggestionId).toBe('suggestion-123');
      expect(feedback[1].suggestionId).toBe('suggestion-123');
    });

    test('should return empty array for unknown suggestion', () => {
      const feedback = suggestionFeedback.getFeedbackForSuggestion('unknown');
      expect(feedback).toHaveLength(0);
    });
  });

  describe('getFeedbackByType', () => {
    test('should return all feedback of specified type', () => {
      suggestionFeedback.recordAccepted('suggestion-123');
      suggestionFeedback.recordDismissed('suggestion-456');
      suggestionFeedback.recordAccepted('suggestion-789');

      const feedback = suggestionFeedback.getFeedbackByType(
        FEEDBACK_TYPES.ACCEPTED
      );

      expect(feedback).toHaveLength(2);
      expect(feedback[0].feedbackType).toBe(FEEDBACK_TYPES.ACCEPTED);
      expect(feedback[1].feedbackType).toBe(FEEDBACK_TYPES.ACCEPTED);
    });

    test('should throw error for invalid feedback type', () => {
      expect(() => {
        suggestionFeedback.getFeedbackByType('invalid-type');
      }).toThrow();
    });
  });

  describe('getStatistics', () => {
    test('should return correct statistics', () => {
      suggestionFeedback.recordAccepted('suggestion-123');
      suggestionFeedback.recordDismissed('suggestion-456');
      suggestionFeedback.recordAccepted('suggestion-789');
      suggestionFeedback.recordHelpful('suggestion-123', 5);

      const stats = suggestionFeedback.getStatistics();

      expect(stats.totalSuggestions).toBe(3);
      expect(stats.totalFeedbackEntries).toBe(4);
      expect(stats.byType[FEEDBACK_TYPES.ACCEPTED]).toBe(2);
      expect(stats.byType[FEEDBACK_TYPES.DISMISSED]).toBe(1);
      expect(stats.byType[FEEDBACK_TYPES.HELPFUL]).toBe(1);

      // Acceptance rate calculation: 2 accepted / (2 accepted + 1 dismissed + 0 ignored) = 2/3
      expect(stats.acceptanceRate).toBeCloseTo(0.667, 2);
    });
  });

  describe('storage limits', () => {
    test('should enforce size limits by removing oldest entries', () => {
      // Set very low limit for testing
      suggestionFeedback.maxStorageItems = 3;

      // Add 5 entries
      for (let i = 1; i <= 5; i++) {
        suggestionFeedback.recordAccepted(`suggestion-${i}`, {
          timestamp: new Date(2025, 0, i).toISOString(), // Ensure predictable order
        });
      }

      // Should only keep newest 3 entries
      const allFeedback = [
        ...suggestionFeedback.getFeedbackForSuggestion('suggestion-1'),
        ...suggestionFeedback.getFeedbackForSuggestion('suggestion-2'),
        ...suggestionFeedback.getFeedbackForSuggestion('suggestion-3'),
        ...suggestionFeedback.getFeedbackForSuggestion('suggestion-4'),
        ...suggestionFeedback.getFeedbackForSuggestion('suggestion-5'),
      ];

      expect(allFeedback).toHaveLength(3);

      // Should have entries for suggestions 3, 4, and 5 (newest)
      expect(
        suggestionFeedback.getFeedbackForSuggestion('suggestion-1')
      ).toHaveLength(0);
      expect(
        suggestionFeedback.getFeedbackForSuggestion('suggestion-2')
      ).toHaveLength(0);
      expect(
        suggestionFeedback.getFeedbackForSuggestion('suggestion-3')
      ).toHaveLength(1);
      expect(
        suggestionFeedback.getFeedbackForSuggestion('suggestion-4')
      ).toHaveLength(1);
      expect(
        suggestionFeedback.getFeedbackForSuggestion('suggestion-5')
      ).toHaveLength(1);
    });
  });
});

describe('FeedbackAnalyzer', () => {
  let suggestionFeedback;
  let feedbackAnalyzer;

  beforeEach(() => {
    // Setup test feedback instance with mock data
    suggestionFeedback = new SuggestionFeedback();

    // Mock methods
    suggestionFeedback.getStatistics = jest.fn().mockReturnValue({
      totalSuggestions: 3,
      totalFeedbackEntries: 10,
      acceptanceRate: 0.6,
      byType: {
        [FEEDBACK_TYPES.ACCEPTED]: 6,
        [FEEDBACK_TYPES.DISMISSED]: 3,
        [FEEDBACK_TYPES.IGNORED]: 1,
      },
    });

    suggestionFeedback.getFeedbackByType = jest.fn((type) => {
      if (type === FEEDBACK_TYPES.ACCEPTED) {
        return [
          { suggestionId: 'suggestion-123', ruleId: 'rule-1' },
          { suggestionId: 'suggestion-456', ruleId: 'rule-1' },
          { suggestionId: 'suggestion-789', ruleId: 'rule-2' },
          { suggestionId: 'suggestion-321', ruleId: 'rule-2' },
          { suggestionId: 'suggestion-654', ruleId: 'rule-2' },
          { suggestionId: 'suggestion-987', ruleId: 'rule-3' },
        ];
      } else if (type === FEEDBACK_TYPES.DISMISSED) {
        return [
          { suggestionId: 'suggestion-111', ruleId: 'rule-1' },
          { suggestionId: 'suggestion-222', ruleId: 'rule-3' },
          { suggestionId: 'suggestion-333', ruleId: 'rule-3' },
        ];
      }
      return [];
    });

    feedbackAnalyzer = new FeedbackAnalyzer(suggestionFeedback);
  });

  describe('analyzePerformance', () => {
    test('should calculate rule performance correctly', () => {
      const analysis = feedbackAnalyzer.analyzePerformance();

      expect(analysis).toHaveProperty('overallStats');
      expect(analysis).toHaveProperty('rulePerformance');
      expect(analysis).toHaveProperty('recommendations');

      // Rule 1: 2 accepted, 1 dismissed = 2/3 acceptance rate
      expect(analysis.rulePerformance['rule-1'].accepted).toBe(2);
      expect(analysis.rulePerformance['rule-1'].dismissed).toBe(1);
      expect(analysis.rulePerformance['rule-1'].total).toBe(3);
      expect(analysis.rulePerformance['rule-1'].acceptanceRate).toBeCloseTo(
        0.667,
        2
      );

      // Rule 2: 3 accepted, 0 dismissed = 100% acceptance rate
      expect(analysis.rulePerformance['rule-2'].accepted).toBe(3);
      expect(analysis.rulePerformance['rule-2'].dismissed).toBe(0);
      expect(analysis.rulePerformance['rule-2'].acceptanceRate).toBe(1);

      // Rule 3: 1 accepted, 2 dismissed = 1/3 acceptance rate
      expect(analysis.rulePerformance['rule-3'].accepted).toBe(1);
      expect(analysis.rulePerformance['rule-3'].dismissed).toBe(2);
      expect(analysis.rulePerformance['rule-3'].acceptanceRate).toBeCloseTo(
        0.333,
        2
      );
    });

    test('should generate appropriate recommendations', () => {
      const analysis = feedbackAnalyzer.analyzePerformance();

      // Should have recommendation for rule-2 (high acceptance)
      const rule2Recommendation = analysis.recommendations.find(
        (r) => r.ruleId === 'rule-2' && r.type === 'rule_promotion'
      );
      expect(rule2Recommendation).toBeDefined();

      // Should not have low-acceptance recommendation for rule-3 because not enough data
      // (would need 5+ total interactions)
      const rule3Recommendation = analysis.recommendations.find(
        (r) => r.ruleId === 'rule-3' && r.type === 'rule_adjustment'
      );
      expect(rule3Recommendation).toBeUndefined();
    });
  });
});
