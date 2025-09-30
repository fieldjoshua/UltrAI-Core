/**
 * Unit tests for SSEPanel component with mocked EventSource
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { jest } from '@jest/globals';

// Mock EventSource globally
const mockEventSource = {
  close: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  onopen: null,
  onmessage: null,
  onerror: null,
  readyState: 1, // OPEN
};

// Mock the EventSource constructor
global.EventSource = jest.fn(() => mockEventSource) as any;

// Import SSEPanel after mocking EventSource
import SSEPanel from '../SSEPanel';

describe('SSEPanel', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockEventSource.close.mockClear();
    mockEventSource.addEventListener.mockClear();
    mockEventSource.removeEventListener.mockClear();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Connection States', () => {
    test('shows connecting status initially', () => {
      render(<SSEPanel correlationId="test-123" />);

      expect(screen.getByText('connecting')).toBeInTheDocument();
      expect(screen.getByText(/Waiting for events/)).toBeInTheDocument();
    });

    test('shows open status when connection opens', async () => {
      render(<SSEPanel correlationId="test-123" />);

      // Simulate connection open
      if (mockEventSource.onopen) {
        mockEventSource.onopen(new Event('open'));
      }

      await waitFor(() => {
        expect(screen.getByText('open')).toBeInTheDocument();
      });
    });

    test('shows error status when connection fails', async () => {
      render(<SSEPanel correlationId="test-123" />);

      // Simulate connection error
      if (mockEventSource.onerror) {
        mockEventSource.onerror(new Event('error'));
      }

      await waitFor(() => {
        expect(screen.getByText('error')).toBeInTheDocument();
      });
    });

    test('handles invalid correlation ID gracefully', () => {
      // Mock console.error to avoid noise in test output
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      render(<SSEPanel correlationId="" />);

      expect(screen.getByText('error')).toBeInTheDocument();

      consoleSpy.mockRestore();
    });
  });

  describe('Event Handling', () => {
    test('displays named events correctly', async () => {
      render(<SSEPanel correlationId="test-123" />);

      // Simulate receiving a named event
      const messageEvent = new MessageEvent('analysis_start', {
        data: JSON.stringify({
          event: 'analysis_start',
          data: { models: ['gpt-4', 'claude-3'] }
        })
      });

      // Find the message handler and call it
      const messageHandler = mockEventSource.addEventListener.mock.calls.find(
        call => call[0] === 'analysis_start'
      )?.[1];

      if (messageHandler) {
        messageHandler(messageEvent);
      }

      await waitFor(() => {
        expect(screen.getByText('analysis_start')).toBeInTheDocument();
        expect(screen.getByText(/"models": \["gpt-4", "claude-3"\]/)).toBeInTheDocument();
      });
    });

    test('displays connected event on initial connection', async () => {
      render(<SSEPanel correlationId="test-123" />);

      // Simulate initial connected event
      const messageEvent = new MessageEvent('connected', {
        data: JSON.stringify({
          event: 'connected'
        })
      });

      // Find the message handler for 'connected' event
      const messageHandler = mockEventSource.addEventListener.mock.calls.find(
        call => call[0] === 'connected'
      )?.[1];

      if (messageHandler) {
        messageHandler(messageEvent);
      }

      await waitFor(() => {
        expect(screen.getByText('connected')).toBeInTheDocument();
      });
    });

    test('handles malformed JSON gracefully', async () => {
      render(<SSEPanel correlationId="test-123" />);

      // Simulate receiving malformed JSON
      const messageEvent = new MessageEvent('message', {
        data: 'invalid json {'
      });

      // Find the message handler and call it
      const messageHandler = mockEventSource.onmessage;
      if (messageHandler) {
        messageHandler(messageEvent);
      }

      await waitFor(() => {
        expect(screen.getByText('message')).toBeInTheDocument();
        expect(screen.getByText('invalid json {')).toBeInTheDocument();
      });
    });

    test('displays heartbeat events', async () => {
      render(<SSEPanel correlationId="test-123" />);

      // Simulate heartbeat event
      const messageEvent = new MessageEvent('heartbeat', {
        data: JSON.stringify({
          event: 'heartbeat'
        })
      });

      // Find the message handler for 'heartbeat' event
      const messageHandler = mockEventSource.addEventListener.mock.calls.find(
        call => call[0] === 'heartbeat'
      )?.[1];

      if (messageHandler) {
        messageHandler(messageEvent);
      }

      await waitFor(() => {
        expect(screen.getByText('heartbeat')).toBeInTheDocument();
      });
    });
  });

  describe('EventSource Integration', () => {
    test('creates EventSource with correct URL', () => {
      const correlationId = 'test-correlation-456';
      render(<SSEPanel correlationId={correlationId} />);

      expect(global.EventSource).toHaveBeenCalledWith(
        expect.stringContaining(`/orchestrator/events?correlation_id=${encodeURIComponent(correlationId)}`),
        { withCredentials: false }
      );
    });

    test('sanitizes correlation ID in URL', () => {
      const correlationId = 'test-with-spaces_and_symbols!';
      render(<SSEPanel correlationId={correlationId} />);

      expect(global.EventSource).toHaveBeenCalledWith(
        expect.stringContaining(encodeURIComponent(correlationId.replace(/[^a-zA-Z0-9_\-]/g, ''))),
        { withCredentials: false }
      );
    });

    test('sets up event listeners for known events', () => {
      render(<SSEPanel correlationId="test-123" />);

      const expectedEvents = [
        'connected',
        'analysis_start',
        'initial_start',
        'model_selected',
        'model_completed',
        'pipeline_complete',
        'service_unavailable'
      ];

      expectedEvents.forEach(eventName => {
        expect(mockEventSource.addEventListener).toHaveBeenCalledWith(
          eventName,
          expect.any(Function)
        );
      });
    });

    test('cleans up EventSource on unmount', () => {
      const { unmount } = render(<SSEPanel correlationId="test-123" />);

      unmount();

      expect(mockEventSource.close).toHaveBeenCalled();
    });

    test('limits events to maxEvents prop', async () => {
      render(<SSEPanel correlationId="test-123" maxEvents={2} />);

      // Simulate multiple events
      for (let i = 0; i < 5; i++) {
        const messageEvent = new MessageEvent('test_event', {
          data: JSON.stringify({
            event: 'test_event',
            data: { index: i }
          })
        });

        const messageHandler = mockEventSource.addEventListener.mock.calls.find(
          call => call[0] === 'test_event'
        )?.[1];

        if (messageHandler) {
          messageHandler(messageEvent);
        }
      }

      // Should only show the latest 2 events (plus initial connected)
      await waitFor(() => {
        const eventElements = screen.getAllByText('test_event');
        expect(eventElements.length).toBeLessThanOrEqual(2);
      });
    });
  });

  describe('Display Features', () => {
    test('shows custom title when provided', () => {
      const customTitle = 'Custom Event Stream';
      render(<SSEPanel correlationId="test-123" title={customTitle} />);

      expect(screen.getByText(customTitle)).toBeInTheDocument();
    });

    test('uses default title when none provided', () => {
      render(<SSEPanel correlationId="test-123" />);

      expect(screen.getByText('Live Orchestrator Events')).toBeInTheDocument();
    });

    test('displays correlation ID in waiting message', () => {
      const correlationId = 'my-analysis-789';
      render(<SSEPanel correlationId={correlationId} />);

      expect(screen.getByText(`Waiting for events on correlation_id: ${correlationId}`)).toBeInTheDocument();
    });

    test('formats timestamps correctly', async () => {
      render(<SSEPanel correlationId="test-123" />);

      // Simulate receiving an event
      const messageEvent = new MessageEvent('test_event', {
        data: JSON.stringify({
          event: 'test_event',
          data: { message: 'test' }
        })
      });

      const messageHandler = mockEventSource.addEventListener.mock.calls.find(
        call => call[0] === 'test_event'
      )?.[1];

      if (messageHandler) {
        messageHandler(messageEvent);
      }

      await waitFor(() => {
        // Should show ISO timestamp format
        expect(screen.getByText(/\[.*T.*Z\]/)).toBeInTheDocument();
      });
    });

    test('pretty-prints JSON payloads', async () => {
      render(<SSEPanel correlationId="test-123" />);

      const testData = {
        event: 'test_event',
        data: {
          models: ['gpt-4', 'claude-3'],
          metadata: {
            processing_time: 12.5,
            tokens_used: 1500
          }
        }
      };

      const messageEvent = new MessageEvent('test_event', {
        data: JSON.stringify(testData)
      });

      const messageHandler = mockEventSource.addEventListener.mock.calls.find(
        call => call[0] === 'test_event'
      )?.[1];

      if (messageHandler) {
        messageHandler(messageEvent);
      }

      await waitFor(() => {
        expect(screen.getByText(/"models": \[/)).toBeInTheDocument();
        expect(screen.getByText(/"processing_time": 12.5/)).toBeInTheDocument();
      });
    });
  });
});