## Summary

Describe the change.

## Focus Declaration

- I understand our current project goal is: <describe the current goal>
- These changes work toward this goal by: <state the concrete impact>

## Checklist

- [ ] Policy changes included? If yes:
  - [ ] Bumped `version` in `ops/policies.yaml`
  - [ ] Included impact notes
  - [ ] CI policy-lint passes

- [ ] If Render/MCP related, confirm MCP-connected editor will execute changes

## Details

- Scope:
- Risk level:
- Related issues/labels: (include `aux` / `aux-ok` when applicable)

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

