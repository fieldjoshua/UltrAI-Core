## Focus Declaration

- I understand our current project goal is <describe the current goal>.
- These changes work toward this goal by: <state the concrete impact>.

## Summary

- Scope:
- Risk level:
- Related issues/labels: (include `aux` / `aux-ok` when applicable)

## Editor Checklist (Pre‑Merge)

- [ ] Gating intact (3 models + Big 3 providers) with consistent 503 payload
- [ ] No cost/billing fields in API or UI
- [ ] SSE events use the documented names/payload
- [ ] Wizard enforces health gating
- [ ] Changes align with DFD constraints above

## Notes for Aux Models (if labeled `aux`)

- Default scope allowed: tests / docs / CI / monitoring
- Core logic changes require `aux-ok`
- One-task lock; keep PR focused and within timebox

## Summary

- Focus Declaration
  - I understand our current project goal is: <fill>
  - These changes work toward this goal by: <fill>

## Pre-Merge Checklist

- [ ] Gating intact (3 models + Big 3) and consistent 503 payload
- [ ] No cost/billing fields added (API or UI)
- [ ] SSE event names unchanged and schema respected
- [ ] Logs redact secrets; no keys printed
- [ ] CI: Staging Big 3 smoke passed
- [ ] Auxiliary model guardrails observed (PR-only, one-task, timebox, Focus Declaration)
- [ ] Docs updated if policy/contract changed (AI_EDITORS_GUIDE.md / API reference)

## Risk & Rollback

- Risk assessment
- Rollback plan

