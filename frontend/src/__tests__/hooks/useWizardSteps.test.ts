import { renderHook, act } from '@testing-library/react';
import { useWizardSteps } from '../../hooks/useWizardSteps';

const mockSteps = [
  { title: '0. Intro', color: 'mint', type: 'intro' },
  { title: '1. Goals', color: 'mint', type: 'checkbox' },
  { title: '2. Query', color: 'blue', type: 'textarea' },
  { title: '3. Models', color: 'purple', type: 'checkbox' },
];

describe('useWizardSteps', () => {
  it('initializes with step 0', () => {
    const { result } = renderHook(() => useWizardSteps(mockSteps));
    expect(result.current.currentStep).toBe(0);
    expect(result.current.isFirstStep).toBe(true);
    expect(result.current.canGoBack).toBe(false);
  });

  it('navigates to specific step', () => {
    const { result } = renderHook(() => useWizardSteps(mockSteps));
    
    act(() => {
      result.current.goToStep(2);
    });
    
    expect(result.current.currentStep).toBe(2);
    expect(result.current.stepHistory).toEqual([0, 2]);
  });

  it('navigates forward with goNext', () => {
    const { result } = renderHook(() => useWizardSteps(mockSteps));
    
    act(() => {
      result.current.goNext();
    });
    
    expect(result.current.currentStep).toBe(1);
  });

  it('navigates backward with goPrevious', () => {
    const { result } = renderHook(() => useWizardSteps(mockSteps));
    
    act(() => {
      result.current.goToStep(2);
    });
    
    act(() => {
      result.current.goPrevious();
    });
    
    expect(result.current.currentStep).toBe(1);
  });

  it('goes back through history', () => {
    const { result } = renderHook(() => useWizardSteps(mockSteps));
    
    act(() => {
      result.current.goToStep(1);
      result.current.goToStep(2);
      result.current.goToStep(3);
    });
    
    act(() => {
      result.current.goBack();
    });
    
    expect(result.current.currentStep).toBe(2);
    
    act(() => {
      result.current.goBack();
    });
    
    expect(result.current.currentStep).toBe(1);
  });

  it('does not go below step 0', () => {
    const { result } = renderHook(() => useWizardSteps(mockSteps));
    
    act(() => {
      result.current.goPrevious();
    });
    
    expect(result.current.currentStep).toBe(0);
  });

  it('does not go beyond last step', () => {
    const { result } = renderHook(() => useWizardSteps(mockSteps));
    
    act(() => {
      result.current.goToStep(3);
    });
    
    act(() => {
      result.current.goNext();
    });
    
    expect(result.current.currentStep).toBe(3);
    expect(result.current.isLastStep).toBe(true);
  });

  it('provides correct canGoNext/canGoBack flags', () => {
    const { result } = renderHook(() => useWizardSteps(mockSteps));
    
    // At step 0
    expect(result.current.canGoBack).toBe(false);
    expect(result.current.canGoNext).toBe(true);
    
    // At middle step
    act(() => {
      result.current.goToStep(2);
    });
    expect(result.current.canGoBack).toBe(true);
    expect(result.current.canGoNext).toBe(true);
    
    // At last step
    act(() => {
      result.current.goToStep(3);
    });
    expect(result.current.canGoBack).toBe(true);
    expect(result.current.canGoNext).toBe(false);
  });

  it('handles keyboard navigation with ArrowRight', () => {
    const { result } = renderHook(() => useWizardSteps(mockSteps));
    
    const mockEvent = {
      key: 'ArrowRight',
      preventDefault: jest.fn(),
      target: document.createElement('div'),
    } as any;
    
    act(() => {
      result.current.handleKeyboard(mockEvent);
    });
    
    expect(result.current.currentStep).toBe(1);
    expect(mockEvent.preventDefault).toHaveBeenCalled();
  });

  it('handles keyboard navigation with ArrowLeft', () => {
    const { result } = renderHook(() => useWizardSteps(mockSteps));
    
    act(() => {
      result.current.goToStep(2);
    });
    
    const mockEvent = {
      key: 'ArrowLeft',
      preventDefault: jest.fn(),
      target: document.createElement('div'),
    } as any;
    
    act(() => {
      result.current.handleKeyboard(mockEvent);
    });
    
    expect(result.current.currentStep).toBe(1);
  });

  it('handles Enter key on step 0', () => {
    const { result } = renderHook(() => useWizardSteps(mockSteps));
    
    const mockEvent = {
      key: 'Enter',
      preventDefault: jest.fn(),
      target: document.createElement('div'),
    } as any;
    
    act(() => {
      result.current.handleKeyboard(mockEvent);
    });
    
    expect(result.current.currentStep).toBe(1);
  });

  it('ignores keyboard events when typing in input', () => {
    const { result } = renderHook(() => useWizardSteps(mockSteps));
    
    const mockEvent = {
      key: 'ArrowRight',
      preventDefault: jest.fn(),
      target: document.createElement('input'),
    } as any;
    
    act(() => {
      result.current.handleKeyboard(mockEvent);
    });
    
    expect(result.current.currentStep).toBe(0);
    expect(mockEvent.preventDefault).not.toHaveBeenCalled();
  });
});
