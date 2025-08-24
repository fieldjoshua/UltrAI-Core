# P0/P1 Work Tracking and Ownership

## P0 (Me)
1) CORS/CSP lockdown
- AC: prod CORS allows only Vercel+Render; CSP connect-src includes https/wss for both; no wildcards in prod.

2) Structured logging + correlation IDs
- AC: middleware sets `X-Request-ID`; adapters log with requestId; logs scrub PII.

3) SSE streaming on /api/analyze
- AC: implements `SSE_AND_REQUEST_ID_SPEC.md`; non-stream mode unchanged; e2e demo works.

4) Route hygiene + DB ping
- AC: single /api prefix across routers; add `/api/db/ping` (SELECT 1) guarded by auth.

5) CI smoke tests
- AC: script to hit all OpenAPI paths + DB ping; runs in CI on PR; fails on non-2xx (except admin).

## P1 (Claude Code)
1) Auth & rate limiting
- AC: ENABLE_AUTH=true in prod; /api/admin/* and /api/debug/* require auth; per-user/API-key limiter.

2) Secret rotation & scanning
- AC: rotate exposed keys; add secret scanning job in CI; prevent exposure to FE build.

3) Resilience patterns
- AC: circuit breakers + bounded retries with jitter; provider timeouts tuned per vendor.

4) Smart model selection
- AC: folds availability + cost/latency into selection; adds tests.

5) Observability
- AC: OpenTelemetry traces; custom metrics for stage durations, tokens, cost.

## Coordination
- Contract: `documentation/deliverables/SSE_AND_REQUEST_ID_SPEC.md`
- Labels: `P0`, `P1`, `security`, `resilience`, `observability`.
