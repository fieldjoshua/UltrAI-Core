# Frontend Test Checklist

## Multi-Model Selection Guard (≥2 Models Required)

This checklist ensures the frontend correctly enforces the requirement for selecting at least 2 models before enabling Ultra Synthesis™ initialization.

### Manual QA Steps

1. **Initial State Verification**
   - [ ] Navigate to the main orchestrator page
   - [ ] Verify the model selection interface is visible
   - [ ] Confirm "Initialize UltraAI" button is not visible until models are selected

2. **Single Model Selection**
   - [ ] Select only one model (e.g., GPT-4)
   - [ ] Click "Submit Add-ons" or equivalent
   - [ ] Verify the "Initialize UltraAI" button is disabled
   - [ ] Confirm warning message appears: "⚠️ Select at least 2 models"
   - [ ] Verify explanation text: "Ultra Synthesis™ requires multiple models for optimal results"

3. **Two Model Selection**
   - [ ] Select exactly 2 models (e.g., GPT-4 and Claude-3)
   - [ ] Click "Submit Add-ons"
   - [ ] Verify "Initialize UltraAI" button becomes enabled with rocket emoji (🚀)
   - [ ] Confirm no warning message appears
   - [ ] Test that clicking the button proceeds to analysis

4. **Multiple Model Selection (3+)**
   - [ ] Select 3 or more models
   - [ ] Verify "Initialize UltraAI" button remains enabled
   - [ ] Confirm analysis works with all selected models

5. **Model Deselection**
   - [ ] Start with 3 models selected and submitted
   - [ ] Deselect models to have only 1 remaining
   - [ ] Verify the interface updates to show the warning again
   - [ ] Re-select to have 2+ models
   - [ ] Confirm the button re-enables

### Automated Test Suggestions

```typescript
// Example test structure for CyberWizard component
describe('CyberWizard Model Selection Guard', () => {
  it('should disable initialization with < 2 models', () => {
    const { getByText, queryByText } = render(<CyberWizard />);
    
    // Select only one model
    fireEvent.click(getByText('GPT-4'));
    fireEvent.click(getByText('Submit Add-ons'));
    
    // Check for disabled state
    expect(getByText('⚠️ Select at least 2 models')).toBeInTheDocument();
    expect(queryByText('🚀 Initialize UltraAI')).not.toBeInTheDocument();
  });

  it('should enable initialization with >= 2 models', () => {
    const { getByText } = render(<CyberWizard />);
    
    // Select two models
    fireEvent.click(getByText('GPT-4'));
    fireEvent.click(getByText('Claude-3'));
    fireEvent.click(getByText('Submit Add-ons'));
    
    // Check for enabled state
    expect(getByText('🚀 Initialize UltraAI')).toBeInTheDocument();
    expect(getByText('🚀 Initialize UltraAI')).not.toBeDisabled();
  });
});
```

### Background Theme Toggle Verification

1. **Theme Toggle Sanity Check**
   - [ ] Toggle between light/dark themes multiple times
   - [ ] Verify no layout shifts occur during transitions
   - [ ] Check that all text remains readable in both themes
   - [ ] Confirm model selection state persists through theme changes
   - [ ] Verify animations/transitions are smooth

2. **Visual Regression Points**
   - [ ] CyberWizard component maintains dimensions
   - [ ] Button positions remain stable
   - [ ] Model selection cards don't jump or flicker
   - [ ] Warning messages appear/disappear smoothly

### Integration Test Points

1. **API Integration**
   - [ ] Verify selected models are correctly sent to `/api/orchestrator/analyze`
   - [ ] Confirm error handling when < 2 models somehow bypass frontend
   - [ ] Test that model availability affects selection options

2. **State Management**
   - [ ] Selected models persist across navigation (if applicable)
   - [ ] Redux/Context state correctly tracks model selection
   - [ ] Model count updates trigger appropriate UI changes

### Accessibility Testing

1. **Keyboard Navigation**
   - [ ] Tab through model selection works correctly
   - [ ] Enter/Space toggles model selection
   - [ ] Disabled button is properly announced to screen readers
   - [ ] Warning message is announced when it appears

2. **ARIA Labels**
   - [ ] Model selection has appropriate labels
   - [ ] Button states (enabled/disabled) are communicated
   - [ ] Error/warning messages have proper roles

### Edge Cases

1. **Rapid Selection/Deselection**
   - [ ] Quickly toggle models on/off
   - [ ] Verify UI stays in sync with actual selection state
   - [ ] No race conditions or stuck states

2. **Browser Compatibility**
   - [ ] Test in Chrome, Firefox, Safari, Edge
   - [ ] Verify mobile responsiveness
   - [ ] Check touch interactions on mobile devices

3. **Performance**
   - [ ] Model selection should be instant (<100ms response)
   - [ ] No unnecessary re-renders when selection changes
   - [ ] Smooth transitions without jank

## Running Tests

### Manual Testing
1. Start the development server: `cd frontend && npm run dev`
2. Navigate to http://localhost:3000
3. Follow the checklist above

### Automated Testing
```bash
# Run all frontend tests
cd frontend && npm test

# Run specific test file
npm test -- CyberWizard.test.tsx

# Run with coverage
npm test -- --coverage
```

## CI/CD Considerations

- [ ] Add E2E test for model selection in Playwright suite
- [ ] Include visual regression tests for theme toggle
- [ ] Ensure test coverage includes the guard logic
- [ ] Add performance benchmarks for model selection UI