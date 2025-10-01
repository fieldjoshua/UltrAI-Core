/**
 * Unit tests for SSEPanel component with mocked EventSource.
 * 
 * Tests SSE connection lifecycle, event handling, and display rendering.
 */

import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import SSEPanel from '../SSEPanel';

class MockEventSource {
  url: string;
  readyState: number;
  onopen: ((event: Event) => void) | null;
  onerror: ((event: Event) => void) | null;
  onmessage: ((event: MessageEvent) => void) | null;
  private listeners: Map<string, ((event: MessageEvent) => void)[]>;
  
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSED = 2;
  
  constructor(url: string) {
    this.url = url;
    this.readyState = MockEventSource.CONNECTING;
    this.onopen = null;
    this.onerror = null;
    this.onmessage = null;
    this.listeners = new Map();
  }
  
  addEventListener(type: string, listener: (event: MessageEvent) => void) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, []);
    }
    this.listeners.get(type)!.push(listener);
  }
  
  removeEventListener(type: string, listener: (event: MessageEvent) => void) {
    const listeners = this.listeners.get(type);
    if (listeners) {
      const index = listeners.indexOf(listener);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }
  
  close() {
    this.readyState = MockEventSource.CLOSED;
  }
  
  simulateOpen() {
    this.readyState = MockEventSource.OPEN;
    if (this.onopen) {
      this.onopen(new Event('open'));
    }
  }
  
  simulateError() {
    this.readyState = MockEventSource.CLOSED;
    if (this.onerror) {
      this.onerror(new Event('error'));
    }
  }
  
  simulateMessage(data: string) {
    if (this.onmessage) {
      const event = new MessageEvent('message', { data });
      this.onmessage(event);
    }
  }
  
  simulateNamedEvent(eventType: string, data: string) {
    const listeners = this.listeners.get(eventType);
    if (listeners) {
      const event = new MessageEvent(eventType, { data });
      listeners.forEach(listener => listener(event));
    }
  }
}

describe('SSEPanel', () => {
  let mockEventSource: MockEventSource;
  let originalEventSource: any;
  
  beforeEach(() => {
    originalEventSource = global.EventSource;
    (global as any).EventSource = class {
      constructor(url: string) {
        mockEventSource = new MockEventSource(url);
        return mockEventSource;
      }
      static CONNECTING = MockEventSource.CONNECTING;
      static OPEN = MockEventSource.OPEN;
      static CLOSED = MockEventSource.CLOSED;
    };
  });
  
  afterEach(() => {
    global.EventSource = originalEventSource;
  });
  
  it('renders with connecting status initially', () => {
    render(<SSEPanel correlationId="test_123" />);
    
    expect(screen.getByText('connecting')).toBeInTheDocument();
    expect(screen.getByText(/Waiting for events/)).toBeInTheDocument();
  });
  
  it('updates status to open when connection opens', async () => {
    render(<SSEPanel correlationId="test_456" />);
    
    mockEventSource.simulateOpen();
    
    await waitFor(() => {
      expect(screen.getByText('open')).toBeInTheDocument();
    });
  });
  
  it('displays error status on connection error', async () => {
    render(<SSEPanel correlationId="test_789" />);
    
    mockEventSource.simulateError();
    
    await waitFor(() => {
      expect(screen.getByText('error')).toBeInTheDocument();
    });
  });
  
  it('renders received events in list', async () => {
    render(<SSEPanel correlationId="test_events" />);
    
    mockEventSource.simulateOpen();
    
    const eventData = JSON.stringify({
      event: 'test_event',
      data: { message: 'hello' }
    });
    
    mockEventSource.simulateMessage(eventData);
    
    await waitFor(() => {
      expect(screen.getByText(/test_event/)).toBeInTheDocument();
      expect(screen.getByText(/hello/)).toBeInTheDocument();
    });
  });
  
  it('handles named events via addEventListener', async () => {
    render(<SSEPanel correlationId="test_named" />);
    
    mockEventSource.simulateOpen();
    
    const eventData = JSON.stringify({
      event: 'model_selected',
      data: { model: 'gpt-4o' }
    });
    
    mockEventSource.simulateNamedEvent('model_selected', eventData);
    
    await waitFor(() => {
      expect(screen.getByText(/model_selected/)).toBeInTheDocument();
      expect(screen.getByText(/gpt-4o/)).toBeInTheDocument();
    });
  });
  
  it('displays event payload as pretty JSON', async () => {
    render(<SSEPanel correlationId="test_json" />);
    
    mockEventSource.simulateOpen();
    
    const eventData = JSON.stringify({
      event: 'analysis_start',
      data: { 
        models: ['gpt-4o', 'claude-3-5-sonnet-20241022'],
        timestamp: '2025-01-15T12:00:00Z'
      }
    });
    
    mockEventSource.simulateMessage(eventData);
    
    await waitFor(() => {
      const eventElement = screen.getByText(/analysis_start/);
      expect(eventElement).toBeInTheDocument();
      
      const container = eventElement.closest('li');
      expect(container?.textContent).toContain('gpt-4o');
      expect(container?.textContent).toContain('claude-3-5-sonnet-20241022');
    });
  });
  
  it('constructs correct EventSource URL with correlation_id', () => {
    const correlationId = 'test_url_123';
    render(<SSEPanel correlationId={correlationId} />);
    
    expect(mockEventSource.url).toContain(`correlation_id=${encodeURIComponent(correlationId)}`);
  });
  
  it('uses custom title when provided', () => {
    const customTitle = 'My Custom Event Stream';
    render(<SSEPanel correlationId="test_title" title={customTitle} />);
    
    expect(screen.getByText(customTitle)).toBeInTheDocument();
  });
  
  it('uses default title when not provided', () => {
    render(<SSEPanel correlationId="test_default_title" />);
    
    expect(screen.getByText('Live Orchestrator Events')).toBeInTheDocument();
  });
  
  it('limits events to maxEvents prop', async () => {
    const maxEvents = 3;
    render(<SSEPanel correlationId="test_max" maxEvents={maxEvents} />);
    
    mockEventSource.simulateOpen();
    
    for (let i = 0; i < 10; i++) {
      const eventData = JSON.stringify({
        event: `event_${i}`,
        data: { index: i }
      });
      mockEventSource.simulateMessage(eventData);
    }
    
    await waitFor(() => {
      const eventItems = screen.getAllByRole('listitem');
      expect(eventItems.length).toBeLessThanOrEqual(maxEvents);
    });
  });
  
  it('handles invalid correlation_id gracefully', () => {
    render(<SSEPanel correlationId="" />);
    
    expect(screen.getByText('error')).toBeInTheDocument();
  });
  
  it('closes EventSource on unmount', () => {
    const { unmount } = render(<SSEPanel correlationId="test_unmount" />);
    
    const closeSpy = jest.spyOn(mockEventSource, 'close');
    
    unmount();
    
    expect(closeSpy).toHaveBeenCalled();
  });
});
