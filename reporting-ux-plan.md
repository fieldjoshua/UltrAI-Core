### Reporting UX placement plan (no refactors)

Goal: Specify where to present first-round drafts, meta-round drafts, ultra synthesis, and summary in existing components. This is documentation only; do not modify component structure.

Primary components
- `frontend/src/components/OrchestratorInterface.jsx`
  - Show progress via existing `AnalysisProgress` while running.
  - On completion, in the results section:
    - Ultra Synthesis: Prefer `results.formatted_synthesis` (string). If absent, use `ultra_response`.
    - Initial Drafts: If `results.initial_responses` present, render a collapsible section labeled "Initial Drafts" listing `successful_models` with `preview`.
    - Meta Drafts: If `results.meta_analysis` or detailed mode includes `peer_review_responses`, render collapsible "Meta Drafts" with previews.
    - Pipeline Summary: If `results.formatted_output.pipeline_summary` (detailed) or `pipeline_info` exists, render a compact summary (stages, models).
  - Live events: Optional side panel with `SSEPanel` when `correlationId` is set.

- Wizard pages (`frontend/src/components/wizard/CyberWizardWithQuery.tsx`, `CyberWizard.tsx`)
  - In final step:
    - Ultra Synthesis: Render `ultra_response` or `formatted_synthesis` as the primary content body.
    - Provide a "Show sources" toggle that reveals Initial Drafts and Meta Drafts if available, same labels as above.
    - Display a compact pipeline chips row (e.g., Initial ✓, Meta ✓, Ultra ✓) based on `pipeline_info.stages_completed`.

- `frontend/src/components/AnalysisInterface.tsx`
  - In the `results` tab card:
    - Primary: Ultra Synthesis (`formatted_synthesis` -> fallback `ultra_response`).
    - Secondary: If present, list Initial Drafts previews and a link/button to expand Meta Drafts.
    - Footer: Pipeline summary line using `pipeline_info`.

Labels and copy (align with OutputFormatter)
- "Ultra Synthesis"
- "Initial Drafts"
- "Meta Drafts"
- "Pipeline Summary"

Data sources
- Simple mode: `ultra_response`, `results.formatted_synthesis`, optional `results.initial_responses`, optional `results.meta_analysis`.
- Detailed mode: `results.formatted_output.full_document` (for downloadable copy), `results.formatted_output.initial_responses`, `results.formatted_output.peer_review_responses`, `results.formatted_output.pipeline_summary`.

Download/export (optional placement)
- Provide a "Copy" or "Download .txt" for the Ultra Synthesis body only; avoid blocking on full detailed output.


