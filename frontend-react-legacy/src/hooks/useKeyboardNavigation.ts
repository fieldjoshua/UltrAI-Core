import { useEffect, useCallback } from 'react';
import { KEYBOARD_KEYS } from '../utils/accessibility';

interface KeyboardNavigationOptions {
  onEnter?: () => void;
  onEscape?: () => void;
  onArrowUp?: () => void;
  onArrowDown?: () => void;
  onArrowLeft?: () => void;
  onArrowRight?: () => void;
  onHome?: () => void;
  onEnd?: () => void;
  onTab?: (e: KeyboardEvent) => void;
  enabled?: boolean;
}

export const useKeyboardNavigation = ({
  onEnter,
  onEscape,
  onArrowUp,
  onArrowDown,
  onArrowLeft,
  onArrowRight,
  onHome,
  onEnd,
  onTab,
  enabled = true,
}: KeyboardNavigationOptions = {}) => {
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!enabled) return;

      switch (e.key) {
        case KEYBOARD_KEYS.ENTER:
          onEnter?.();
          break;
        case KEYBOARD_KEYS.ESCAPE:
          onEscape?.();
          break;
        case KEYBOARD_KEYS.ARROW_UP:
          onArrowUp?.();
          break;
        case KEYBOARD_KEYS.ARROW_DOWN:
          onArrowDown?.();
          break;
        case KEYBOARD_KEYS.ARROW_LEFT:
          onArrowLeft?.();
          break;
        case KEYBOARD_KEYS.ARROW_RIGHT:
          onArrowRight?.();
          break;
        case KEYBOARD_KEYS.HOME:
          onHome?.();
          break;
        case KEYBOARD_KEYS.END:
          onEnd?.();
          break;
        case KEYBOARD_KEYS.TAB:
          onTab?.(e);
          break;
      }
    },
    [
      enabled,
      onEnter,
      onEscape,
      onArrowUp,
      onArrowDown,
      onArrowLeft,
      onArrowRight,
      onHome,
      onEnd,
      onTab,
    ]
  );

  useEffect(() => {
    if (enabled) {
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }
  }, [enabled, handleKeyDown]);

  return {
    isEnabled: enabled,
  };
};
