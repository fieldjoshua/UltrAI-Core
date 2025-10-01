import { renderHook, act } from '@testing-library/react';
import { useModelSelection, presets } from '../../hooks/useModelSelection';

describe('useModelSelection', () => {
  it('should initialize with empty selectedModels and null selectionMode', () => {
    const { result } = renderHook(() => useModelSelection());

    expect(result.current.selectedModels).toEqual([]);
    expect(result.current.selectionMode).toBeNull();
  });

  it('should select premium preset correctly', () => {
    const { result } = renderHook(() => useModelSelection());

    act(() => {
      result.current.selectPreset('premium');
    });

    expect(result.current.selectedModels).toEqual(presets.premium);
    expect(result.current.selectionMode).toBe('premium');
  });

  it('should select speed preset correctly', () => {
    const { result } = renderHook(() => useModelSelection());

    act(() => {
      result.current.selectPreset('speed');
    });

    expect(result.current.selectedModels).toEqual(presets.speed);
    expect(result.current.selectionMode).toBe('speed');
  });

  it('should select budget preset correctly', () => {
    const { result } = renderHook(() => useModelSelection());

    act(() => {
      result.current.selectPreset('budget');
    });

    expect(result.current.selectedModels).toEqual(presets.budget);
    expect(result.current.selectionMode).toBe('budget');
  });

  it('should toggle models in selectedModels', () => {
    const { result } = renderHook(() => useModelSelection());

    act(() => {
      result.current.selectPreset('premium');
    });

    expect(result.current.selectedModels).toContain('gpt-4');

    act(() => {
      result.current.toggleModel('gpt-4');
    });

    expect(result.current.selectedModels).not.toContain('gpt-4');
  });

  it('should add model when toggling unselected model', () => {
    const { result } = renderHook(() => useModelSelection());

    act(() => {
      result.current.toggleModel('gpt-4');
    });

    expect(result.current.selectedModels).toContain('gpt-4');
  });

  it('should handle multiple toggles correctly', () => {
    const { result } = renderHook(() => useModelSelection());

    act(() => {
      result.current.toggleModel('gpt-4');
      result.current.toggleModel('claude-3-opus');
    });

    expect(result.current.selectedModels).toEqual(['gpt-4', 'claude-3-opus']);

    act(() => {
      result.current.toggleModel('gpt-4');
    });

    expect(result.current.selectedModels).toEqual(['claude-3-opus']);
  });
});