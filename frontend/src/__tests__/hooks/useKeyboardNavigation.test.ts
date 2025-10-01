import { renderHook } from '@testing-library/react';
import { jest } from '@jest/globals';
import { useKeyboardNavigation } from '../../hooks/useKeyboardNavigation';

describe('useKeyboardNavigation', () => {
  const createKeyboardEvent = (key: string, target?: HTMLElement): KeyboardEvent => {
    const event = new KeyboardEvent('keydown', {
      key,
      bubbles: true,
      cancelable: true,
    });
    
    if (target) {
      Object.defineProperty(event, 'target', {
        value: target,
        writable: false,
      });
    }
    
    return event;
  };

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic functionality', () => {
    it('should initialize with enabled state', () => {
      const { result } = renderHook(() => useKeyboardNavigation());
      
      expect(result.current.isEnabled).toBe(true);
    });

    it('should respect enabled prop', () => {
      const { result } = renderHook(() => useKeyboardNavigation({ enabled: false }));
      
      expect(result.current.isEnabled).toBe(false);
    });

    it('should call onEnter handler when Enter is pressed', () => {
      const onEnter = jest.fn();
      renderHook(() => useKeyboardNavigation({ onEnter }));
      
      window.dispatchEvent(createKeyboardEvent('Enter'));
      
      expect(onEnter).toHaveBeenCalledTimes(1);
    });

    it('should call onEscape handler when Escape is pressed', () => {
      const onEscape = jest.fn();
      renderHook(() => useKeyboardNavigation({ onEscape }));
      
      window.dispatchEvent(createKeyboardEvent('Escape'));
      
      expect(onEscape).toHaveBeenCalledTimes(1);
    });

    it('should not call handlers when disabled', () => {
      const onEnter = jest.fn();
      renderHook(() => useKeyboardNavigation({ onEnter, enabled: false }));
      
      window.dispatchEvent(createKeyboardEvent('Enter'));
      
      expect(onEnter).not.toHaveBeenCalled();
    });
  });

  describe('Arrow key navigation', () => {
    it('should call onArrowUp when ArrowUp is pressed', () => {
      const onArrowUp = jest.fn();
      renderHook(() => useKeyboardNavigation({ onArrowUp }));
      
      window.dispatchEvent(createKeyboardEvent('ArrowUp'));
      
      expect(onArrowUp).toHaveBeenCalledTimes(1);
    });

    it('should call onArrowDown when ArrowDown is pressed', () => {
      const onArrowDown = jest.fn();
      renderHook(() => useKeyboardNavigation({ onArrowDown }));
      
      window.dispatchEvent(createKeyboardEvent('ArrowDown'));
      
      expect(onArrowDown).toHaveBeenCalledTimes(1);
    });

    it('should call onArrowLeft when ArrowLeft is pressed', () => {
      const onArrowLeft = jest.fn();
      renderHook(() => useKeyboardNavigation({ onArrowLeft }));
      
      window.dispatchEvent(createKeyboardEvent('ArrowLeft'));
      
      expect(onArrowLeft).toHaveBeenCalledTimes(1);
    });

    it('should call onArrowRight when ArrowRight is pressed', () => {
      const onArrowRight = jest.fn();
      renderHook(() => useKeyboardNavigation({ onArrowRight }));
      
      window.dispatchEvent(createKeyboardEvent('ArrowRight'));
      
      expect(onArrowRight).toHaveBeenCalledTimes(1);
    });
  });

  describe('Navigation keys', () => {
    it('should call onHome when Home is pressed', () => {
      const onHome = jest.fn();
      renderHook(() => useKeyboardNavigation({ onHome }));
      
      window.dispatchEvent(createKeyboardEvent('Home'));
      
      expect(onHome).toHaveBeenCalledTimes(1);
    });

    it('should call onEnd when End is pressed', () => {
      const onEnd = jest.fn();
      renderHook(() => useKeyboardNavigation({ onEnd }));
      
      window.dispatchEvent(createKeyboardEvent('End'));
      
      expect(onEnd).toHaveBeenCalledTimes(1);
    });

    it('should call onTab when Tab is pressed', () => {
      const onTab = jest.fn();
      renderHook(() => useKeyboardNavigation({ onTab }));
      
      window.dispatchEvent(createKeyboardEvent('Tab'));
      
      expect(onTab).toHaveBeenCalledTimes(1);
    });

    it('should call onSpace when Space is pressed', () => {
      const onSpace = jest.fn();
      renderHook(() => useKeyboardNavigation({ onSpace }));
      
      window.dispatchEvent(createKeyboardEvent(' '));
      
      expect(onSpace).toHaveBeenCalledTimes(1);
    });
  });

  describe('Event object passed to handlers', () => {
    it('should pass KeyboardEvent to handlers', () => {
      const onEnter = jest.fn();
      renderHook(() => useKeyboardNavigation({ onEnter }));
      
      const event = createKeyboardEvent('Enter');
      window.dispatchEvent(event);
      
      expect(onEnter).toHaveBeenCalledWith(expect.any(KeyboardEvent));
    });

    it('should allow handlers to access event properties', () => {
      const onArrowUp = jest.fn((e: KeyboardEvent) => {
        expect(e.key).toBe('ArrowUp');
      });
      
      renderHook(() => useKeyboardNavigation({ onArrowUp }));
      
      window.dispatchEvent(createKeyboardEvent('ArrowUp'));
      
      expect(onArrowUp).toHaveBeenCalled();
    });
  });

  describe('preventDefault option', () => {
    it('should call preventDefault when preventDefault is true', () => {
      const onEnter = jest.fn();
      renderHook(() => useKeyboardNavigation({ onEnter, preventDefault: true }));
      
      const event = createKeyboardEvent('Enter');
      const preventDefaultSpy = jest.spyOn(event, 'preventDefault');
      window.dispatchEvent(event);
      
      expect(preventDefaultSpy).toHaveBeenCalled();
    });

    it('should not call preventDefault when preventDefault is false', () => {
      const onEnter = jest.fn();
      renderHook(() => useKeyboardNavigation({ onEnter, preventDefault: false }));
      
      const event = createKeyboardEvent('Enter');
      const preventDefaultSpy = jest.spyOn(event, 'preventDefault');
      window.dispatchEvent(event);
      
      expect(preventDefaultSpy).not.toHaveBeenCalled();
    });

    it('should selectively preventDefault for specified keys', () => {
      const onEnter = jest.fn();
      const onEscape = jest.fn();
      
      renderHook(() =>
        useKeyboardNavigation({
          onEnter,
          onEscape,
          preventDefault: ['Enter'],
        })
      );
      
      const enterEvent = createKeyboardEvent('Enter');
      const escapeEvent = createKeyboardEvent('Escape');
      
      const enterPreventSpy = jest.spyOn(enterEvent, 'preventDefault');
      const escapePreventSpy = jest.spyOn(escapeEvent, 'preventDefault');
      
      window.dispatchEvent(enterEvent);
      window.dispatchEvent(escapeEvent);
      
      expect(enterPreventSpy).toHaveBeenCalled();
      expect(escapePreventSpy).not.toHaveBeenCalled();
    });
  });

  describe('stopPropagation option', () => {
    it('should call stopPropagation when stopPropagation is true', () => {
      const onEnter = jest.fn();
      renderHook(() => useKeyboardNavigation({ onEnter, stopPropagation: true }));
      
      const event = createKeyboardEvent('Enter');
      const stopPropSpy = jest.spyOn(event, 'stopPropagation');
      window.dispatchEvent(event);
      
      expect(stopPropSpy).toHaveBeenCalled();
    });

    it('should not call stopPropagation when stopPropagation is false', () => {
      const onEnter = jest.fn();
      renderHook(() => useKeyboardNavigation({ onEnter, stopPropagation: false }));
      
      const event = createKeyboardEvent('Enter');
      const stopPropSpy = jest.spyOn(event, 'stopPropagation');
      window.dispatchEvent(event);
      
      expect(stopPropSpy).not.toHaveBeenCalled();
    });
  });

  describe('ignoreInputs option', () => {
    it('should ignore events from input elements by default', () => {
      const onEnter = jest.fn();
      renderHook(() => useKeyboardNavigation({ onEnter }));
      
      const input = document.createElement('input');
      const event = createKeyboardEvent('Enter', input);
      window.dispatchEvent(event);
      
      expect(onEnter).not.toHaveBeenCalled();
    });

    it('should ignore events from textarea elements', () => {
      const onEnter = jest.fn();
      renderHook(() => useKeyboardNavigation({ onEnter }));
      
      const textarea = document.createElement('textarea');
      const event = createKeyboardEvent('Enter', textarea);
      window.dispatchEvent(event);
      
      expect(onEnter).not.toHaveBeenCalled();
    });

    it('should ignore events from select elements', () => {
      const onArrowDown = jest.fn();
      renderHook(() => useKeyboardNavigation({ onArrowDown }));
      
      const select = document.createElement('select');
      const event = createKeyboardEvent('ArrowDown', select);
      window.dispatchEvent(event);
      
      expect(onArrowDown).not.toHaveBeenCalled();
    });

    it('should allow input events when ignoreInputs is false', () => {
      const onEnter = jest.fn();
      renderHook(() => useKeyboardNavigation({ onEnter, ignoreInputs: false }));
      
      const input = document.createElement('input');
      const event = createKeyboardEvent('Enter', input);
      window.dispatchEvent(event);
      
      expect(onEnter).toHaveBeenCalled();
    });

    it('should ignore events from contentEditable elements', () => {
      const onEnter = jest.fn();
      renderHook(() => useKeyboardNavigation({ onEnter }));
      
      const div = document.createElement('div');
      div.setAttribute('contenteditable', 'true');
      Object.defineProperty(div, 'isContentEditable', {
        value: true,
        writable: false,
      });
      const event = createKeyboardEvent('Enter', div);
      window.dispatchEvent(event);
      
      expect(onEnter).not.toHaveBeenCalled();
    });
  });

  describe('Cleanup', () => {
    it('should remove event listener on unmount', () => {
      const onEnter = jest.fn();
      const { unmount } = renderHook(() => useKeyboardNavigation({ onEnter }));
      
      unmount();
      
      window.dispatchEvent(createKeyboardEvent('Enter'));
      
      expect(onEnter).not.toHaveBeenCalled();
    });

    it('should remove event listener when disabled', () => {
      const onEnter = jest.fn();
      const { rerender } = renderHook(
        ({ enabled }) => useKeyboardNavigation({ onEnter, enabled }),
        { initialProps: { enabled: true } }
      );
      
      rerender({ enabled: false });
      
      window.dispatchEvent(createKeyboardEvent('Enter'));
      
      expect(onEnter).not.toHaveBeenCalled();
    });
  });

  describe('Multiple handlers', () => {
    it('should handle multiple different keys', () => {
      const onEnter = jest.fn();
      const onEscape = jest.fn();
      const onArrowUp = jest.fn();
      
      renderHook(() => useKeyboardNavigation({ onEnter, onEscape, onArrowUp }));
      
      window.dispatchEvent(createKeyboardEvent('Enter'));
      window.dispatchEvent(createKeyboardEvent('Escape'));
      window.dispatchEvent(createKeyboardEvent('ArrowUp'));
      
      expect(onEnter).toHaveBeenCalledTimes(1);
      expect(onEscape).toHaveBeenCalledTimes(1);
      expect(onArrowUp).toHaveBeenCalledTimes(1);
    });

    it('should not call unregistered handlers', () => {
      const onEnter = jest.fn();
      
      renderHook(() => useKeyboardNavigation({ onEnter }));
      
      window.dispatchEvent(createKeyboardEvent('Escape'));
      
      expect(onEnter).not.toHaveBeenCalled();
    });
  });

  describe('Handler updates', () => {
    it('should use updated handler', () => {
      const onEnter1 = jest.fn();
      const onEnter2 = jest.fn();
      
      const { rerender } = renderHook(
        ({ onEnter }) => useKeyboardNavigation({ onEnter }),
        { initialProps: { onEnter: onEnter1 } }
      );
      
      window.dispatchEvent(createKeyboardEvent('Enter'));
      expect(onEnter1).toHaveBeenCalledTimes(1);
      
      rerender({ onEnter: onEnter2 });
      
      window.dispatchEvent(createKeyboardEvent('Enter'));
      expect(onEnter2).toHaveBeenCalledTimes(1);
      expect(onEnter1).toHaveBeenCalledTimes(1); // Should not be called again
    });
  });

  describe('Edge cases', () => {
    it('should handle unknown keys gracefully', () => {
      const onEnter = jest.fn();
      renderHook(() => useKeyboardNavigation({ onEnter }));
      
      window.dispatchEvent(createKeyboardEvent('UnknownKey'));
      
      expect(onEnter).not.toHaveBeenCalled();
    });

    it('should handle rapid key presses', () => {
      const onEnter = jest.fn();
      renderHook(() => useKeyboardNavigation({ onEnter }));
      
      window.dispatchEvent(createKeyboardEvent('Enter'));
      window.dispatchEvent(createKeyboardEvent('Enter'));
      window.dispatchEvent(createKeyboardEvent('Enter'));
      
      expect(onEnter).toHaveBeenCalledTimes(3);
    });

    it('should handle no handlers provided', () => {
      expect(() => {
        renderHook(() => useKeyboardNavigation());
        window.dispatchEvent(createKeyboardEvent('Enter'));
      }).not.toThrow();
    });
  });
});
