# AI Editors Guide: UltrAI Orchestration Guardrails (2025‑09‑17)

This guide memorializes non‑negotiable rules to keep edits aligned.

## Multi‑Model Gating (Production)
- UltrAI is online only when:
  - `MINIMUM_MODELS_REQUIRED = 3`
  - `REQUIRED_PROVIDERS = [openai, anthropic, google]`
  - All are healthy; no single‑model fallback in prod
- Implemented in:
  - `app/config.py`
  - `app/routes/orchestrator_minimal.py` (status/analyze/stream)
  - `app/services/orchestration_service.py::run_pipeline` (preflight)

## 503 Payload Shape (When Not Ready)
Return HTTP 503 with:
```json
{
  "error": "SERVICE_UNAVAILABLE",
  "message": "...",
  "details": {
    "models_required": 3,
    "models_available": 0,
    "required_providers": ["openai","anthropic","google"],
    "providers_present": [],
    "service_status": "degraded"
  }
}
```

## No‑Cost Policy (Current Phase)
- Do NOT compute/return cost/price/billing fields
- Frontend: do NOT render pricing/estimates in Wizard
- Internal tokens/metrics allowed for logs only

## SSE Event Schema (Stream)
- Event names: `stage_started`, `model_completed`, `stage_completed`, `synthesis_chunk`, `error`
- Payload base: `{ stage, provider?, model?, latency_ms?, tokens?, data? }`

## Frontend UX Gating
- Wizard (`frontend/src/components/CyberWizard.tsx`):
  - Show health banner when not ready
  - Disable start/initialize actions until ready

## Edit Checklist (Before Merging)
- Keep the gate intact (3 models + Big 3 providers)
- Preserve 503 payload shape exactly
- No cost fields leak into responses/UI
- Maintain SSE names/payloads

If a change needs to alter any rule here, update this guide in the same PR.
