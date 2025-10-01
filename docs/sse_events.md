# SSE Events Documentation

This document defines the Server-Sent Events (SSE) contract for the `/orchestrator/events` endpoint.

## Overview

The SSE stream provides real-time updates during orchestration pipeline execution. Events are published via the `sse_event_bus` and consumed by the frontend `SSEPanel` component.

## Event Format

All events follow the SSE specification with two fields:
- `event`: Event type identifier
- `data`: JSON payload containing event details

## Event Types

### Connection Events

#### `connected`
**Purpose**: Initial connection confirmation
**Payload**: `{"event": "connected"}`
**Triggered**: When client first connects to SSE stream

#### `heartbeat`
**Purpose**: Keep connection alive (sent every 15 seconds)
**Payload**: `{"event": "heartbeat"}`
**Triggered**: Periodic background task

### Analysis Lifecycle Events

#### `analysis_start`
**Purpose**: Analysis pipeline initiated
**Payload**: `{"models": ["model1", "model2", ...]}`
**Triggered**: When `/orchestrator/analyze` endpoint is called

#### `model_selected`
**Purpose**: Ultra synthesis model chosen
**Payload**: `{"model": "selected_model_name"}`
**Triggered**: After model selection for final synthesis

#### `initial_start`
**Purpose**: Initial response phase beginning
**Payload**: `{}`
**Triggered**: Before starting initial model queries

#### `stage_started`
**Purpose**: Pipeline stage initiated
**Payload**: `{"stage": "stage_name", "models": ["model1", ...]}`
**Triggered**: At start of each pipeline stage

#### `model_completed`
**Purpose**: Individual model completion
**Payload**: `{"model": "model_name", "stage": "current_stage"}`
**Triggered**: When a model finishes processing in current stage

#### `stage_completed`
**Purpose**: Pipeline stage finished
**Payload**: `{"stage": "stage_name", "models": ["model1", ...]}`
**Triggered**: When all models in a stage complete

#### `pipeline_complete`
**Purpose**: Entire pipeline finished successfully
**Payload**: `{"results": {...}}`
**Triggered**: When all pipeline stages complete successfully

### Error Events

#### `service_unavailable`
**Purpose**: Service or provider unavailable
**Payload**: `{"error": "error_message", "providers": [...]}`
**Triggered**: When required providers are unavailable

## Frontend Integration

The `SSEPanel` component listens for these events and displays them in real-time:

```typescript
// Event listeners are set up for known event types
const namedEvents = [
  'connected', 'analysis_start', 'initial_start',
  'model_selected', 'model_completed', 'pipeline_complete',
  'service_unavailable'
];

namedEvents.forEach(name => {
  es.addEventListener(name, (ev: MessageEvent) => {
    // Process event and update UI
  });
});
```

## Error Handling

- Connection errors trigger `status: 'error'`
- Malformed JSON in event data falls back to raw text display
- Queue overflow drops oldest events (max 1000 per correlation ID)

## Usage Example

```bash
# Subscribe to events for correlation_id "analysis_123"
curl -N "http://localhost:8000/api/orchestrator/events?correlation_id=analysis_123"
```

Expected output:
```
event: connected
data: {"event": "connected"}

event: analysis_start
data: {"event": "analysis_start", "data": {"models": ["gpt-4", "claude-3-opus"]}}

event: heartbeat
data: {"event": "heartbeat"}
```