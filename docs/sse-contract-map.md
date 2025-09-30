### SSE contract map (events, payloads, and sequencing)

Source files
- Publisher: `app/services/sse_event_bus.py`
  - Frame format: `event: <name>\n` + `data: {"event": "<name>", "data": <payload>}\n\n`
  - Heartbeat: `data: {"event": "heartbeat"}\n\n` (no `event:` line)
- Emitters: `app/routes/orchestrator_minimal.py`, `app/services/orchestration_service.py`
- Consumer: `frontend/src/components/panels/SSEPanel.tsx`

Endpoint
- `GET /orchestrator/events?correlation_id=<id>` returns `text/event-stream`
- Initial frame is a named `connected` event

Named events and typical payloads (data.data)
- `connected`: `{}`
- `analysis_start`: `{ models: string[] }`
- `initial_start`: `{}`
- `model_selected`: `{ model: string }`
- `stage_started`: `{ stage: "peer_review_and_revision", models?: string[] } | { stage: "ultra_synthesis", synthesis_model: string }`
- `stage_completed`: `{ stage: string, success: boolean }`
- `model_completed`: `{ model: string }`
- `pipeline_complete`: `{}`
- `service_unavailable`: `{ error: "SERVICE_UNAVAILABLE", message?: string }`
- `heartbeat`: (no `event:` line, arrives as default message with `{ event: "heartbeat" }`)

Sequencing (typical)
1. `connected`
2. `analysis_start`
3. `model_selected` (repeat per selected model)
4. `initial_start`
5. `stage_started` (peer review)
6. `stage_completed` (peer review)
7. `stage_started` (ultra synthesis)
8. `stage_completed` (ultra synthesis)
9. `model_completed` (repeat)
10. `pipeline_complete`

Client handling expectations
- `SSEPanel` listens to default messages and the following named events: `connected`, `analysis_start`, `initial_start`, `model_selected`, `model_completed`, `pipeline_complete`, `service_unavailable`.
- Clients should parse `JSON.parse(ev.data)` and read `payload.event` and `payload.data`.
- Heartbeats may arrive without `event:`; treat as keepalive.

Error handling
- If a 503 occurs due to provider readiness, expect `service_unavailable` followed by HTTP error from the request path, not from SSE.
- Clients should surface `service_unavailable.data` message to the user.


