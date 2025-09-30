# Output Content Style Guide

Canonical labels and terminology for UltrAI orchestration pipeline output sections.

## Canonical Section Labels

### 1. Initial Drafts

**Canonical Label:** `"Initial Drafts"` or `"Initial Responses"`

**Backend Key:** `initial_response` or `initial_responses`

**OutputFormatter Field:** `formatted_output.initial_responses`

**Display Context:**
- Stage 1 in the 3-stage pipeline
- Contains individual model outputs before peer review
- Typically collapsed/hidden in simple UI mode

**Copy Variations:**
- "Initial Drafts" (preferred for user-facing)
- "Initial Responses" (technical/detailed view)
- "First Drafts (Model-by-Model)" (OrchestratorInterface.jsx:723)
- "Model Responses" (legacy mode)

**Backend Source:**
```python
# OutputFormatter.py:108-126
def _format_initial_responses(self, initial_response: Dict[str, Any]) -> Dict[str, Any]:
    # Returns dict with 'responses', 'model_count', 'successful_models'
```

---

### 2. Meta Drafts

**Canonical Label:** `"Meta Drafts"` or `"Peer Review"`

**Backend Key:** `peer_review_and_revision` or `peer_review_responses`

**OutputFormatter Field:** `formatted_output.peer_review_responses`

**Display Context:**
- Stage 2 in the 3-stage pipeline
- Models critique and revise based on peer feedback
- Optional in simple UI mode

**Copy Variations:**
- "Meta Drafts (Peer-Reviewed)" (OrchestratorInterface.jsx:788)
- "Meta Analysis" (AnalysisInterface.tsx, alternate pipeline)
- "Peer Review & Revision" (technical documentation)

**Backend Source:**
```python
# OutputFormatter.py:128-144
def _format_peer_review(self, peer_review: Dict[str, Any]) -> Dict[str, Any]:
    # Returns dict with 'responses', 'revision_count', 'models_with_revisions'
```

---

### 3. Ultra Synthesis™

**Canonical Label:** `"Ultra Synthesis™"` or `"Ultra Synthesis"`

**Backend Key:** `ultra_synthesis`

**OutputFormatter Field:** `formatted_output.synthesis` or `results.ultra_synthesis`

**Display Context:**
- **Primary result** — the main output users care about
- Stage 3 (final) in the 3-stage pipeline
- Always visible, prominently displayed

**Copy Variations:**
- "Ultra Synthesis™" (with trademark symbol, preferred)
- "Ultra Synthesis" (without symbol, acceptable)
- "Synthesized Response" (legacy mode)
- "Final Synthesis" (avoided, sounds too final/rigid)

**Visual Treatment:**
- Gradient heading (purple-to-blue)
- Larger font, premium card styling
- Badge: "Intelligence Multiplication Complete"

**Backend Source:**
```python
# OutputFormatter.py:84-106
def _format_synthesis(self, synthesis_text: str) -> Dict[str, Any]:
    # Returns dict with 'text', 'sections', 'word_count', 'formatted_text'
```

---

### 4. Pipeline Summary

**Canonical Label:** `"Pipeline Summary"`

**Backend Key:** `pipeline_summary`

**OutputFormatter Field:** `formatted_output.pipeline_summary`

**Display Context:**
- Metadata section showing pipeline execution details
- Displayed in detailed mode or as expandable section
- Contains: stages completed, models used, success status

**Copy Variations:**
- "Pipeline Summary" (preferred)
- "Analysis Summary" (alternate, less technical)
- "Execution Details" (avoided, too enterprise-y)

**Fields:**
```typescript
{
  stages_completed: string[]      // e.g., ["initial_response", "peer_review_and_revision", "ultra_synthesis"]
  total_models_used: string[]     // e.g., ["gpt-4o", "claude-3-5-sonnet-20241022"]
  stage_count: number             // e.g., 3
  success: boolean                // true if pipeline completed
}
```

**Backend Source:**
```python
# OutputFormatter.py:146-180
def _create_pipeline_summary(self, pipeline_results: Dict[str, Any], include_metadata: bool) -> Dict[str, Any]:
```

---

## Full Document Section Headers

When OutputFormatter generates `full_document` string, it uses these headers:

### Main Header
```
🌟 ULTRA SYNTHESIS™ RESULTS 🌟
================================================================================
```

### Section Dividers
```
📊 ULTRA SYNTHESIS
------------------------------------------------------------
{synthesis text}

💡 Synthesized by: {model_name}
```

```
🎯 INITIAL RESPONSES ({N} models)
------------------------------------------------------------
### {model_name}
{response text}
```

```
📈 PIPELINE SUMMARY
------------------------------------------------------------
✅ Stages Completed: {stages}
🤖 Models Used: {models}
📊 Total Stages: {count}
```

**Backend Source:** `OutputFormatter.py:182-227`

---

## Terminology Mapping

### Backend → Frontend Mapping

| Backend Term | Frontend Display | Notes |
|--------------|------------------|-------|
| `initial_response` | "Initial Drafts" | Stage 1 |
| `peer_review_and_revision` | "Meta Drafts" | Stage 2 |
| `ultra_synthesis` | "Ultra Synthesis™" | Stage 3 (primary) |
| `formatted_output` | Various sections | Structured data for rendering |
| `synthesis.text` | Main content area | The actual answer |
| `synthesis.sections` | Expandable sections | Parsed markdown headers |
| `pipeline_summary` | "Pipeline Summary" | Metadata/stats |

---

## OutputFormatter Keys Reference

### Top-Level Structure

```typescript
{
  synthesis: {
    text: string                    // Raw synthesis text
    sections: Section[]             // Parsed markdown sections
    word_count: number
    formatted_text: string          // With formatting enhancements
  }
  synthesis_model: string           // e.g., "gpt-4o"
  initial_responses?: {             // Optional, controlled by include_initial_responses flag
    responses: Record<string, {
      text: string
      word_count: number
      preview: string
    }>
    model_count: number
    successful_models: string[]
  }
  peer_review_responses?: {         // Optional, controlled by include_peer_review flag
    responses: Record<string, {...}>
    revision_count: number
    models_with_revisions: string[]
  }
  pipeline_summary: {
    stages_completed: string[]
    total_models_used: string[]
    stage_count: number
    success: boolean
    metadata?: {...}                // Optional, controlled by include_metadata flag
  }
  full_document: string             // Formatted full text output
}
```

---

## Display Mode Mapping

### Simple Mode (Default)

**Flag:** `include_pipeline_details=false`

**Visible Sections:**
- ✅ Ultra Synthesis™ (primary)
- ✅ Formatted Synthesis (full_document, fallback)
- ✅ Pipeline Info (metadata: time, models)
- ❌ Initial Drafts (hidden)
- ❌ Meta Drafts (hidden)

**Example Response Shape:**
```json
{
  "ultra_synthesis": "...",
  "formatted_synthesis": "...",
  "status": "completed"
}
```

---

### Detailed Mode

**Flag:** `include_pipeline_details=true`

**Visible Sections:**
- ✅ Ultra Synthesis™ (still primary)
- ✅ Initial Drafts (expandable)
- ✅ Meta Drafts (expandable)
- ✅ Pipeline Summary (with full stats)
- ✅ Formatted Output (structured data)

**Example Response Shape:**
```json
{
  "initial_response": {...},
  "peer_review_and_revision": {...},
  "ultra_synthesis": {...},
  "formatted_output": {
    "synthesis": {...},
    "initial_responses": {...},
    "peer_review_responses": {...},
    "pipeline_summary": {...},
    "full_document": "..."
  }
}
```

---

## UI Component Responsibilities

### OrchestratorInterface.jsx

**Displays:**
- Ultra Synthesis™ with gradient styling (lines 644-686)
- "Detailed Analysis Breakdown" collapsible section (lines 690-816)
- Within breakdown: Initial Drafts (stage 1), Meta Drafts (stage 2)

**Key Props:**
- `results.ultra_response` → Main synthesis display
- `results.initial_responses` → Stage 1 breakdown
- `results.peer_review_responses` → Stage 2 breakdown

---

### AnalysisInterface.tsx

**Displays:**
- ResultsDisplay component with all sections
- Passes `results` array to ResultsDisplay

---

### ResultsDisplay Component (atoms/)

**Responsibilities:**
- Render synthesis text with markdown formatting
- Show/hide sections based on mode
- Display model badges and metadata

---

## Content Guidelines

### Writing Style

**Ultra Synthesis™:**
- Professional but accessible
- Structured with markdown headings
- Bullet points for key insights
- Conclusion section summarizing answer

**Initial/Meta Drafts:**
- Can be raw/unpolished
- Model-specific voice preserved
- Minimal formatting

**Pipeline Summary:**
- Technical, factual
- Use bullet points
- Include numbers (word counts, processing time, model counts)

---

### Formatting Conventions

**Emphasis:**
- Bold for **key findings**, **important**, **significant**, **notable**, **critical**
- Bold for **conclusion**, **summary**, **recommendation**

**Lists:**
- Convert numbered lists to bullets with `• ` prefix
- Preserve indentation for nested lists

**Sections:**
- Use `## ` for h2 headings
- Use `### ` for h3 headings
- Extract sections into `synthesis.sections` array

---

## Testing Content Output

### Backend Unit Tests

```bash
pytest tests/unit/test_output_formatter.py -v
```

**Validates:**
- Section extraction from markdown
- Word count accuracy
- Full document structure
- Include/exclude flags work correctly

---

### Frontend Render Tests

```bash
npm test -- ResultsDisplay.test.tsx
```

**Validates:**
- All canonical labels render correctly
- Simple mode hides Initial/Meta drafts
- Detailed mode shows all sections
- Error states display appropriately

---

## Related Files

**Backend:**
- `app/services/output_formatter.py` (main formatter logic)
- `app/routes/orchestrator_minimal.py` (builds response with formatter)

**Frontend:**
- `frontend/src/components/OrchestratorInterface.jsx` (main results display)
- `frontend/src/components/atoms/ResultsDisplay.tsx` (results component)
- `frontend/src/components/AnalysisInterface.tsx` (alternate interface)

**Documentation:**
- `docs/analysis_response.schema.json` (JSON schema)
- `reports/samples/analysis_response_*.json` (example responses)
