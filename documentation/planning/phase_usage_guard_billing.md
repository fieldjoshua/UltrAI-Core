# Phase X – Usage-Guard & Billing Readiness

_(tracked per RULES.md action-plan conventions)_

## Owner

`multi-provider-model-troubleshooting`

## Goal

Introduce hard/soft limits, cost ceilings, and rate-limits so that Ultra Synthesis can be safely monetised without runaway token usage or storage costs.

## Tasks

1. **Middleware – limits_middleware.py**
   • Add prompt/attachment size checks (8 k token / 100 KB text / 10 MB file).
   • Return HTTP 413 on breach with JSON error.

2. **RateLimiter extension**
   • Track tokens & USD cost.
   • Enforce per-request ($1) and daily user ceiling ($5).
   • Global monthly budget alert at 80 %.

3. **Concurrency & frequency**
   • Free = 30 req/h (burst 5/10 s)
   • Paid = 300 req/h
   • Max 3 concurrent pipelines.

4. **Content moderation**
   • Call provider moderation API; fail on disallowed categories.
   • Regex block obvious PII / secrets.

5. **Retention**
   • Auto-expire S3 uploads and DB records after 30 days.

6. **Frontend UX**
   • Token counter & soft-cap colour warning.
   • File-picker size notice.
   • Usage bar: "X tokens used today / Y remaining".

7. **Automated tests**
   • Oversize prompt ⇒ 413
   • 20 MB file ⇒ 413
   • 4 000 rapid req ⇒ 429
   • Exceed cost ⇒ 402.

8. **Billing tiers**
   • Free trial 200 k tokens.
   • Starter $19/mo → 2 M tokens.
   • Pro $99/mo → 15 M tokens & 32 k context.

## Exit criteria

• All new limits enforced and covered by CI tests.
• LIVE_ONLINE test extended with over-limit scenarios (expect failures).
• Documentation & UI reflect new limits and pricing.
