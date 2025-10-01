import { useEffect, useCallback, useRef } from 'react';

export interface KeyboardNavigationHandlers {
  onEnter?: (e: KeyboardEvent) => void;
  onEscape?: (e: KeyboardEvent) => void;
  onArrowUp?: (e: KeyboardEvent) => void;
  onArrowDown?: (e: KeyboardEvent) => void;
  onArrowLeft?: (e: KeyboardEvent) => void;
  onArrowRight?: (e: KeyboardEvent) => void;
  onHome?: (e: KeyboardEvent) => void;
  onEnd?: (e: KeyboardEvent) => void;
  onTab?: (e: KeyboardEvent) => void;
  onSpace?: (e: KeyboardEvent) => void;
}

export interface KeyboardNavigationOptions extends KeyboardNavigationHandlers {
  enabled?: boolean;
  preventDefault?: boolean | string[];
  stopPropagation?: boolean;
  ignoreInputs?: boolean;
}

const KEY_MAP = {
  Enter: 'onEnter',
  Escape: 'onEscape',
  ArrowUp: 'onArrowUp',
  ArrowDown: 'onArrowDown',
  ArrowLeft: 'onArrowLeft',
  ArrowRight: 'onArrowRight',
  Home: 'onHome',
  End: 'onEnd',
  Tab: 'onTab',
  ' ': 'onSpace',
} as const;

const isInputElement = (target: EventTarget | null): boolean => {
  if (!target || !(target instanceof HTMLElement)) return false;
  const tagName = target.tagName.toLowerCase();
  return (
    tagName === 'input' ||
    tagName === 'textarea' ||
    tagName === 'select' ||
    target.isContentEditable
  );
};

export function useKeyboardNavigation(options: KeyboardNavigationOptions = {}) {
  const {
    enabled = true,
    preventDefault = false,
    stopPropagation = false,
    ignoreInputs = true,
    ...handlers
  } = options;

  const handlersRef = useRef(handlers);

  useEffect(() => {
    handlersRef.current = handlers;
  }, [handlers]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!enabled) return;

      if (ignoreInputs && isInputElement(e.target)) return;

      const handlerKey = KEY_MAP[e.key as keyof typeof KEY_MAP];
      if (!handlerKey) return;

      const handler = handlersRef.current[handlerKey];
      if (!handler) return;

      const shouldPreventDefault =
        preventDefault === true ||
        (Array.isArray(preventDefault) && preventDefault.includes(e.key));

      if (shouldPreventDefault) {
        e.preventDefault();
      }

      if (stopPropagation) {
        e.stopPropagation();
      }

      handler(e);
    },
    [enabled, preventDefault, stopPropagation, ignoreInputs]
  );

  useEffect(() => {
    if (!enabled) return;

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [enabled, handleKeyDown]);

  return {
    isEnabled: enabled,
  };
}
