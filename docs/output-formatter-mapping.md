### Output formatter mapping (backend → formatted output → UI)

Purpose: Precisely map pipeline stage outputs to `OutputFormatter` fields and to UI consumers, so results are tidy and predictable across simple and detailed modes.

- Backend entry points
  - Orchestrator response assembly: `app/routes/orchestrator_minimal.py` (formats `AnalysisResponse`)
  - Formatter: `app/services/output_formatter.py`

- Pipeline stages (as produced by `app/services/orchestration_service.py`)
  - `initial_response` (aka first-round drafts)
    - Expected shape for formatter input: `{ responses: { [modelName]: string } }`
  - `peer_review_and_revision` (aka meta-round drafts)
    - Expected shape for formatter input: `{ revised_responses: { [modelName]: string }, revision_count?: int }`
  - `ultra_synthesis`
    - Expected canonical content: string in `synthesis` or `synthesis_enhanced` (string)

- Formatter outputs (keys returned by `OutputFormatter.format_pipeline_output`)
  - `synthesis`
    - `{ text: string, sections: Array<{ title, content, level }>, word_count: number, formatted_text: string }`
    - Source: `ultra_synthesis.synthesis` (string; if object, coerced to string)
  - `synthesis_model`
    - The model used for synthesis if available (fallback "Unknown")
  - `initial_responses`
    - `{ responses: { [modelName]: { text, word_count, preview } }, model_count: number, successful_models: string[] }`
    - Source: `initial_response.responses`
  - `peer_review_responses`
    - `{ responses: { [modelName]: { text, word_count, preview } }, revision_count?: int, models_with_revisions: string[] }`
    - Source: `peer_review_and_revision.revised_responses`
  - `pipeline_summary`
    - `{ stages_completed: string[], total_models_used: string[], stage_count: number, metadata? }`
    - Aggregates models from `initial_response.successful_models` and `ultra_synthesis.model_used`
  - `full_document`
    - Plain text string: header + formatted synthesis + initial drafts summary + pipeline summary

- Response assembly modes (in `orchestrator_minimal.py`)
  - Simple (default)
    - `results.ultra_synthesis`: string (or object coerced to string)
    - `results.formatted_synthesis`: `formatted.full_document` built from `{ ultra_synthesis, [initial_response] }`
    - Optional passthrough when present: `results.initial_responses`, `results.meta_analysis`
  - Detailed (`include_pipeline_details=true`)
    - `results.<stage>` per stage with `{ output, quality?, status }`
    - `results.formatted_output`: full formatter object with keys above

- UI consumption notes
  - Frontend maps API response to `OrchestrationResponse` in `frontend/src/api/orchestrator.ts`:
    - `ultra_response` is taken from `data.results?.ultra_synthesis?.content || data.results?.content || ''` (covers both string and object forms)
    - Thus, ensure simple mode returns a string-like `ultra_synthesis` or an object with `.content`.
  - When detailed output is enabled, prefer reading `formatted_output.full_document` or `formatted_synthesis` for display.

- Consistency rules
  - For simple mode: always include `formatted_synthesis` (string) alongside `ultra_synthesis` for UI-ready display.
  - For detailed mode: always include `formatted_output.full_document`.
  - If `initial_response.responses` or `peer_review_and_revision.revised_responses` are present, they should be strings per model.

- Edge cases handled by formatter
  - Non-string synthesis values are coerced via `str(value)`.
  - `None` becomes empty string.
  - Markdown emphasis and list normalization are applied in `formatted_text`.

- Minimal acceptance checklist
  - [ ] Ultra synthesis string yields non-empty `formatted_text` and `full_document`.
  - [ ] Initial responses (if present) produce `model_count === Object.keys(responses).length`.
  - [ ] Pipeline summary `stage_count` equals number of present stage keys.


