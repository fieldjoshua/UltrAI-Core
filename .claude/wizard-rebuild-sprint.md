# CyberWizard V2 Rebuild - 2 Hour Sprint

**Goal:** Complete clean rebuild with all tests passing in 120 minutes

---

## Division of Labor (Parallel Execution)

### **CLAUDE** (40 min) - Core Hooks + Types

**T+0 to T+20: Create hooks**
- [ ] `hooks/useWizardSteps.ts` (navigation, keyboard)
- [ ] `hooks/useReceipt.ts` (cost calculation)
- [ ] `hooks/useOrchestration.ts` (API calls, status)

**T+20 to T+40: Tests**
- [ ] `hooks/__tests__/useWizardSteps.test.ts`
- [ ] `hooks/__tests__/useReceipt.test.ts`
- [ ] `hooks/__tests__/useOrchestration.test.ts`

**Handoff at T+40:** "✅ All hooks ready with tests passing"

---

### **GPT** (40 min) - UI Components

**T+0 to T+25: Create components**
- [ ] `wizard/StepNavigation.tsx` (step markers)
- [ ] `wizard/WizardStep.tsx` (step renderer)
- [ ] `wizard/Receipt.tsx` (cost display)
- [ ] `wizard/steps/` (IntroStep, CheckboxStep, TextareaStep, GroupboxStep)

**T+25 to T+40: Tests**
- [ ] `wizard/__tests__/StepNavigation.test.tsx`
- [ ] `wizard/__tests__/WizardStep.test.tsx`
- [ ] `wizard/__tests__/Receipt.test.tsx`

**Handoff at T+40:** "✅ All components ready with tests passing"

---

### **AUX** (40 min) - Model Selection + Step Types

**T+0 to T+20: Create model selection**
- [ ] `hooks/useModelSelection.ts` (preset logic, toggles)
- [ ] `components/wizard/ModelSelector.tsx` (UI for Premium/Speed/Budget)

**T+20 to T+40: Create step-specific components**
- [ ] `wizard/steps/IntroStep.tsx`
- [ ] `wizard/steps/GoalStep.tsx` (checkbox)
- [ ] `wizard/steps/QueryStep.tsx` (textarea)
- [ ] `wizard/steps/AnalysisStep.tsx` (groupbox)
- [ ] `wizard/steps/ModelStep.tsx` (uses ModelSelector)
- [ ] `wizard/steps/AddonsStep.tsx` (checkbox)

**Handoff at T+40:** "✅ Model selection + all step components ready"

---

## Integration Phase (All 3 Together)

### **T+40 to T+80: Build CyberWizardV2**

**Claude:** Assemble main CyberWizardV2.tsx using all hooks/components
**GPT:** Write integration tests for full wizard flow
**Aux:** Handle styling, accessibility, animations

```typescript
// CyberWizardV2.tsx (Claude builds this)
export default function CyberWizardV2() {
  const { currentStep, goToStep, handleKeyboard } = useWizardSteps();
  const { selectedModels, selectPreset } = useModelSelection();
  const { items, addItem, total } = useReceipt();
  const { startOrchestration, status } = useOrchestration();
  
  return (
    <div>
      <StepNavigation ... />
      <WizardStep ... />
      <Receipt ... />
    </div>
  );
}
```

---

### **T+80 to T+100: Testing & Polish**

**All 3:**
- [ ] Run full test suite (target: 50+ tests passing)
- [ ] Fix any integration bugs
- [ ] Verify all wizard features work
- [ ] Check accessibility

---

### **T+100 to T+120: Swap & Deploy**

**Claude:**
- [ ] Rename CyberWizard.tsx → CyberWizard.old.tsx
- [ ] Rename CyberWizardV2.tsx → CyberWizard.tsx
- [ ] Update imports in App.tsx
- [ ] Commit & push

**GPT:**
- [ ] Update tests to point to new wizard
- [ ] Delete old test mocks
- [ ] Verify CI passes

**Aux:**
- [ ] Final smoke test in browser
- [ ] Check all routes still work
- [ ] Confirm no regressions

---

## File Structure (New)

```
frontend/src/
├── components/wizard/
│   ├── CyberWizard.tsx (NEW - 400 lines)
│   ├── CyberWizard.old.tsx (backup)
│   ├── StepNavigation.tsx (80 lines)
│   ├── WizardStep.tsx (100 lines)
│   ├── Receipt.tsx (60 lines)
│   ├── ModelSelector.tsx (120 lines)
│   └── steps/
│       ├── IntroStep.tsx (80 lines)
│       ├── GoalStep.tsx (100 lines)
│       ├── QueryStep.tsx (120 lines)
│       ├── AnalysisStep.tsx (90 lines)
│       ├── ModelStep.tsx (100 lines)
│       └── AddonsStep.tsx (100 lines)
├── hooks/
│   ├── useWizardSteps.ts (100 lines)
│   ├── useModelSelection.ts (120 lines)
│   ├── useReceipt.ts (80 lines)
│   └── useOrchestration.ts (150 lines)
```

**Total: ~1600 lines** (vs 3300 old)

---

## Success Criteria

**Tests:**
- [ ] 25/25 existing CyberWizard tests passing
- [ ] 15+ new hook tests
- [ ] 10+ new component tests
- [ ] Total: 50+ tests, 100% passing

**Functionality:**
- [ ] All 6 wizard steps work
- [ ] Keyboard navigation works
- [ ] Model selection works (Premium/Speed/Budget/Custom)
- [ ] Receipt calculates correctly
- [ ] Orchestration triggers successfully
- [ ] Demo mode works

**Code Quality:**
- [ ] No component over 150 lines
- [ ] All hooks under 150 lines
- [ ] State isolated to relevant hook
- [ ] Full TypeScript types

---

## Communication Protocol

**Every 10 minutes, post update:**
```
[T+10] Claude: ✅ useWizardSteps done, starting useReceipt
[T+10] GPT: ⏳ StepNavigation 60% done
[T+10] Aux: ✅ useModelSelection done, starting step components
```

**At T+40, confirm handoff:**
```
✅ CLAUDE HANDOFF:
- useWizardSteps.ts (87 lines, 5 tests passing)
- useReceipt.ts (64 lines, 4 tests passing)
- useOrchestration.ts (142 lines, 6 tests passing)
- READY for integration
```

---

## START NOW

**Claude:** Create `hooks/useWizardSteps.ts` first
**GPT:** Create `wizard/StepNavigation.tsx` first
**Aux:** Create `hooks/useModelSelection.ts` first

**Timer starts NOW. Report at T+10.**

🚀 GO GO GO!
