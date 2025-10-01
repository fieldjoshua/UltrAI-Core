import { renderHook, act } from '@testing-library/react';
import { useModelSelection, type ModelType } from '../../hooks/useModelSelection';

describe('useModelSelection', () => {
  describe('initialization', () => {
    it('should initialize with empty selection and multiple mode by default', () => {
      const { result } = renderHook(() => useModelSelection());

      expect(result.current.selectedModels).toEqual([]);
      expect(result.current.selectionMode).toBe('multiple');
      expect(result.current.presets).toBeDefined();
    });

    it('should initialize with specified mode', () => {
      const { result } = renderHook(() => useModelSelection('single'));

      expect(result.current.selectionMode).toBe('single');
      expect(result.current.selectedModels).toEqual([]);
    });
  });

  describe('preset selection', () => {
    it('should select premium preset correctly', () => {
      const { result } = renderHook(() => useModelSelection());

      act(() => {
        result.current.selectPreset('premium');
      });

      expect(result.current.selectedModels).toEqual(['gpt-4', 'claude-3-opus', 'gemini-1.5-pro']);
    });

    it('should select speed preset correctly', () => {
      const { result } = renderHook(() => useModelSelection());

      act(() => {
        result.current.selectPreset('speed');
      });

      expect(result.current.selectedModels).toEqual(['gpt-4o-mini', 'claude-3-haiku']);
    });

    it('should select budget preset correctly', () => {
      const { result } = renderHook(() => useModelSelection());

      act(() => {
        result.current.selectPreset('budget');
      });

      expect(result.current.selectedModels).toEqual(['gpt-3.5-turbo']);
    });

    it('should handle preset selection in single mode', () => {
      const { result } = renderHook(() => useModelSelection('single'));

      act(() => {
        result.current.selectPreset('premium');
      });

      // Should only select the first model in single mode
      expect(result.current.selectedModels).toEqual(['gpt-4']);
    });
  });

  describe('model toggling', () => {
    it('should toggle model selection in multiple mode', () => {
      const { result } = renderHook(() => useModelSelection('multiple'));

      // Add a model
      act(() => {
        result.current.toggleModel('gpt-4');
      });

      expect(result.current.selectedModels).toEqual(['gpt-4']);

      // Add another model
      act(() => {
        result.current.toggleModel('claude-3-opus');
      });

      expect(result.current.selectedModels).toEqual(['gpt-4', 'claude-3-opus']);

      // Remove a model
      act(() => {
        result.current.toggleModel('gpt-4');
      });

      expect(result.current.selectedModels).toEqual(['claude-3-opus']);
    });

    it('should handle model selection in single mode', () => {
      const { result } = renderHook(() => useModelSelection('single'));

      // Select a model
      act(() => {
        result.current.toggleModel('gpt-4');
      });

      expect(result.current.selectedModels).toEqual(['gpt-4']);

      // Select another model (should replace the first)
      act(() => {
        result.current.toggleModel('claude-3-opus');
      });

      expect(result.current.selectedModels).toEqual(['claude-3-opus']);

      // Deselect the same model (should clear selection)
      act(() => {
        result.current.toggleModel('claude-3-opus');
      });

      expect(result.current.selectedModels).toEqual([]);
    });
  });

  describe('selection mode switching', () => {
    it('should switch from multiple to single mode', () => {
      const { result } = renderHook(() => useModelSelection('multiple'));

      // Select multiple models
      act(() => {
        result.current.toggleModel('gpt-4');
        result.current.toggleModel('claude-3-opus');
      });

      expect(result.current.selectedModels).toEqual(['gpt-4', 'claude-3-opus']);
      expect(result.current.selectionMode).toBe('multiple');

      // Switch to single mode
      act(() => {
        result.current.setSelectionMode('single');
      });

      // Should keep only the first selected model
      expect(result.current.selectedModels).toEqual(['gpt-4']);
      expect(result.current.selectionMode).toBe('single');
    });

    it('should switch from single to multiple mode', () => {
      const { result } = renderHook(() => useModelSelection('single'));

      // Select a model
      act(() => {
        result.current.toggleModel('gpt-4');
      });

      expect(result.current.selectedModels).toEqual(['gpt-4']);
      expect(result.current.selectionMode).toBe('single');

      // Switch to multiple mode
      act(() => {
        result.current.setSelectionMode('multiple');
      });

      expect(result.current.selectedModels).toEqual(['gpt-4']);
      expect(result.current.selectionMode).toBe('multiple');
    });
  });

  describe('utility functions', () => {
    it('should check if model is selected correctly', () => {
      const { result } = renderHook(() => useModelSelection());

      expect(result.current.isModelSelected('gpt-4')).toBe(false);

      act(() => {
        result.current.toggleModel('gpt-4');
      });

      expect(result.current.isModelSelected('gpt-4')).toBe(true);
      expect(result.current.isModelSelected('claude-3-opus')).toBe(false);
    });

    it('should clear selection correctly', () => {
      const { result } = renderHook(() => useModelSelection());

      // Select some models
      act(() => {
        result.current.selectPreset('premium');
      });

      expect(result.current.selectedModels).toHaveLength(3);

      // Clear selection
      act(() => {
        result.current.clearSelection();
      });

      expect(result.current.selectedModels).toEqual([]);
    });
  });

  describe('presets data', () => {
    it('should have correct preset configurations', () => {
      const { result } = renderHook(() => useModelSelection());

      const { presets } = result.current;

      expect(presets.premium.models).toEqual(['gpt-4', 'claude-3-opus', 'gemini-1.5-pro']);
      expect(presets.speed.models).toEqual(['gpt-4o-mini', 'claude-3-haiku']);
      expect(presets.budget.models).toEqual(['gpt-3.5-turbo']);

      expect(presets.premium.name).toBe('Premium');
      expect(presets.speed.name).toBe('Speed');
      expect(presets.budget.name).toBe('Budget');

      expect(presets.premium.description).toBe('Highest quality models for complex analysis');
      expect(presets.speed.description).toBe('Fast processing with good quality');
      expect(presets.budget.description).toBe('Cost-effective option for basic tasks');
    });
  });

  describe('edge cases', () => {
    it('should handle toggling non-existent model gracefully', () => {
      const { result } = renderHook(() => useModelSelection());

      // This should not throw an error
      act(() => {
        result.current.toggleModel('non-existent-model' as ModelType);
      });

      expect(result.current.selectedModels).toEqual([]);
    });

    it('should handle selecting same preset multiple times', () => {
      const { result } = renderHook(() => useModelSelection());

      act(() => {
        result.current.selectPreset('premium');
      });

      const firstSelection = result.current.selectedModels;

      act(() => {
        result.current.selectPreset('premium');
      });

      expect(result.current.selectedModels).toEqual(firstSelection);
    });

    it('should handle mode switching with empty selection', () => {
      const { result } = renderHook(() => useModelSelection('multiple'));

      // Switch modes with no selection
      act(() => {
        result.current.setSelectionMode('single');
      });

      expect(result.current.selectedModels).toEqual([]);
      expect(result.current.selectionMode).toBe('single');
    });
  });

  describe('integration scenarios', () => {
    it('should work correctly in a typical usage pattern', () => {
      const { result } = renderHook(() => useModelSelection());

      // Start with preset selection
      act(() => {
        result.current.selectPreset('speed');
      });

      expect(result.current.selectedModels).toEqual(['gpt-4o-mini', 'claude-3-haiku']);

      // Add an individual model
      act(() => {
        result.current.toggleModel('gpt-4');
      });

      expect(result.current.selectedModels).toEqual(['gpt-4o-mini', 'claude-3-haiku', 'gpt-4']);

      // Remove one model
      act(() => {
        result.current.toggleModel('claude-3-haiku');
      });

      expect(result.current.selectedModels).toEqual(['gpt-4o-mini', 'gpt-4']);

      // Switch to single mode
      act(() => {
        result.current.setSelectionMode('single');
      });

      expect(result.current.selectedModels).toEqual(['gpt-4o-mini']);

      // Clear and start over
      act(() => {
        result.current.clearSelection();
        result.current.selectPreset('budget');
      });

      expect(result.current.selectedModels).toEqual(['gpt-3.5-turbo']);
    });
  });
});