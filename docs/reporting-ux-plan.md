# Reporting UX Placement Plan

This document specifies where each orchestration artifact should appear in existing UI components without requiring structural modifications.

## Component Overview

### OrchestratorInterface.jsx (`frontend/src/components/OrchestratorInterface.jsx`)
**Purpose**: Main orchestration interface with live progress and results display
**Current Structure**: Single-page layout with progress tracking and results sections

#### Artifact Placement

##### 1. Initial Drafts (Individual Model Responses)
**Location**: Lines 689-750 (after Ultra Synthesis section)
**Current Implementation**:
```jsx
{/* Individual Model Responses */}
{results.initial_responses && (
  <div className="mt-8">
    <h3 className="text-xl font-semibold mb-4 flex items-center">
      <span className="mr-2">🎯</span>
      Initial Drafts ({results.initial_responses.model_count} models)
    </h3>
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {Object.entries(results.initial_responses.responses).map(([model, data]) => (
        <div key={model} className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <h4 className="font-medium text-gray-800 mb-2">{model}</h4>
          <p className="text-sm text-gray-600 line-clamp-4">{data.preview}</p>
        </div>
      ))}
    </div>
  </div>
)}
```
**Props Used**: `results.initial_responses.responses`, `results.initial_responses.model_count`
**Display Logic**: Only shown when `results.initial_responses` exists

##### 2. Meta Drafts (Peer Review Responses)
**Location**: Lines 751-800 (after Initial Drafts section)
**Current Implementation**:
```jsx
{/* Meta Analysis & Revisions */}
{results.meta_analysis && (
  <div className="mt-8">
    <h3 className="text-xl font-semibold mb-4 flex items-center">
      <span className="mr-2">🔍</span>
      Meta Drafts ({results.meta_analysis.revision_count} revisions)
    </h3>
    <div className="space-y-4">
      {Object.entries(results.meta_analysis.responses).map(([model, data]) => (
        <div key={model} className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <h4 className="font-medium text-blue-800 mb-2">{model} (Revised)</h4>
          <p className="text-sm text-blue-700">{data.preview}</p>
        </div>
      ))}
    </div>
  </div>
)}
```
**Props Used**: `results.meta_analysis.responses`, `results.meta_analysis.revision_count`
**Display Logic**: Only shown when `results.meta_analysis` exists

##### 3. Ultra Synthesis
**Location**: Lines 646-687 (primary result section)
**Current Implementation**:
```jsx
{/* Ultra Synthesis™ - Primary Result */}
<div className="mb-8">
  <div className="flex items-center justify-between mb-4">
    <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
      Ultra Synthesis™
    </h2>
    <div className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
      Intelligence Multiplication Complete
    </div>
  </div>
  <div className="bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 p-8 rounded-xl border-2 border-purple-200 shadow-lg">
    <div className="prose max-w-none">
      <div data-testid="ultra-synthesis" className="text-lg leading-relaxed text-gray-800 whitespace-pre-wrap font-medium">
        {results.ultra_response}
      </div>
    </div>
  </div>
</div>
```
**Props Used**: `results.ultra_response`
**Display Logic**: Shown when `useFeatherOrchestration && results.status === 'success'`

##### 4. Pipeline Summary
**Location**: Lines 801-850 (footer section)
**Current Implementation**:
```jsx
{/* Pipeline Summary */}
<div className="mt-8 bg-gray-50 p-6 rounded-lg border border-gray-200">
  <h3 className="text-lg font-semibold mb-4 flex items-center">
    <span className="mr-2">📈</span>
    Pipeline Summary
  </h3>
  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
    <div>
      <span className="font-medium text-gray-700">Stages Completed:</span>
      <div className="mt-1 text-gray-600">
        {results.pipeline_summary?.stages_completed?.join(', ') || 'N/A'}
      </div>
    </div>
    <div>
      <span className="font-medium text-gray-700">Models Used:</span>
      <div className="mt-1 text-gray-600">
        {results.pipeline_summary?.total_models_used?.join(', ') || 'N/A'}
      </div>
    </div>
    <div>
      <span className="font-medium text-gray-700">Total Stages:</span>
      <div className="mt-1 text-gray-600">
        {results.pipeline_summary?.stage_count || 'N/A'}
      </div>
    </div>
  </div>
</div>
```
**Props Used**: `results.pipeline_summary.stages_completed`, `results.pipeline_summary.total_models_used`, `results.pipeline_summary.stage_count`
**Display Logic**: Always shown when results exist

### ResultsStep.tsx (`frontend/src/components/steps/ResultsStep.tsx`)
**Purpose**: Dedicated results display page in wizard flow
**Current Structure**: Single-purpose results display with actions

#### Artifact Placement

##### 1. Ultra Synthesis (Primary Content)
**Location**: Lines 66-76 (main content area)
**Current Implementation**:
```jsx
<div className="prose prose-lg dark:prose-invert max-w-none">
  {output ? (
    <div className="whitespace-pre-wrap rounded-lg border border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-gray-800/50">
      {output}
    </div>
  ) : (
    <div className="text-center py-8 text-gray-500">
      <p>No output generated or loaded.</p>
    </div>
  )}
</div>
```
**Props Used**: `output` (mapped from orchestration results)
**Display Logic**: Primary content area

##### 2. Initial Drafts, Meta Drafts, Pipeline Summary
**Current Gap**: Not currently displayed in ResultsStep
**Recommended Addition**:
```jsx
{/* Additional Results Sections */}
{results?.initial_responses && (
  <div className="mt-8">
    <h3 className="text-lg font-semibold mb-4">🎯 Initial Drafts</h3>
    {/* Initial responses display */}
  </div>
)}

{results?.meta_analysis && (
  <div className="mt-8">
    <h3 className="text-lg font-semibold mb-4">🔍 Meta Drafts</h3>
    {/* Meta analysis display */}
  </div>
)}

{results?.pipeline_summary && (
  <div className="mt-8 bg-gray-50 p-4 rounded-lg">
    <h3 className="text-lg font-semibold mb-4">📈 Pipeline Summary</h3>
    {/* Summary display */}
  </div>
)}
```

### Wizard Components (CyberWizard.tsx, etc.)
**Purpose**: Multi-step wizard interface
**Current Structure**: Tabbed interface with different views

#### Artifact Placement

##### 1. Live Progress (SSE Events)
**Location**: Status/progress section during analysis
**Current Implementation**: SSEPanel component integration
**Props Used**: `correlationId` for real-time event streaming

##### 2. Final Results Display
**Location**: Results tab/step after completion
**Current Implementation**: Full results display with all artifacts
**Props Used**: Complete `results` object from API response

## Implementation Notes

### Data Flow
1. **OrchestratorInterface**: Receives complete `results` object from `/orchestrator/analyze`
2. **ResultsStep**: Receives `output` string (primary synthesis) + full `results` context
3. **Wizard Components**: Receive `results` object and extract sections as needed

### Responsive Design
- **Mobile**: Single-column stacked layout
- **Tablet**: Two-column layout (synthesis + responses)
- **Desktop**: Three-column layout (synthesis + responses + summary)

### Accessibility
- **ARIA Labels**: Each section has proper heading hierarchy
- **Screen Readers**: Semantic markup with clear section breaks
- **Keyboard Navigation**: Proper tab order through sections

### Performance
- **Lazy Loading**: Load detailed sections on demand
- **Virtualization**: For large response lists
- **Caching**: Results cached in component state

## Copy Requirements

### Section Headers (Following Style Guide)
- **Ultra Synthesis**: "📊 ULTRA SYNTHESIS" (h2, prominent styling)
- **Initial Drafts**: "🎯 INITIAL RESPONSES ({count} models)" (h3)
- **Meta Drafts**: "🔍 META DRAFTS ({count} revisions)" (h3)
- **Pipeline Summary**: "📈 PIPELINE SUMMARY" (h3)

### Status Messages
- **Processing Time**: "Processing time: {time}s" (small text)
- **Model Count**: Displayed in section headers
- **Stage Count**: "Total Stages: {count}" in summary

## Component Props Mapping

| Component | Props | Data Source | Display Location |
|-----------|-------|-------------|------------------|
| OrchestratorInterface | `results.ultra_response` | API response | Primary synthesis section |
| OrchestratorInterface | `results.initial_responses` | API response | Secondary responses section |
| OrchestratorInterface | `results.meta_analysis` | API response | Tertiary meta section |
| OrchestratorInterface | `results.pipeline_summary` | API response | Footer summary section |
| ResultsStep | `output` | Primary synthesis | Main content area |
| ResultsStep | `results` (context) | Full response object | Additional sections |
| Wizard Components | `results` | Full response object | Tabbed results view |

This plan ensures all artifacts are properly displayed using existing component structures without requiring refactoring.