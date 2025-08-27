# Ultra UI/UX – Implementation Guide

## Overview
The wizard UI uses a simple, deterministic 12‑column grid to place three windows:
- Site header (vertical “ULTRAI”): column 1
- Main wizard panel: columns 4–8
- Receipt (itemized): columns 9–11
- Final output/status box: directly under the main panel (columns 4–8)

No full‑bleed transforms are used. The grid is bounded and centered (`max-w-6xl`), preventing overflow and keeping the background image fully visible.

## Key Files
- `src/components/CyberWizard.tsx` – main wizard, grid layout, panels, progress dots
- `src/components/OptionCards.tsx` – one‑line option rows/cards
- `src/components/AnalysisModes.tsx` – detailed analysis options
- `src/components/StatusUpdater.tsx` – status steps after final submit
- `src/components/layout/NavBar.tsx` – left, slim icon‑only vertical menu
- `public/wizard_steps.json` – wizard steps data
- `public/status_steps.json` – status steps data
- `tailwind.config.js` – custom utilities (glass/animations/neon)

## Layout (12‑col grid)
Positions inside `CyberWizard.tsx`:
- ULTRAI header: `col-start-1 col-span-1`
- Main panel: `col-start-4 col-span-5`
- Receipt: `col-start-9 col-span-3`
- Final output box (under main): same columns as main (`col-start-4 col-span-5`)

To move windows, change `col-start-<n>` and `col-span-<n>` in `CyberWizard.tsx`.

## Styling & Effects
- Tailwind utilities + custom classes in `tailwind.config.js`:
  - `glass-strong` – frosted glass w/ blur, subtle border
  - Neon text shadows: `text-shadow-neon-*`
  - Neon panel glows: `shadow-neon-*`, `animate-border-hum`
- Progress dots centered via `justify-center`; connectors use fixed width lines for predictable spacing

## Data Sources
- Wizard steps: `public/wizard_steps.json`
- Status steps (post‑submit): `public/status_steps.json`

Update these JSON files to change steps, labels, icons, and costs without editing React code.

## Background & No‑Scroll
- Background image layer is full‑screen (`absolute inset-0`, `backgroundSize: 'cover'`) and never cropped by layout shifts
- Panels use fixed heights to avoid scroll within the main view

## Running Locally
From `frontend/`:
```
npm run dev
```
- Local dev: `http://localhost:3009`
- Build: `npm run build`
- Preview: `npm run preview`

## Common Adjustments
- **Move receipt**: change to `col-start-8/10` or adjust `col-span-2/3`
- **Widen/narrow main**: tweak `col-span` while keeping start column
- **Center dots**: container uses `justify-center`; adjust connector width (default `56px`)
- **Final output under main**: panel below uses the same columns as main

## Deployment Notes
- SPA routing: ensure server rewrites to `index.html` (e.g., nginx `try_files $uri /index.html;`)
- Static assets served from `/public` (e.g., `/wizard_steps.json`)

## Troubleshooting
- **Receipt on next row**: total spans exceed 12 or container too narrow. Reduce receipt `col-span` (e.g., to 2) or shift `col-start`.
- **Panels misaligned**: keep both main and receipt in the same grid row and remove transforms/margins; use `items-start` and consistent top margin on the grid wrapper.
- **Background looks cropped**: remove full‑bleed hacks and keep bounded `max-w-6xl` container (as currently set).
- **Prod works differently from local**: check SPA fallback, JSON asset paths, and API/CORS (`VITE_API_URL`).
