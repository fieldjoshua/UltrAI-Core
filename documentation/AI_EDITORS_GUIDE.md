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

## Lean Editor Workflow (Focus + Oversight)
- Auto-Go: skip pre-plan for single-file ≤10-line diffs or docs/tests-only changes
- Batch small fixes: one consolidated status for related edits ≤50 lines total
- Todos only for multi-file or >15 min tasks
- Large-diff confirm thresholds: >10 lines for core logic; >50 for tests/docs
- Parallel tool usage required for ≥3 independent lookups; optional for 1–2
- Micro-refactors allowed (renames/typing/unused imports) ≤15 lines, no behavior change
- Memory citation required only when policy materially affects behavior/output

CI/PR Oversight
- PR template checkboxes: gating/no-cost/SSE/log-redaction/secret-scan
- Staging smoke: Big 3 healthy, providers configured
- Regex scan: block cost/billing terms in frontend UI code
- SSE contract spot-check: event names present
