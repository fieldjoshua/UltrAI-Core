# Streaming Orchestration Responses

## Overview

The UltraAI orchestrator now supports streaming responses using Server-Sent Events (SSE), enabling real-time updates as the multi-stage pipeline processes queries. This feature provides immediate feedback to users and enables more responsive user interfaces.

## Endpoint

### POST `/api/orchestrator/analyze/stream`

Initiates a streaming analysis session that sends events as the pipeline progresses.

#### Request Body

```json
{
  "query": "What are the key principles of quantum computing?",
  "selected_models": ["gpt-4", "claude-3-5-sonnet"],
  "stream_stages": ["synthesis_chunks", "model_responses"],
  "chunk_size": 50,
  "options": {
    "temperature": 0.7
  }
}
```

#### Parameters

- `query` (required): The text to analyze
- `selected_models` (optional): List of models to use (defaults to auto-selection)
- `stream_stages` (optional): Which stages to stream
  - `"all"`: Stream all events
  - `"synthesis_chunks"`: Stream synthesis in chunks (default)
  - `"model_responses"`: Stream individual model responses
- `chunk_size` (optional): Approximate words per synthesis chunk (default: 50)
- `options` (optional): Additional pipeline options

#### Response

Returns a `text/event-stream` with Server-Sent Events. Each event follows this format:

```
data: {"event": "event_type", "sequence": 1, "timestamp": "2024-01-20T10:30:00Z", "data": {...}}

```

## Event Types

### Pipeline Events

#### `pipeline_start`
Emitted when the pipeline begins processing.

```json
{
  "event": "pipeline_start",
  "data": {
    "query": "truncated query...",
    "selected_models": ["gpt-4", "claude-3"],
    "total_stages": 3,
    "options": {}
  }
}
```

#### `pipeline_complete`
Emitted when the entire pipeline finishes successfully.

```json
{
  "event": "pipeline_complete",
  "data": {
    "total_stages": 3,
    "success": true
  }
}
```

#### `pipeline_error`
Emitted if the pipeline encounters a fatal error.

```json
{
  "event": "pipeline_error",
  "data": {
    "error": "No valid models provided"
  }
}
```

### Stage Events

#### `stage_start`
Emitted when a pipeline stage begins.

```json
{
  "event": "stage_start",
  "data": {
    "stage_name": "initial_response",
    "stage_index": 0,
    "total_stages": 3,
    "description": "Initial response generation from multiple models"
  }
}
```

#### `stage_complete`
Emitted when a stage completes successfully.

```json
{
  "event": "stage_complete",
  "data": {
    "stage_name": "peer_review_and_revision",
    "stage_index": 1,
    "success": true
  }
}
```

### Model Events

#### `model_start`
Emitted when a model begins processing.

```json
{
  "event": "model_start",
  "data": {
    "model": "gpt-4",
    "stage": "initial_response"
  }
}
```

#### `model_response`
Emitted when a model completes its response.

```json
{
  "event": "model_response",
  "data": {
    "model": "claude-3-5-sonnet",
    "response_text": "Quantum computing leverages...",
    "tokens_used": {
      "prompt_tokens": 150,
      "completion_tokens": 500
    },
    "response_time": 2.3
  }
}
```

### Synthesis Events

#### `synthesis_start`
Emitted when Ultra Synthesis™ begins.

```json
{
  "event": "synthesis_start",
  "data": {
    "models_available": ["gpt-4", "claude-3"]
  }
}
```

#### `synthesis_chunk`
Emitted for each chunk of the synthesis (if streaming enabled).

```json
{
  "event": "synthesis_chunk",
  "data": {
    "chunk_text": "Based on the comprehensive analysis...",
    "chunk_index": 0,
    "model_used": "claude-3-5-sonnet",
    "total_chunks": 10
  }
}
```

#### `synthesis_complete`
Emitted when synthesis finishes.

```json
{
  "event": "synthesis_complete",
  "data": {
    "model_used": "claude-3-5-sonnet",
    "total_length": 2500
  }
}
```

## Client Implementation

### JavaScript/TypeScript Example

```typescript
const eventSource = new EventSource('/api/orchestrator/analyze/stream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    query: "Explain quantum computing",
    stream_stages: ["synthesis_chunks"]
  })
});

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.event) {
    case 'pipeline_start':
      console.log('Analysis started...');
      break;
      
    case 'synthesis_chunk':
      // Append chunk to display
      appendToOutput(data.data.chunk_text);
      break;
      
    case 'pipeline_complete':
      console.log('Analysis complete!');
      eventSource.close();
      break;
      
    case 'pipeline_error':
      console.error('Error:', data.data.error);
      eventSource.close();
      break;
  }
};

eventSource.onerror = (error) => {
  console.error('SSE Error:', error);
  eventSource.close();
};
```

### Python Example

```python
import requests
import json

response = requests.post(
    'https://api.example.com/api/orchestrator/analyze/stream',
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    },
    json={
        'query': 'Explain quantum computing',
        'stream_stages': ['synthesis_chunks']
    },
    stream=True
)

for line in response.iter_lines():
    if line and line.startswith(b'data: '):
        event_data = json.loads(line[6:])
        
        if event_data['event'] == 'synthesis_chunk':
            print(event_data['data']['chunk_text'], end='', flush=True)
        elif event_data['event'] == 'pipeline_complete':
            print("\n\nAnalysis complete!")
            break
```

## Performance Considerations

1. **Chunk Size**: Larger chunks reduce events but may feel less responsive
2. **Buffering**: Some proxies/CDNs buffer SSE; use `X-Accel-Buffering: no` header
3. **Timeouts**: Long-running connections may timeout; implement reconnection logic
4. **Concurrent Streams**: Limit concurrent streams per user to prevent resource exhaustion

## Configuration

### Environment Variables

- `STREAMING_ENABLED`: Enable/disable streaming globally (default: true)
- `DEFAULT_CHUNK_SIZE`: Default synthesis chunk size (default: 50)
- `MAX_CONCURRENT_STREAMS`: Maximum concurrent streams per user (default: 5)

### Per-Request Options

Configure streaming behavior per request:

```json
{
  "stream_stages": ["all"],           // Stream everything
  "chunk_size": 100,                  // Larger chunks
  "options": {
    "synthesis_streaming": false      // Disable synthesis chunking
  }
}
```

## Error Handling

Streaming errors are sent as events:

```json
{
  "event": "stage_error",
  "data": {
    "stage_name": "initial_response",
    "error": "OpenAI API rate limit exceeded"
  }
}
```

Clients should:
1. Listen for error events
2. Implement automatic reconnection with backoff
3. Provide fallback to non-streaming endpoint

## Migration Guide

### From Non-Streaming to Streaming

1. Change endpoint from `/analyze` to `/analyze/stream`
2. Replace JSON response parsing with SSE event handling
3. Accumulate synthesis chunks instead of receiving complete text
4. Update UI to show progressive updates

### Backward Compatibility

The non-streaming endpoint remains available at `/api/orchestrator/analyze` for clients that don't support SSE or prefer batch responses.

## Future Enhancements

1. **WebSocket Support**: Alternative to SSE for bidirectional communication
2. **Partial Model Responses**: Stream tokens as models generate them
3. **Progress Indicators**: Percentage completion for each stage
4. **Cancellation**: Allow clients to cancel in-progress analyses
5. **Response Caching**: Cache and replay streams for identical queries