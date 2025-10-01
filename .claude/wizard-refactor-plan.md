# CyberWizard Refactoring Plan

**Goal:** Split 3300-line CyberWizard into testable components with isolated state

**Estimated:** 2-3 days | **Split:** Claude + GPT + Aux

---

## Current Architecture Problems

```
CyberWizard.tsx (3300 lines)
├── 30 useState variables (!)
├── Complex step navigation logic
├── Model selection + API calls
├── Receipt calculation
├── Orchestration triggering
└── Results display
```

**Issues:**
- Too much state = unpredictable updates in tests
- Hard to test individual features
- Changes break unrelated tests
- 12/25 tests timing out

---

## Target Architecture

```
CyberWizard.tsx (orchestrator, ~500 lines)
├── useWizardSteps hook
│   └── Step navigation, keyboard handling
├── useModelSelection hook
│   └── Model choices, Premium/Speed/Budget logic
├── useReceipt hook
│   └── Cost calculation, itemized list
├── StepNavigation component
│   └── Step markers, progress bar
├── WizardStep component
│   └── Individual step rendering
└── OrchestrationTrigger component
    └── Initialize button, status display
```

**Benefits:**
- Each hook testable in isolation (5-10 lines of test code)
- State scoped to feature (predictable updates)
- Tests pass reliably
- Easy to add new steps/features

---

## Division of Labor

### **CLAUDE** (Foundation & Hooks - 8 hours)

**Priority 1: Extract Step Navigation Hook**
```typescript
// hooks/useWizardSteps.ts
export function useWizardSteps(steps: WizardStep[]) {
  const [currentStep, setCurrentStep] = useState(0);
  const [stepHistory, setStepHistory] = useState<number[]>([0]);
  
  const goToStep = useCallback((step: number) => {
    setCurrentStep(step);
    setStepHistory(prev => [...prev, step]);
  }, []);
  
  const goBack = useCallback(() => {
    if (stepHistory.length > 1) {
      const newHistory = stepHistory.slice(0, -1);
      setStepHistory(newHistory);
      setCurrentStep(newHistory[newHistory.length - 1]);
    }
  }, [stepHistory]);
  
  const handleKeyboard = useCallback((e: KeyboardEvent) => {
    if (e.key === 'ArrowRight') goToStep(Math.min(currentStep + 1, steps.length - 1));
    if (e.key === 'ArrowLeft') goToStep(Math.max(currentStep - 1, 1));
  }, [currentStep, steps.length]);
  
  return { currentStep, goToStep, goBack, handleKeyboard, stepHistory };
}
```

**Test (20 lines):**
```typescript
test('useWizardSteps navigates forward', () => {
  const { result } = renderHook(() => useWizardSteps(mockSteps));
  act(() => result.current.goToStep(2));
  expect(result.current.currentStep).toBe(2);
});
```

**Tasks:**
- [ ] Create `frontend/src/hooks/useWizardSteps.ts`
- [ ] Create `frontend/src/hooks/__tests__/useWizardSteps.test.ts`
- [ ] Extract keyboard handling from CyberWizard
- [ ] Test: forward, backward, keyboard nav
- [ ] Update CyberWizard to use hook

**Priority 2: Extract Receipt Hook**
```typescript
// hooks/useReceipt.ts
export function useReceipt() {
  const [items, setItems] = useState<ReceiptItem[]>([]);
  
  const addItem = useCallback((item: ReceiptItem) => {
    setItems(prev => [...prev, item]);
  }, []);
  
  const removeItem = useCallback((id: string) => {
    setItems(prev => prev.filter(i => i.id !== id));
  }, []);
  
  const total = useMemo(() => 
    items.reduce((sum, item) => sum + item.cost, 0),
    [items]
  );
  
  return { items, addItem, removeItem, total, clear: () => setItems([]) };
}
```

**Tasks:**
- [ ] Create `frontend/src/hooks/useReceipt.ts`
- [ ] Create `frontend/src/hooks/__tests__/useReceipt.test.ts`
- [ ] Extract cost calculation logic
- [ ] Test: add, remove, total calculation
- [ ] Update CyberWizard to use hook

---

### **GPT** (Components & Model Selection - 8 hours)

**Priority 1: Create StepNavigation Component**
```typescript
// components/wizard/StepNavigation.tsx
export function StepNavigation({ 
  steps, 
  currentStep, 
  onStepClick 
}: StepNavigationProps) {
  return (
    <nav aria-label="Wizard steps">
      {steps.filter(s => s.idx !== 0).map(step => (
        <button
          key={step.idx}
          onClick={() => onStepClick(step.idx)}
          aria-current={currentStep === step.idx ? 'step' : undefined}
          aria-label={`Go to step ${step.idx}: ${step.title}`}
        >
          {step.idx}
        </button>
      ))}
    </nav>
  );
}
```

**Test (15 lines):**
```typescript
test('StepNavigation renders all steps', () => {
  render(<StepNavigation steps={mockSteps} currentStep={1} onStepClick={vi.fn()} />);
  expect(screen.getAllByRole('button')).toHaveLength(5); // Excludes step 0
});
```

**Tasks:**
- [ ] Create `frontend/src/components/wizard/StepNavigation.tsx`
- [ ] Create `frontend/src/components/wizard/__tests__/StepNavigation.test.tsx`
- [ ] Extract step marker rendering from CyberWizard
- [ ] Test: render, click handling, active state
- [ ] Update CyberWizard to use component

**Priority 2: Extract Model Selection Hook**
```typescript
// hooks/useModelSelection.ts
export function useModelSelection() {
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [selectionMode, setSelectionMode] = useState<'premium' | 'speed' | 'budget' | 'custom'>('premium');
  
  const selectPreset = useCallback((mode: 'premium' | 'speed' | 'budget') => {
    setSelectionMode(mode);
    const presets = {
      premium: ['gpt-4', 'claude-3-opus', 'gemini-1.5-pro'],
      speed: ['gpt-4o-mini', 'claude-3-haiku'],
      budget: ['gpt-3.5-turbo']
    };
    setSelectedModels(presets[mode]);
  }, []);
  
  const toggleModel = useCallback((model: string) => {
    setSelectionMode('custom');
    setSelectedModels(prev => 
      prev.includes(model) 
        ? prev.filter(m => m !== model)
        : [...prev, model]
    );
  }, []);
  
  return { selectedModels, selectionMode, selectPreset, toggleModel };
}
```

**Tasks:**
- [ ] Create `frontend/src/hooks/useModelSelection.ts`
- [ ] Create `frontend/src/hooks/__tests__/useModelSelection.test.ts`
- [ ] Extract model selection logic
- [ ] Test: preset selection, manual toggle, validation
- [ ] Update CyberWizard to use hook

---

### **AUX** (Step Components & Integration - 8 hours)

**Priority 1: Create WizardStep Component**
```typescript
// components/wizard/WizardStep.tsx
export function WizardStep({ 
  step, 
  isActive, 
  onValueChange 
}: WizardStepProps) {
  if (!isActive) return null;
  
  switch (step.type) {
    case 'intro':
      return <IntroStep step={step} />;
    case 'checkbox':
      return <CheckboxStep step={step} onChange={onValueChange} />;
    case 'textarea':
      return <TextareaStep step={step} onChange={onValueChange} />;
    case 'groupbox':
      return <GroupboxStep step={step} onChange={onValueChange} />;
    default:
      return null;
  }
}
```

**Tasks:**
- [ ] Create `frontend/src/components/wizard/WizardStep.tsx`
- [ ] Create step type components (IntroStep, CheckboxStep, etc.)
- [ ] Create `frontend/src/components/wizard/__tests__/WizardStep.test.tsx`
- [ ] Test each step type renders correctly
- [ ] Update CyberWizard to use component

**Priority 2: Integration & Migration**
```typescript
// CyberWizard.tsx (after refactor)
export default function CyberWizard() {
  const { currentStep, goToStep, handleKeyboard } = useWizardSteps(steps);
  const { selectedModels, selectPreset } = useModelSelection();
  const { items, addItem, total } = useReceipt();
  
  useEffect(() => {
    window.addEventListener('keydown', handleKeyboard);
    return () => window.removeEventListener('keydown', handleKeyboard);
  }, [handleKeyboard]);
  
  return (
    <div>
      <StepNavigation steps={steps} currentStep={currentStep} onStepClick={goToStep} />
      <WizardStep step={steps[currentStep]} isActive onValueChange={handleStepValue} />
      <Receipt items={items} total={total} />
    </div>
  );
}
```

**Tasks:**
- [ ] Update CyberWizard to use all new hooks/components
- [ ] Remove old state variables (30 → ~8)
- [ ] Verify all features still work
- [ ] Run full test suite
- [ ] Fix any integration issues

---

## Success Criteria

**Tests:**
- [ ] All 25 CyberWizard tests passing (currently 13/25)
- [ ] New hook tests: 15+ tests (5 per hook)
- [ ] New component tests: 10+ tests
- [ ] Total: 50+ tests, all passing

**Code Quality:**
- [ ] CyberWizard.tsx: 3300 → ~500 lines
- [ ] State variables: 30 → ~8
- [ ] No component over 300 lines
- [ ] All hooks under 100 lines

**Functionality:**
- [ ] All wizard features still work
- [ ] No visual regressions
- [ ] Performance same or better
- [ ] Accessibility maintained

---

## Timeline

**Day 1:**
- Claude: Extract useWizardSteps + useReceipt hooks
- GPT: Create StepNavigation component + useModelSelection hook
- Aux: Create WizardStep component

**Day 2:**
- All: Write comprehensive tests for new code
- Aux: Begin CyberWizard integration

**Day 3:**
- Aux: Complete integration, remove old code
- All: Fix failing tests, verify functionality
- Claude: Final test run + documentation

---

## Communication Protocol

**After each task completion, report:**
1. What was completed
2. Test results (X/Y passing)
3. Any blockers
4. Next task starting

**Handoff format:**
```
✅ COMPLETED: useWizardSteps hook
- File: hooks/useWizardSteps.ts (87 lines)
- Tests: 5/5 passing
- CyberWizard updated: lines 1200-1250 replaced with hook
- NEXT: Starting useReceipt hook
```

---

## File Structure After Refactor

```
frontend/src/
├── components/wizard/
│   ├── CyberWizard.tsx (500 lines, main orchestrator)
│   ├── StepNavigation.tsx (80 lines)
│   ├── WizardStep.tsx (150 lines)
│   ├── steps/
│   │   ├── IntroStep.tsx
│   │   ├── CheckboxStep.tsx
│   │   ├── TextareaStep.tsx
│   │   └── GroupboxStep.tsx
│   └── __tests__/
│       ├── CyberWizard.test.tsx (existing, now all passing)
│       ├── StepNavigation.test.tsx (new)
│       └── WizardStep.test.tsx (new)
├── hooks/
│   ├── useWizardSteps.ts (100 lines)
│   ├── useModelSelection.ts (120 lines)
│   ├── useReceipt.ts (80 lines)
│   └── __tests__/
│       ├── useWizardSteps.test.ts (new)
│       ├── useModelSelection.test.ts (new)
│       └── useReceipt.test.ts (new)
```

---

## START HERE

**Claude starts with:** `useWizardSteps` hook (Priority 1)
**GPT starts with:** `StepNavigation` component (Priority 1)  
**Aux starts with:** `WizardStep` component (Priority 1)

All work in parallel, communicate via handoff messages.

**Ready to begin?**
