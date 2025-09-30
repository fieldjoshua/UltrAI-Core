# GPT-5 Local Tasks — Documentation

## B3: Database URL Fallback
- Source: `app/database/session.py`
- Behavior:
  - Reads `DATABASE_URL` from environment; converts `postgres://` → `postgresql://`.
  - If unset, defaults to `sqlite:///./ultrai_dev.db` (development convenience).
  - On empty string, raises `ValueError("Invalid or empty DATABASE_URL")`.
  - For SQLite, uses `NullPool` and `check_same_thread=False`.
  - For Postgres/MySQL, uses `QueuePool` with pre-ping.
- Recommendation (production):
  - Set `DATABASE_URL` to managed Postgres (Render Postgres) and avoid SQLite.
  - Keep SQLite only for local dev and CI where persistence isn’t needed.

## C2: Required Environment Variables (APIs)
- Common (staging + prod APIs):
  - `RAG_ENABLED=false`
  - `MINIMUM_MODELS_REQUIRED=3`
  - `ENABLE_SINGLE_MODEL_FALLBACK=false`
  - `CORS_ORIGINS=<comma-separated-origins>`
- Staging API only:
  - `ALLOW_PUBLIC_ORCHESTRATION=true`
  - `JWT_SECRET=<secure-random-32+>`
  - `JWT_REFRESH_SECRET=<secure-random-32+>`
- Production API only:
  - `ALLOW_PUBLIC_ORCHESTRATION=false`
  - `DATABASE_URL=<postgres-url>`
- Provider keys (as applicable):
  - `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `HUGGINGFACE_API_KEY`

## C2: Required Environment Variables (Frontends)
- All UIs:
  - `VITE_RAG_ENABLED=false`
  - `VITE_API_URL=<api base>` (staging/prod)

## Notes
- Render dashboard updated to use `CORS_ORIGINS` (not `CORS_ALLOWED_ORIGINS`).
- Sentry: use `environment` in `sentry_sdk.init(...)`; set tags at runtime via `set_tag`.