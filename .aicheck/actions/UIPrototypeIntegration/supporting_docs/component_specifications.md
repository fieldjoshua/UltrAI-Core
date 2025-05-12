# UI Component Specifications

This document provides detailed specifications for each UI component to be implemented as part of the UI Prototype Integration action.

## 1. Prompt Input Component

### Component Name: `PromptInput`

### Props:
- `onSubmit: (prompt: string, options: AnalysisOptions) => void`
- `isLoading: boolean`
- `maxLength?: number` (default: 4000)
- `placeholder?: string`
- `initialValue?: string`

### State:
- `prompt: string`
- `errorMessage?: string`
- `charCount: number`

### Functionality:
- Auto-resizing textarea
- Character counter with max limit
- Submit button (disabled when empty or error)
- Loading state indicator
- Validation for minimum length (10 chars)
- Error message display
- Keyboard shortcut (Ctrl/Cmd + Enter) for submission

### Styling:
- Light/dark mode compatible
- Focus states
- Error states
- Responsive (mobile-friendly)

## 2. LLM Selector Component

### Component Name: `ModelSelector`

### Props:
- `availableModels: Model[]`
- `selectedModels: string[]`
- `onSelectionChange: (modelIds: string[]) => void`
- `isLoading: boolean`
- `error?: Error`
- `maxSelections?: number` (default: 5)

### State:
- `groupedModels: Record<string, Model[]>` (grouped by provider)
- `selections: string[]`
- `expanded: Record<string, boolean>` (for provider groups)

### Model Interface:
```typescript
interface Model {
  id: string;
  name: string;
  provider: string;
  description?: string;
  capabilities?: string[];
  isAvailable: boolean;
}
```

### Functionality:
- Group models by provider
- Expandable/collapsible provider sections
- Checkbox selection for each model
- Model tooltips with capabilities
- Maximum selection limit enforcement
- "Select All" / "Clear All" options per provider
- Disabled state for unavailable models
- Loading state

### Styling:
- Card-based design
- Provider grouping with headers
- Selection indicators
- Disabled state styling
- Responsive grid layout

## 3. Analysis Pattern Selector Component

### Component Name: `PatternSelector`

### Props:
- `availablePatterns: AnalysisPattern[]`
- `selectedPattern: string`
- `onPatternChange: (patternId: string) => void`
- `isLoading: boolean`
- `error?: Error`

### State:
- `selected: string`
- `expandedDetail: string | null`

### Pattern Interface:
```typescript
interface AnalysisPattern {
  id: string;
  name: string;
  description: string;
  useCases: string[];
  configOptions?: PatternConfigOption[];
}

interface PatternConfigOption {
  id: string;
  name: string;
  type: 'boolean' | 'select' | 'range';
  default: any;
  options?: any[];
}
```

### Functionality:
- Card-based pattern selection
- Detailed information display
- Configuration options for patterns that support it
- Visual selection indicator
- Pattern comparison tooltip

### Styling:
- Card design with hover effects
- Selected state highlighting
- Expandable details section
- Icon indicators for pattern types
- Responsive layout

## 4. Results Display Component

### Component Name: `ResultsDisplay`

### Props:
- `results: AnalysisResult[]`
- `isLoading: boolean`
- `error?: Error`
- `comparisonMode?: boolean`

### State:
- `activeTab: string` (model ID or 'comparison')
- `expandedSections: string[]`
- `viewMode: 'standard' | 'compact' | 'detailed'`

### Result Interface:
```typescript
interface AnalysisResult {
  modelId: string;
  modelName: string;
  content: string;
  timestamp: string;
  processingTimeMs: number;
  sections?: {
    id: string;
    title: string;
    content: string;
  }[];
  metadata?: Record<string, any>;
}
```

### Functionality:
- Tabbed interface for model results
- Syntax highlighting for code blocks
- Collapsible sections
- Copy to clipboard functionality
- Export to file (txt, markdown)
- Side-by-side comparison view
- Timestamp and processing time display
- Error state handling
- Empty state handling

### Styling:
- Tabbed navigation
- Code block formatting
- Responsive design (stacked on mobile)
- Light/dark mode compatible
- Print-friendly styles

## 5. Progress Indicator Component

### Component Name: `AnalysisProgress`

### Props:
- `status: 'idle' | 'preparing' | 'analyzing' | 'complete' | 'error'`
- `currentStep?: number`
- `totalSteps?: number`
- `estimatedTimeRemaining?: number`
- `statusMessage?: string`
- `error?: Error`

### State:
- `progress: number` (percentage)
- `elapsedTime: number`

### Functionality:
- Visual progress indicator (linear or circular)
- Step indicator for multi-stage processes
- Animated transitions
- Time estimation display
- Status message display
- Error state handling
- Cancelation option (if supported)

### Styling:
- Animated progress bar/spinner
- Step indicators
- Status message styling
- Error state styling
- Compact mobile view

## 6. Layout Component

### Component Name: `AnalysisLayout`

### Props:
- `children: React.ReactNode`
- `navigationItems?: NavigationItem[]`
- `theme?: 'light' | 'dark' | 'system'`
- `onThemeChange?: (theme: 'light' | 'dark' | 'system') => void`

### State:
- `isMobileMenuOpen: boolean`
- `currentTheme: 'light' | 'dark'`

### Functionality:
- Responsive layout with sidebar/header
- Mobile menu toggle
- Theme switching
- Navigation between sections
- Fixed header with scrollable content
- Footer with relevant links

### Styling:
- Responsive grid layout
- Header and sidebar styling
- Mobile-friendly navigation
- Theme-aware styling
- Consistent spacing
- Container width limits for readability

## Integration Component

### Component Name: `AnalysisInterface`

### State:
- `prompt: string`
- `selectedModels: string[]`
- `selectedPattern: string`
- `isSubmitting: boolean`
- `results: AnalysisResult[] | null`
- `error: Error | null`
- `analysisStatus: 'idle' | 'preparing' | 'analyzing' | 'complete' | 'error'`

### Functionality:
- Manages overall state of the analysis interface
- Coordinates between components
- Handles API requests
- Manages loading states
- Handles error states
- Provides functions for child components

### Integration:
- Fetches available models and patterns on mount
- Submits analysis requests
- Polls for analysis status
- Retrieves results when complete
- Handles error conditions
- Manages user preferences in local storage

## Accessibility Requirements

All components must:
- Have proper ARIA attributes
- Support keyboard navigation
- Maintain sufficient color contrast
- Include screen reader friendly text
- Handle focus management properly
- Support text zoom
- Have semantic HTML structure

## Browser Compatibility

All components must function correctly in:
- Chrome (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Edge (last 2 versions)

## Performance Goals

- Initial load time < 2s
- Time to interactive < 3s
- Smooth animations (60fps)
- Responsive to user input (< 100ms)
- Optimized bundle size