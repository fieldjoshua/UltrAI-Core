📘 UltrAI Cursor Rules

🔎 Branches
	•	main → Staging (active development, may be unstable).
	•	production → Production (stable, curated features only).
	•	demo → No branch — uses production branch but with mock API (VITE_API_MODE=mock).
	•	ultrai-play-* → Playground branches (short-lived demos/experiments).

⸻

🌐 Render Services
	•	ultrai-staging → branch main → https://staging-ultrai.onrender.com
	•	ultrai-prod → branch production → https://ultrai.com
	•	ultrai-demo → branch production, env override VITE_API_MODE=mock → https://demo-ultrai.onrender.com
	•	**ultrai-play-** → branch ultrai-play-, env override VITE_APP_MODE=playground+VITE_API_MODE=mock→https://ultrai-play-.onrender.com`

⸻

📝 Environments
	•	Staging (main + VITE_APP_MODE=staging) → active dev, live API.
	•	Production (production + VITE_APP_MODE=production + VITE_API_MODE=live) → stable, live users.
	•	Demo (production + VITE_API_MODE=mock) → prod UI, mock API, safe for presentations.
	•	Playground (ultrai-play-* + VITE_APP_MODE=playground + VITE_API_MODE=mock) → experiments/client demos.

⸻

🎨 Skins
	•	Current options: night (default), afternoon, sunset, morning.
	•	All environments default to night until others are fully styled.
	•	Skins can be toggled at runtime with SkinSwitcher (floating UI).
	•	Skins can also be forced with query params:
	•	?skin=night
	•	?skin=afternoon
	•	?skin=sunset
	•	?skin=morning

⸻

🔁 Workflow Rules
	•	Never commit directly to production.
	•	All work happens in main.
	•	Promote staging → production by merge or cherry-pick.
	•	Demo = production branch, but with VITE_API_MODE=mock.
	•	Playgrounds are short-lived and do not auto-update — sync manually if needed.
	•	Delete playground branches + Render services when finished.

⸻

🧑‍💻 Git Flow Cheat Sheet

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

⸻

📌 Naming Conventions
	•	Playgrounds: ultrai-play-clientx-v1, ultrai-play-investorpitch, etc.
	•	Always include purpose and version if multiple demos for the same client.

⸻

✅ Summary
	•	Prod & Demo are siblings (same branch, different API mode).
	•	Playgrounds have their own mode (playground) because they may diverge.
	•	Skins are universal, defaulting to night until others are fully ready.
	•	Cursor autocomplete will show only staging | production | playground for appMode.

⸻

👉 Do you want me to also merge this with the intro + readme package I gave you earlier into a single master docs/README.md so Cursor users only need to open one doc to see rules, skins, and env setup?



⸻

🤝 Collaboration & Oversight

• Roles
	• Claude-1 (Implementation AI): core implementation & PRs
	• UltrAI (Oversight AI): planning, review, guardrails, bounded one-offs

• Signals (use as message headers)
	• [PLAN] – Plan-of-Record updates
	• [CLAUDE_DO] – Assign core work to Claude-1
	• [ULTRA_DO] – Assign one-offs to UltrAI
	• [STATUS] – Status updates
	• [REVIEW] – Request verification; include PR links + evidence
	• [BLOCKER] – Risks/dependencies
	• [COMPLETE] – Completion notice

• Push Gates (must pass before push/merge)
	• Local tests green; commands + outputs documented
	• Security checks: dependency audit, secret/regex scan, basic injection/XSS checks
	• Model policy: ≥2 healthy models online; single-model fallback disabled
	• CORS and env vars verified for target env

• Review Cadence
	• After first PR; after integration; pre-deploy
	• Provide curl verifications and logs

• Drift Prevention
	• If off track, state: "I'm getting off track. Returning to [ORIGINAL_TASK]"
	• No refactors/optimizations/features unless explicitly requested

• Real-time Monitoring & Check-ins
	• SSE: `GET /api/orchestrator/events?correlation_id=…`
	• Events: analysis_start, model_selected, initial_start, pipeline_complete, model_completed, analysis_complete, service_unavailable
	• Check-in: `POST /api/oversight/checkin` with {task_id, status, evidence?, notes?}

See `docs/OVERSIGHT_README.md` for full details.
