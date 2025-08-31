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


