import React, { useEffect, useMemo, useRef, useState } from 'react';

interface SSEPanelProps {
  correlationId: string;
  title?: string;
  maxEvents?: number;
}

const SSEPanel: React.FC<SSEPanelProps> = ({
  correlationId,
  title = 'Live Orchestrator Events',
  maxEvents = 100,
}) => {
  const [events, setEvents] = useState<
    Array<{ time: string; event: string; payload: any }>
  >([]);
  const [status, setStatus] = useState<
    'connecting' | 'open' | 'closed' | 'error'
  >('connecting');
  const esRef = useRef<EventSource | null>(null);

  const apiBase = useMemo(
    () => (import.meta as any).env?.VITE_API_URL || '/api',
    []
  );

  useEffect(() => {
    // Basic validation for correlationId to avoid malformed URLs
    const safeId = String(correlationId || '').replace(/[^a-zA-Z0-9_\-]/g, '');
    if (!safeId) {
      setStatus('error');
      return;
    }

    const url = `${apiBase}/orchestrator/events?correlation_id=${encodeURIComponent(safeId)}`;
    const es = new EventSource(url, { withCredentials: false });
    esRef.current = es;

    es.onopen = () => setStatus('open');
    es.onerror = () => setStatus('error');
    es.onmessage = (msg: MessageEvent) => {
      try {
        // If server uses named events, they arrive via addEventListener; also handle default message
        const data = JSON.parse(msg.data);
        const evtName = (data && data.event) || 'message';
        setEvents(prev => {
          const next = [
            {
              time: new Date().toISOString(),
              event: evtName,
              payload: data,
            },
            ...prev,
          ];
          return next.slice(0, maxEvents);
        });
      } catch (_e) {
        // Fall back to raw text
        setEvents(prev =>
          [
            {
              time: new Date().toISOString(),
              event: 'message',
              payload: msg.data,
            },
            ...prev,
          ].slice(0, maxEvents)
        );
      }
    };

    // Also listen to a few known named events
    const namedEvents = [
      'connected',
      'analysis_start',
      'initial_start',
      'model_selected',
      'model_completed',
      'pipeline_complete',
      'service_unavailable',
    ];
    namedEvents.forEach(name => {
      es.addEventListener(name, (ev: MessageEvent) => {
        try {
          const data = JSON.parse(ev.data);
          setEvents(prev =>
            [
              { time: new Date().toISOString(), event: name, payload: data },
              ...prev,
            ].slice(0, maxEvents)
          );
        } catch (_e) {
          setEvents(prev =>
            [
              { time: new Date().toISOString(), event: name, payload: ev.data },
              ...prev,
            ].slice(0, maxEvents)
          );
        }
      });
    });

    return () => {
      setStatus('closed');
      try {
        es.close();
      } catch {
        /* ignore */
      }
      esRef.current = null;
    };
  }, [apiBase, correlationId, maxEvents]);

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
      <div className="px-4 py-2 border-b flex items-center justify-between">
        <div className="text-sm font-semibold text-gray-800">{title}</div>
        <div
          className={`text-xs ${status === 'open' ? 'text-green-600' : status === 'error' ? 'text-red-600' : 'text-gray-500'}`}
        >
          {status}
        </div>
      </div>
      <div className="p-3 max-h-64 overflow-auto text-xs font-mono leading-snug">
        {events.length === 0 ? (
          <div className="text-gray-500">
            Waiting for events on correlation_id: {correlationId}
          </div>
        ) : (
          <ul className="space-y-2">
            {events.map((e, idx) => (
              <li key={idx} className="border-b pb-2 sse-item-enter">
                <div className="text-gray-600">
                  [{e.time}]{' '}
                  <span className="font-semibold text-gray-800">{e.event}</span>
                </div>
                <pre className="whitespace-pre-wrap break-words text-gray-800">
                  {typeof e.payload === 'string'
                    ? e.payload
                    : JSON.stringify(e.payload, null, 2)}
                </pre>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default SSEPanel;
