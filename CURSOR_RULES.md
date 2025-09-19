# Cursor Rules — UltrAI Orchestration Guardrails

These rules are authoritative for AI editors in this repo. Keep changes aligned; update this file if any rule must change.

## Non‑Negotiable Runtime Policies
- Multi‑Model Gating (Production)
  - UltrAI must be online only when all are true:
    - MINIMUM_MODELS_REQUIRED = 3
    - REQUIRED_PROVIDERS = [openai, anthropic, google]
    - All required providers are healthy
  - No single‑model fallback in production.
  - Enforced in: `app/config.py`, `app/routes/orchestrator_minimal.py`, `app/services/orchestration_service.py::run_pipeline`.

- 503 Payload Consistency (When Not Ready)
  - Return HTTP 503 with payload:
    - error: "SERVICE_UNAVAILABLE"
    - message: string
    - details: { models_required: 3, models_available: int?, required_providers: string[], providers_present: string[], service_status: "degraded" }

- No‑Cost Policy (Current Phase)
  - Do NOT compute/return any cost/price/billing fields in API or UI.
  - Token usage may be logged internally but never exposed to end users.

- SSE Event Schema (Stream)
  - Event names: stage_started, model_completed, stage_completed, synthesis_chunk, error
  - Payload base: { stage, provider?, model?, latency_ms?, tokens?, data? }

- Frontend UX Gating
  - Wizard must show a health banner and disable start/initialize actions unless status.ready == true.

## Data Flow Diagram (DFD) — Logical Constraints (Authoritative Summary)
- External Entity: User — provides prompt, attachments (≤ 25MB), optional context (≤ 4000 tokens).
- Data Stores
  - D1 Configuration & Settings: API keys, timeouts, gating config.
  - D2 Prompt Library: Initial, Meta, UltrAI Mode prompts.
  - D3 Model Responses: Initial drafts, Peer drafts, Revised drafts, Raw synthesis.
  - D4 Logs & Metrics: Provenance/audit logs, metrics (no cost exposure).

- Process 1: User Input & Configuration (Wizard)
  - P1.1 Collect: prompt required; attachments ≤ 25MB; context ≤ 4000 tokens.
  - P1.2 Mode/Models: Only "Standard Synthesis"; model tiers: Auto/Premium/Balanced/Economy (Auto defers to P3.2/3.3).
  - P1.3 Modules: Only active modules selectable; coming‑soon greyed out.
  - P1.4 Validate: resolve module conflicts (Secure Mode disables Traceability; Encrypted Package limits to JSON/PDF; multi‑delivery → zip).

- Process 2: System Initialization & Readiness
  - Verify env: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY; MINIMUM_MODELS_REQUIRED=3; REQUIRED_PROVIDERS=[openai,anthropic,google]; ENABLE_SINGLE_MODEL_FALLBACK=false.
  - Check model health: ensure status.ready and ≥ 3 healthy including all required providers; else 503.

- Process 3: Input Processing & Model Allocation
  - P3.1 Normalize & Validate: size/token limits; apply prompt extraction fix to avoid "Unknown prompt".
  - P3.2 Complexity Score (Auto only): score = word_count/50 + attachment_count*10 + technical_terms*5.
  - P3.3 Allocate Models: pick by score/tier; TODAY safeguard must NOT override gating (no forced models in prod).

- Process 4: Orchestration Engine (3‑Stage)
  - P4.1 Initial (parallel): 500‑word default cap; log warning >5s, critical >10s.
  - P4.2 Validation: retry once; proceed without failed models; if <3 successful → abort with error (or skip P4.3 in dev per guard, not prod).
  - P4.3 Meta Round: only if ≥3 successful.
  - P4.4 UltrAI Mode: neutral synthesizer; use UltrAI prompt; consensus tagging; timeouts/fallbacks; alerts on low agreement/confidence.

- Process 5: Enhancement & Output Generation
  - Apply modules (Confidence/Traceability/Summarization/Formatting/Delivery/Redaction) per constraints; skip failed modules.

- Process 6: Output Delivery
  - Deliver final synthesis and module outputs; stream progress via SSE.

- Cross‑Cutting Fallbacks
  - Tier fallback chains must not violate gating/no‑cost policies.
  - Emergency paths are dev‑only and must be disabled in production.

## Editor Checklist (Pre‑Merge)
- [ ] Gating intact (3 models + Big 3 providers) with consistent 503 payload.
- [ ] No cost/billing fields in API or UI.
- [ ] SSE events use the documented names/payload.
- [ ] Wizard enforces health gating.
- [ ] Changes align with DFD constraints above.

Refer also to: `documentation/AI_EDITORS_GUIDE.md` for a compact spec AI tools can ingest.

## Lean Workflow Addendum (Efficiency without losing control)
- Auto-Go allowed for single-file ≤10-line diffs or docs/tests-only changes.
- Batch small related fixes; single status update for batch ≤50 lines.
- Todos reserved for multi-file or >15 min tasks.
- Confirmation thresholds: core logic >10 lines; tests/docs >50 lines.
- Parallel tool calls required for ≥3 independent lookups; optional for ≤2.
- Micro-refactors permitted (renames/typing/unused imports) when ≤15 lines and no behavior change.
- Memory citation only when policy alters behavior/output (e.g., staging override readiness).

## Focus Declaration (Minimal but mandatory)
- At the start of every task and in PR descriptions, include:
  - "I understand our current project goal is <X>."
  - "These changes work toward this goal by: <Y>."
- Limit to 1–2 lines; optimize for clarity, not verbosity.

## Loop Limiting Rules (Prevent spin; escalate)
- Caps
  - File edit retry cap: 2 per error class; on 3rd, stop and ask.
  - Linter correction cycles: 2 per file per session; on 3rd, request guidance.
  - Identical tool invocations: max 2; change input or pause on 3rd.
  - Deploy/status polling: 2 checks within 2 minutes; then wait/backoff.
  - HTTP 429/5xx: exponential backoff, max 2 retries; then mark blocked.
- Require a state change before repeating an action; note what changed.
- On cap reached: emit concise reason and proposed next action; ask for confirmation if needed.
