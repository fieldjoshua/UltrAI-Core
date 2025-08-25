# SSE Event Schema, Correlation IDs, and Cost Estimate Contract

## Correlation ID
- Header: `X-Request-ID`
- Generation: backend middleware generates UUIDv4 if absent; echoes back in all responses and SSE `event: meta`.
- Propagation: LLM adapter calls include `x-request-id` in logs/metrics.

## SSE Channel (analysis)
- Endpoint: `POST /api/analyze` with `Accept: text/event-stream` OR query `?stream=true`.
- Events (ordered):
  - `event: meta` data: `{ "requestId": string, "model": string, "receivedAt": ISO8601 }`
  - `event: status` data: `{ "stage": "preparing" | "analyzing" | "synthesis", "percent": 0..100 }`
  - `event: token` data: `{ "text": string }` (repeated)
  - `event: cost` data: `{ "inputTokens": number, "outputTokens": number, "estimatedCostUsd": number }`
  - `event: error` data: `{ "message": string, "code"?: string }` (terminal)
  - `event: done` data: `{ "completedAt": ISO8601 }` (terminal)
- Keep-alive: comment lines every 15s: `: ping`.
- Close on error/done.

## Cost Estimate Payload
- Endpoint: `POST /api/analyze?estimate=true` OR `event: cost` during stream.
- Shape:
```
{
  "model": "gpt-4o",
  "inputTokens": 1234,
  "outputTokens": 0,
  "unitCosts": { "inputPer1k": 0.005, "outputPer1k": 0.015 },
  "estimatedCostUsd": 0.00617,
  "capExceeded": false
}
```
- Cap logic: reject if projected exceeds per-request/user caps; include `capExceeded`.

## Error Contract
- JSON and SSE `event: error` share shape:
```
{ "requestId": string, "message": string, "code": "INVALID_INPUT" | "PROVIDER_TIMEOUT" | "RATE_LIMIT" | "INTERNAL" }
```

## Acceptance Criteria
- Middleware sets/echoes `X-Request-ID`.
- `/api/analyze` supports SSE with the events above; non-stream mode unchanged.
- Cost estimate available pre-run and during stream.
- Adapters log with requestId; retries bounded with jitter.

