# Output Content Style Guide

This guide defines the canonical labels, headings, and content structure used by the `OutputFormatter` for consistent display across backend formatting and frontend UI components.

## Canonical Section Labels

### Primary Sections

#### 1. Ultra Synthesis™
**Backend Key**: `synthesis`
**Display Label**: "📊 ULTRA SYNTHESIS"
**Description**: The primary synthesized result from the multi-model analysis
**Content Structure**:
- Main synthesis text (formatted with markdown)
- Attribution: "💡 Synthesized by: {model_name}"
- Sections extracted from synthesis text (if present)

**UI Placement**: Prominent display as the main result

#### 2. Initial Drafts
**Backend Key**: `initial_responses`
**Display Label**: "🎯 INITIAL RESPONSES ({model_count} models)"
**Description**: Raw responses from individual models before synthesis
**Content Structure**:
- Model name as subheading: "### {model_name}"
- Response preview text (truncated to 150 chars)
- Model count indicator

**UI Placement**: Secondary section showing individual model contributions

#### 3. Meta Drafts
**Backend Key**: `peer_review_responses`
**Display Label**: "🔍 META ANALYSIS" (implied from context)
**Description**: Peer review and revision responses
**Content Structure**:
- Model name as subheading: "### {model_name}"
- Revised response preview text
- Revision count indicator

**UI Placement**: Tertiary section showing refinement process

#### 4. Pipeline Summary
**Backend Key**: `pipeline_summary`
**Display Label**: "📈 PIPELINE SUMMARY"
**Description**: Execution metadata and completion status
**Content Structure**:
- "✅ Stages Completed: {stage1, stage2, ...}"
- "🤖 Models Used: {model1, model2, ...}"
- "📊 Total Stages: {count}"

**UI Placement**: Footer section with execution details

## Content Formatting Rules

### Headings and Structure
- **Main Sections**: Use emoji + ALL CAPS labels
- **Model Names**: Display as "### {model_name}" subheadings
- **Section Separators**: 80-character "=" lines between major sections
- **Subsection Separators**: 60-character "-" lines for model sections

### Text Formatting
- **Bold Key Terms**: `**key finding**`, `**conclusion**`, `**recommendation**`
- **List Items**: Convert markdown lists to "• " bullet points
- **Preview Truncation**: Limit to 150 characters with "..." suffix
- **Word Count**: Include in metadata but not prominently displayed

### Attribution
- **Synthesis Attribution**: "💡 Synthesized by: {model_name}"
- **Model Count**: Display as "({count} models)" in section headers
- **Stage Count**: Display as "📊 Total Stages: {count}"

## Data Source Mapping

| Display Label | Backend Key | Data Structure | Required For |
|---------------|-------------|----------------|--------------|
| Ultra Synthesis | `synthesis` | `{"text": str, "sections": [...], "word_count": int, "formatted_text": str}` | All responses |
| Initial Responses | `initial_responses` | `{"responses": {...}, "model_count": int, "successful_models": [...]}` | Detailed view |
| Meta Analysis | `peer_review_responses` | `{"responses": {...}, "revision_count": int, "models_with_revisions": [...]}` | Detailed view |
| Pipeline Summary | `pipeline_summary` | `{"stages_completed": [...], "total_models_used": [...], "stage_count": int}` | All responses |

## UI Implementation Notes

### Component Structure
```typescript
// Typical component structure for displaying formatted output
<div>
  <h1>📊 ULTRA SYNTHESIS</h1>
  <div>{formatted_synthesis.text}</div>
  <div>💡 Synthesized by: {formatted_synthesis.model}</div>

  <h1>🎯 INITIAL RESPONSES ({initial_responses.model_count} models)</h1>
  {Object.entries(initial_responses.responses).map(([model, data]) => (
    <div key={model}>
      <h2>### {model}</h2>
      <div>{data.preview}</div>
    </div>
  ))}

  <h1>📈 PIPELINE SUMMARY</h1>
  <div>✅ Stages Completed: {pipeline_summary.stages_completed.join(', ')}</div>
  <div>🤖 Models Used: {pipeline_summary.total_models_used.join(', ')}</div>
</div>
```

### Responsive Design
- **Mobile**: Stack sections vertically, use smaller headings
- **Desktop**: Two-column layout for synthesis + responses
- **Print**: Full-width layout with clear section breaks

### Accessibility
- **ARIA Labels**: Use section headings as landmarks
- **Screen Readers**: Ensure emoji labels have text alternatives
- **Keyboard Navigation**: Proper heading hierarchy (h1 → h2 → h3)

## Consistency Constraints

### Do Not Change
- Section header emojis and styling
- Attribution format ("💡 Synthesized by: {model}")
- Model count display format ("({count} models)")
- Section separator characters and lengths

### Can Customize
- CSS styling and colors
- Layout arrangements (grid vs. flex)
- Animation and transitions
- Additional metadata display

## Migration from Legacy Labels

| Legacy Label | New Canonical Label | Status |
|--------------|-------------------|---------|
| "Synthesis Results" | "📊 ULTRA SYNTHESIS" | Updated |
| "Model Responses" | "🎯 INITIAL RESPONSES" | Updated |
| "Peer Review" | "🔍 META ANALYSIS" | Updated |
| "Summary" | "📈 PIPELINE SUMMARY" | Updated |

All components should use the canonical labels defined in this guide to ensure consistent user experience across the application.