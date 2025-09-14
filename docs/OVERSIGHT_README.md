# UltrAI Oversight & Collaboration README

## Purpose
This README codifies policies and procedures for collaboration between Claude-1 (Implementation AI) and UltrAI (Oversight AI). It defines roles, signals, gates, review cadence, and documentation artifacts for reliable delivery.

## Roles
- **Claude-1 (Implementation AI)**: Owns core implementation tasks, coding, and primary PRs.
- **UltrAI (Oversight AI)**: Owns planning, review, guardrails, and bounded one-offs.

## Communication Signals
Use clear headers in messages and artifacts:
- `[PLAN]` Plan-of-Record updates
- `[CLAUDE_DO]` Assign core task to Claude-1
- `[ULTRA_DO]` Assign one-off/support task to UltrAI
- `[STATUS]` Status updates
- `[REVIEW]` Code review / verification request
- `[BLOCKER]` Blocker, risk, or dependency
- `[COMPLETE]` Task completion

## Push Gates (Must Pass Before Push/Merge)
1. Local tests pass with documented commands and outputs
2. Security checks executed:
   - Dependency audit (pip/npm)
   - Secret/regex scan
   - Basic injection/XSS surface checks for UI/API changes
3. Model availability policy: ≥2 healthy models online; single-model fallback disabled
4. CORS and environment variables verified for target environment

## Review Cadence
- After first working PR
- After integration across components
- Pre-deploy
Each `[REVIEW]` includes: PR links, test evidence, endpoint curls, and any security outputs.

## Drift Prevention Protocol
If off track, explicitly state:
“I'm getting off track. Returning to [ORIGINAL_TASK]”.
No refactors/optimizations/features unless requested. Single-task focus.

## Artifacts
- `AI_COLLABORATION_PROTOCOL.md`: roles, communication formats
- `ACTIVE_TASKS.md`: task board, owners, statuses, comms log
- `DELEGATION_001_SECURITY_AUDIT.md` (example delegation): expected outputs and evidence

## Checkpoints in Orchestration (Backend Policy)
- Config (in `app/config.py`, names may vary):
  - `MINIMUM_MODELS_REQUIRED = 2`
  - `ENABLE_SINGLE_MODEL_FALLBACK = False`
  - `CHECKPOINTS_ENABLED = True`
  - `CHECKPOINT_TIMEOUT_SECONDS = 30`
  - Suggested: `CHECKPOINT_PARALLEL_WAIT`, `CHECKPOINT_LOG_VERBOSE`, `CHECKPOINT_RETRY_ONCE`
- Gates inserted in pipeline:
  - `initial_sync` after initial responses
  - `peer_sync` after peer review
  - `final_sync` before ultra synthesis
- On failure: structured `PipelineResult` with message and checkpoint report; return partials if policy allows.

## Documentation Quality Bar
- Acceptance criteria must be measurable and testable
- Commands provided are copy-paste runnable
- Any config change lists exact keys and target services

## Evidence Requirements
- Paste test outputs (summarized) and link to full logs if large
- Include `curl` verifications for key endpoints (e.g., `/api/available-models`, `/api/orchestrator/status`)
- Note environment (local/staging/prod) and API base URL used

## Operating Procedure
1. `[PLAN]` Post plan-of-record and acceptance criteria
2. `[CLAUDE_DO]` Assign core task(s) to Claude-1
3. `[ULTRA_DO]` Assign bounded one-off(s) to UltrAI
4. Implementation → tests → security checks → evidence
5. `[REVIEW]` Submit evidence; Oversight signs off
6. Push/merge when gates satisfied

## Appendix: Local Test Notes
- Frontend dev (example): `VITE_API_URL=<API> VITE_API_MODE=prod npm run dev`
- Backend: run uvicorn with required env (JWT secrets, ENVIRONMENT)
- Verify model endpoints:
  - `/api/available-models?healthy_only=true`
  - `/api/orchestrator/status`
