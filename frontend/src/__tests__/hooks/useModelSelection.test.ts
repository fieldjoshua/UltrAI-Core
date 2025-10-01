import { renderHook, act } from '@testing-library/react';
import { useModelSelection, MODEL_PRESETS } from '../../hooks/useModelSelection';

describe('useModelSelection', () => {
  it('initializes with empty selectedModels and custom selectionMode', () => {
    const { result } = renderHook(() => useModelSelection());

    expect(result.current.selectedModels).toEqual([]);
    expect(result.current.selectionMode).toBe('custom');
    expect(result.current.availableModels).toEqual([
      'gpt-4', 'claude-3-opus', 'gemini-1.5-pro',
      'gpt-4o-mini', 'claude-3-haiku',
      'gpt-3.5-turbo'
    ]);
  });

  it('selects premium preset correctly', () => {
    const { result } = renderHook(() => useModelSelection());

    act(() => {
      result.current.selectPreset('premium');
    });

    expect(result.current.selectedModels).toEqual(MODEL_PRESETS.premium);
    expect(result.current.selectionMode).toBe('premium');
  });

  it('selects speed preset correctly', () => {
    const { result } = renderHook(() => useModelSelection());

    act(() => {
      result.current.selectPreset('speed');
    });

    expect(result.current.selectedModels).toEqual(MODEL_PRESETS.speed);
    expect(result.current.selectionMode).toBe('speed');
  });

  it('selects budget preset correctly', () => {
    const { result } = renderHook(() => useModelSelection());

    act(() => {
      result.current.selectPreset('budget');
    });

    expect(result.current.selectedModels).toEqual(MODEL_PRESETS.budget);
    expect(result.current.selectionMode).toBe('budget');
  });

  it('toggles model selection and switches to custom mode', () => {
    const { result } = renderHook(() => useModelSelection());

    // Initially no models selected
    expect(result.current.selectedModels).toEqual([]);

    // Add a model
    act(() => {
      result.current.toggleModel('gpt-4');
    });

    expect(result.current.selectedModels).toEqual(['gpt-4']);
    expect(result.current.selectionMode).toBe('custom');
    expect(result.current.isModelSelected('gpt-4')).toBe(true);
  });

  it('toggles model off when already selected', () => {
    const { result } = renderHook(() => useModelSelection());

    // Add a model
    act(() => {
      result.current.toggleModel('gpt-4');
    });

    expect(result.current.selectedModels).toEqual(['gpt-4']);

    // Remove the same model
    act(() => {
      result.current.toggleModel('gpt-4');
    });

    expect(result.current.selectedModels).toEqual([]);
    expect(result.current.isModelSelected('gpt-4')).toBe(false);
  });

  it('clears all selections and resets to custom mode', () => {
    const { result } = renderHook(() => useModelSelection());

    // Select a preset first
    act(() => {
      result.current.selectPreset('premium');
    });

    expect(result.current.selectedModels).toEqual(MODEL_PRESETS.premium);
    expect(result.current.selectionMode).toBe('premium');

    // Clear selections
    act(() => {
      result.current.clearSelection();
    });

    expect(result.current.selectedModels).toEqual([]);
    expect(result.current.selectionMode).toBe('custom');
  });

  it('correctly identifies selected models', () => {
    const { result } = renderHook(() => useModelSelection());

    // Initially no models are selected
    expect(result.current.isModelSelected('gpt-4')).toBe(false);
    expect(result.current.isModelSelected('claude-3-opus')).toBe(false);

    // Add one model
    act(() => {
      result.current.toggleModel('gpt-4');
    });

    expect(result.current.isModelSelected('gpt-4')).toBe(true);
    expect(result.current.isModelSelected('claude-3-opus')).toBe(false);

    // Add another model
    act(() => {
      result.current.toggleModel('claude-3-opus');
    });

    expect(result.current.isModelSelected('gpt-4')).toBe(true);
    expect(result.current.isModelSelected('claude-3-opus')).toBe(true);
  });

  it('maintains custom mode when manually toggling models', () => {
    const { result } = renderHook(() => useModelSelection());

    // Start with premium preset
    act(() => {
      result.current.selectPreset('premium');
    });

    expect(result.current.selectionMode).toBe('premium');

    // Toggle a model manually - should switch to custom
    act(() => {
      result.current.toggleModel('gpt-4o-mini');
    });

    expect(result.current.selectionMode).toBe('custom');
    expect(result.current.selectedModels).toContain('gpt-4o-mini');
  });

  it('handles multiple model toggles correctly', () => {
    const { result } = renderHook(() => useModelSelection());

    // Add multiple models
    act(() => {
      result.current.toggleModel('gpt-4');
      result.current.toggleModel('claude-3-haiku');
      result.current.toggleModel('gpt-3.5-turbo');
    });

    expect(result.current.selectedModels).toEqual([
      'gpt-4',
      'claude-3-haiku',
      'gpt-3.5-turbo'
    ]);
    expect(result.current.selectionMode).toBe('custom');

    // Remove one model
    act(() => {
      result.current.toggleModel('claude-3-haiku');
    });

    expect(result.current.selectedModels).toEqual([
      'gpt-4',
      'gpt-3.5-turbo'
    ]);
  });

  it('switches between presets correctly', () => {
    const { result } = renderHook(() => useModelSelection());

    // Select premium
    act(() => {
      result.current.selectPreset('premium');
    });

    expect(result.current.selectedModels).toEqual(MODEL_PRESETS.premium);
    expect(result.current.selectionMode).toBe('premium');

    // Switch to speed
    act(() => {
      result.current.selectPreset('speed');
    });

    expect(result.current.selectedModels).toEqual(MODEL_PRESETS.speed);
    expect(result.current.selectionMode).toBe('speed');

    // Switch to budget
    act(() => {
      result.current.selectPreset('budget');
    });

    expect(result.current.selectedModels).toEqual(MODEL_PRESETS.budget);
    expect(result.current.selectionMode).toBe('budget');
  });

  it('handles edge case of selecting preset with no models', () => {
    const { result } = renderHook(() => useModelSelection());

    // This shouldn't happen in practice, but test the robustness
    act(() => {
      result.current.selectPreset('custom');
    });

    expect(result.current.selectedModels).toEqual([]);
    expect(result.current.selectionMode).toBe('custom');
  });

  it('maintains availableModels as flattened preset array', () => {
    const { result } = renderHook(() => useModelSelection());

    const expectedModels = Object.values(MODEL_PRESETS).flat();
    expect(result.current.availableModels).toEqual(expectedModels);
    expect(new Set(result.current.availableModels).size).toBe(expectedModels.length);
  });
});