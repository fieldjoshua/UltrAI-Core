# SSE Events Documentation

Server-Sent Events (SSE) provide real-time updates during orchestration pipeline execution.

## Endpoint

```
GET /orchestrator/events?correlation_id={correlation_id}
```

## Connection Flow

1. Client initiates SSE connection with `correlation_id`
2. Server immediately sends `connected` event
3. During pipeline execution, named events are published
4. Heartbeat events sent every 15 seconds to keep connection alive
5. Connection closes when client disconnects or pipeline completes

## Event Format

All events follow the SSE specification:

```
event: {event_name}
data: {"event": "{event_name}", "data": {...}}

```

## Event Types

### connected

Sent immediately upon SSE connection establishment.

**Payload:**
```json
{
  "event": "connected"
}
```

**When:** Connection opens

---

### analysis_start

Sent when an analysis request begins processing.

**Payload:**
```json
{
  "event": "analysis_start",
  "data": {
    "models": ["gpt-4o", "claude-3-5-sonnet-20241022", "gemini-1.5-pro"]
  }
}
```

**When:** `/orchestrator/analyze` endpoint receives request

---

### initial_start

Sent when the initial response stage begins.

**Payload:**
```json
{
  "event": "initial_start",
  "data": {}
}
```

**When:** Initial model response generation starts

---

### model_selected

Sent for each model selected for the analysis (emitted once per model).

**Payload:**
```json
{
  "event": "model_selected",
  "data": {
    "model": "gpt-4o"
  }
}
```

**When:** Before pipeline execution, once per selected model

---

### stage_started

Sent when a pipeline stage begins execution.

**Payload:**
```json
{
  "event": "stage_started",
  "data": {
    "stage": "peer_review_and_revision"
  }
}
```

**When:** Start of each pipeline stage (initial_response, peer_review_and_revision, ultra_synthesis)

---

### stage_completed

Sent when a pipeline stage completes successfully.

**Payload:**
```json
{
  "event": "stage_completed",
  "data": {
    "stage": "initial_response",
    "duration_seconds": 3.42
  }
}
```

**When:** End of each pipeline stage

---

### model_completed

Sent when a specific model completes its processing.

**Payload:**
```json
{
  "event": "model_completed",
  "data": {
    "model": "claude-3-5-sonnet-20241022"
  }
}
```

**When:** After each model finishes processing (emitted at analysis completion)

---

### pipeline_complete

Sent when the entire orchestration pipeline finishes.

**Payload:**
```json
{
  "event": "pipeline_complete",
  "data": {}
}
```

**When:** Pipeline execution completes (before final HTTP response sent)

---

### analysis_complete

Sent when analysis completes with results.

**Payload:**
```json
{
  "event": "analysis_complete",
  "data": {
    "processing_time": 12.45,
    "stages": ["initial_response", "peer_review_and_revision", "ultra_synthesis"]
  }
}
```

**When:** After pipeline results are formatted and ready to return

---

### service_unavailable

Sent when the service encounters a fatal error (insufficient models/providers).

**Payload:**
```json
{
  "event": "service_unavailable",
  "data": {
    "error": "SERVICE_UNAVAILABLE",
    "message": "UltraAI requires at least 3 models to proceed"
  }
}
```

**When:** Service cannot fulfill request due to configuration/availability issues

---

### heartbeat

Sent periodically to keep the SSE connection alive.

**Payload:**
```json
{
  "event": "heartbeat"
}
```

**When:** Every 15 seconds (configurable)

---

## Typical Event Sequence

### Successful Analysis

```
1. connected
2. analysis_start
3. model_selected (×3)
4. initial_start
5. stage_started (initial_response)
6. stage_completed (initial_response)
7. stage_started (peer_review_and_revision)
8. stage_completed (peer_review_and_revision)
9. stage_started (ultra_synthesis)
10. stage_completed (ultra_synthesis)
11. pipeline_complete
12. model_completed (×3)
13. analysis_complete
```

### Failed Analysis

```
1. connected
2. analysis_start
3. model_selected (×2)
4. initial_start
5. stage_started (initial_response)
6. service_unavailable
```

## Implementation Details

### Backend

- **Event Bus:** `app/services/sse_event_bus.py` (`SSEEventBus` class)
- **Route:** `app/routes/orchestrator_minimal.py` (`/orchestrator/events`)
- **Publishing:** Events published via `sse_event_bus.publish(correlation_id, event_name, data)`

### Frontend

- **Component:** `frontend/src/components/panels/SSEPanel.tsx`
- **API:** Native browser `EventSource` API
- **Connection:** Auto-reconnect on error, closes on unmount

## Usage Example (Frontend)

```typescript
const eventSource = new EventSource(
  `/api/orchestrator/events?correlation_id=${correlationId}`
);

eventSource.addEventListener('model_selected', (event) => {
  const data = JSON.parse(event.data);
  console.log('Model selected:', data.data.model);
});

eventSource.addEventListener('analysis_complete', (event) => {
  const data = JSON.parse(event.data);
  console.log('Analysis complete in', data.data.processing_time, 'seconds');
  eventSource.close();
});
```

## Testing

Integration test: `tests/integration/test_sse_events.py`

```bash
pytest tests/integration/test_sse_events.py -v
```

## Notes

- Events are **ephemeral** (not persisted across server restarts)
- Queue size: 1000 events per `correlation_id`
- Old events are dropped when queue is full
- Connection timeout handled by browser (typically 45-60s)
- Heartbeats prevent connection closure during long operations
