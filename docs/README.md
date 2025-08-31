## UltrAI Skins, Environments, and Cursor Rules (2025)

### Overview
This document unifies the skin system, environment split, and Cursor collaboration rules so contributors can get up to speed fast.

### Environments
- **Staging** (branch: `main`, `VITE_APP_MODE=staging`) – active development; may be unstable.
- **Production** (branch: `production`, `VITE_APP_MODE=production`, `VITE_API_MODE=live`) – stable and user-facing.
- **Demo** (branch: `production`, `VITE_API_MODE=mock`) – production UI with mock API; safe for presentations.
- **Playground** (branches: `ultrai-play-*`, `VITE_APP_MODE=playground`, `VITE_API_MODE=mock`) – experiments/client demos; short‑lived.

### Skins
- Available: `night` (default), `afternoon`, `sunset`, `morning`.
- Default skin in all environments: `night`.
- Change skins at runtime via a floating `SkinSwitcher` component or by query param, e.g. `?skin=sunset`.

### Frontend Config (Vite)
Environment variables (examples):
```
# Staging
VITE_APP_MODE=staging
VITE_API_MODE=live
VITE_DEFAULT_SKIN=night

# Production
VITE_APP_MODE=production
VITE_API_MODE=live
VITE_DEFAULT_SKIN=night

# Demo
VITE_APP_MODE=production
VITE_API_MODE=mock
VITE_DEFAULT_SKIN=night

# Playground
VITE_APP_MODE=playground
VITE_API_MODE=mock
VITE_DEFAULT_SKIN=night
```

Recommended files to add in `frontend/src`:
- `config.ts` – exports `config` with `appMode`, `apiMode`, `defaultSkin`, `availableSkins` (reads from `import.meta.env`).
- `skins/index.ts` – dynamic CSS loader for `night`, `afternoon`, `sunset`, `morning`.
- `components/SkinSwitcher.tsx` – floating UI to switch skins; honors `?skin=...`.

### Render Services
- `ultrai-staging` → branch `main` → `https://staging-ultrai.onrender.com`
- `ultrai-prod` → branch `production` → `https://ultrai.com`
- `ultrai-demo` → branch `production`, override `VITE_API_MODE=mock` → `https://demo-ultrai.onrender.com`
- `ultrai-play-*` → branch `ultrai-play-*`, overrides `VITE_APP_MODE=playground` + `VITE_API_MODE=mock` → `https://ultrai-play-*.onrender.com`

### Cursor Rules (collaboration)
- Branches:
  - `main` → staging; all work happens here.
  - `production` → production; never commit directly; promote from `main` via merge/cherry‑pick.
  - `demo` → not a branch; uses production branch with `VITE_API_MODE=mock` in service config.
  - `ultrai-play-*` → playgrounds; short‑lived, no auto‑update from `main` (sync manually as needed).
- Workflow:
  - Do not commit directly to `production`.
  - Promote staging → production by PR/merge; deploying both `ultrai-prod` and `ultrai-demo`.
  - Clean up playground branches and services when finished.

### Git Flow Cheat Sheet
```bash
# Work in staging
git checkout main
git add -A
git commit -m "New feature"
git push origin main   # deploys ultrai-staging

# Promote staging → production
git checkout production
git merge --no-ff main
git push origin production   # deploys ultrai-prod and ultrai-demo

# Create a playground
git checkout -b ultrai-play-clientx-v1 main
git push origin ultrai-play-clientx-v1
# deploys ultrai-play-clientx-v1
```

### Naming
- Playgrounds: `ultrai-play-clientx-v1`, `ultrai-play-investorpitch`, etc. Include purpose and version when multiple demos exist.

### Summary
- Prod & Demo share the production branch; Demo uses mock API plumbing.
- Playground is a distinct mode for divergence.
- Skins are universal; default to `night` until all are fully styled.

For the full Cursor‑specific rules, see `docs/cursor-rules.md`.


