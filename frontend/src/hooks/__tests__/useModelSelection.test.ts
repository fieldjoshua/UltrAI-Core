import { renderHook, act } from '@testing-library/react';
import { useModelSelection, ModelType, SelectionMode } from '../useModelSelection';

describe('useModelSelection', () => {
  describe('initial state', () => {
    it('should initialize with empty selectedModels and custom selectionMode', () => {
      const { result } = renderHook(() => useModelSelection());

      expect(result.current.selectedModels).toEqual([]);
      expect(result.current.selectionMode).toBe('custom');
    });
  });

  describe('selectPreset', () => {
    it('should select premium preset correctly', () => {
      const { result } = renderHook(() => useModelSelection());

      act(() => {
        result.current.selectPreset('premium');
      });

      expect(result.current.selectedModels).toEqual(['gpt-4', 'claude-3-opus', 'gemini-1.5-pro']);
      expect(result.current.selectionMode).toBe('premium');
    });

    it('should select speed preset correctly', () => {
      const { result } = renderHook(() => useModelSelection());

      act(() => {
        result.current.selectPreset('speed');
      });

      expect(result.current.selectedModels).toEqual(['gpt-4o-mini', 'claude-3-haiku']);
      expect(result.current.selectionMode).toBe('speed');
    });

    it('should select budget preset correctly', () => {
      const { result } = renderHook(() => useModelSelection());

      act(() => {
        result.current.selectPreset('budget');
      });

      expect(result.current.selectedModels).toEqual(['gpt-3.5-turbo']);
      expect(result.current.selectionMode).toBe('budget');
    });

    it('should allow switching between presets', () => {
      const { result } = renderHook(() => useModelSelection());

      act(() => {
        result.current.selectPreset('premium');
      });

      expect(result.current.selectedModels).toEqual(['gpt-4', 'claude-3-opus', 'gemini-1.5-pro']);

      act(() => {
        result.current.selectPreset('budget');
      });

      expect(result.current.selectedModels).toEqual(['gpt-3.5-turbo']);
      expect(result.current.selectionMode).toBe('budget');
    });
  });

  describe('toggleModel', () => {
    it('should add a model when toggling an unselected model', () => {
      const { result } = renderHook(() => useModelSelection());

      act(() => {
        result.current.toggleModel('gpt-4');
      });

      expect(result.current.selectedModels).toEqual(['gpt-4']);
      expect(result.current.selectionMode).toBe('custom');
    });

    it('should remove a model when toggling a selected model', () => {
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

    it('should switch to preset mode when selection matches preset', () => {
      const { result } = renderHook(() => useModelSelection());

      // Manually select models that match premium preset
      act(() => {
        result.current.toggleModel('gpt-4');
        result.current.toggleModel('claude-3-opus');
        result.current.toggleModel('gemini-1.5-pro');
      });

      expect(result.current.selectedModels).toEqual(['gpt-4', 'claude-3-opus', 'gemini-1.5-pro']);
      expect(result.current.selectionMode).toBe('premium');
    });

    it('should switch back to custom mode when selection no longer matches preset', () => {
      const { result } = renderHook(() => useModelSelection());

      // Select premium preset first
      act(() => {
        result.current.selectPreset('premium');
      });

      expect(result.current.selectionMode).toBe('premium');

      // Remove one model to break preset match
      act(() => {
        result.current.toggleModel('gpt-4');
      });

      expect(result.current.selectionMode).toBe('custom');
    });
  });

  describe('isModelSelected', () => {
    it('should return true for selected models', () => {
      const { result } = renderHook(() => useModelSelection());

      act(() => {
        result.current.toggleModel('gpt-4');
      });

      expect(result.current.isModelSelected('gpt-4')).toBe(true);
    });

    it('should return false for unselected models', () => {
      const { result } = renderHook(() => useModelSelection());

      expect(result.current.isModelSelected('gpt-4')).toBe(false);
    });

    it('should update correctly after toggling models', () => {
      const { result } = renderHook(() => useModelSelection());

      act(() => {
        result.current.toggleModel('gpt-4');
      });

      expect(result.current.isModelSelected('gpt-4')).toBe(true);

      act(() => {
        result.current.toggleModel('gpt-4');
      });

      expect(result.current.isModelSelected('gpt-4')).toBe(false);
    });
  });

  describe('clearSelection', () => {
    it('should clear all selected models and reset to custom mode', () => {
      const { result } = renderHook(() => useModelSelection());

      act(() => {
        result.current.selectPreset('premium');
      });

      expect(result.current.selectedModels.length).toBeGreaterThan(0);
      expect(result.current.selectionMode).toBe('premium');

      act(() => {
        result.current.clearSelection();
      });

      expect(result.current.selectedModels).toEqual([]);
      expect(result.current.selectionMode).toBe('custom');
    });
  });

  describe('complex scenarios', () => {
    it('should handle selecting preset then adding custom models', () => {
      const { result } = renderHook(() => useModelSelection());

      // Start with premium preset
      act(() => {
        result.current.selectPreset('premium');
      });

      expect(result.current.selectionMode).toBe('premium');
      expect(result.current.selectedModels).toEqual(['gpt-4', 'claude-3-opus', 'gemini-1.5-pro']);

      // Add an additional model
      act(() => {
        result.current.toggleModel('gpt-3.5-turbo');
      });

      expect(result.current.selectedModels).toEqual(['gpt-4', 'claude-3-opus', 'gemini-1.5-pro', 'gpt-3.5-turbo']);
      expect(result.current.selectionMode).toBe('custom');
    });

    it('should handle removing models from preset and returning to preset when match is restored', () => {
      const { result } = renderHook(() => useModelSelection());

      // Start with premium preset
      act(() => {
        result.current.selectPreset('premium');
      });

      expect(result.current.selectionMode).toBe('premium');

      // Remove one model
      act(() => {
        result.current.toggleModel('gpt-4');
      });

      expect(result.current.selectionMode).toBe('custom');
      expect(result.current.selectedModels).toEqual(['claude-3-opus', 'gemini-1.5-pro']);

      // Add the model back
      act(() => {
        result.current.toggleModel('gpt-4');
      });

      expect(result.current.selectionMode).toBe('premium');
      expect(result.current.selectedModels).toEqual(['claude-3-opus', 'gemini-1.5-pro', 'gpt-4']);
    });
  });

  describe('edge cases', () => {
    it('should handle toggling a model that is already selected', () => {
      const { result } = renderHook(() => useModelSelection());

      act(() => {
        result.current.toggleModel('gpt-4');
        result.current.toggleModel('gpt-4'); // Toggle again
      });

      expect(result.current.selectedModels).toEqual([]);
      expect(result.current.selectionMode).toBe('custom');
    });

    it('should handle selecting all models manually to match premium preset', () => {
      const { result } = renderHook(() => useModelSelection());

      // Select all premium models individually
      act(() => {
        result.current.toggleModel('gpt-4');
        result.current.toggleModel('claude-3-opus');
        result.current.toggleModel('gemini-1.5-pro');
      });

      expect(result.current.selectedModels).toEqual(['gpt-4', 'claude-3-opus', 'gemini-1.5-pro']);
      expect(result.current.selectionMode).toBe('premium');
    });
  });
});