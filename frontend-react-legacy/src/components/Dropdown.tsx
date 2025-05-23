import React, { useState, useRef, useEffect } from 'react';
import { useKeyboardNavigation } from '../hooks/useKeyboardNavigation';
import { screenReader } from '../utils/accessibility';
import { focusManagement } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';

interface DropdownItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  disabled?: boolean;
}

interface DropdownProps {
  items: DropdownItem[];
  trigger: React.ReactElement;
  onSelect?: (item: DropdownItem) => void;
  position?: 'left' | 'right';
  width?: 'auto' | 'full';
}

export const Dropdown: React.FC<DropdownProps> = ({
  items,
  trigger,
  onSelect,
  position = 'left',
  width = 'auto',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState<number>(-1);
  const containerRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  const positionClasses = {
    left: 'left-0',
    right: 'right-0',
  };

  const widthClasses = {
    auto: 'w-auto',
    full: 'w-full',
  };

  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement as HTMLElement;
      screenReader.announce('Dropdown menu opened', 'polite');
    } else {
      screenReader.announce('Dropdown menu closed', 'polite');
    }
  }, [isOpen]);

  useEffect(() => {
    if (isOpen && containerRef.current) {
      const cleanup = focusManagement.trapFocus(containerRef.current);
      return cleanup;
    }
  }, [isOpen]);

  useKeyboardNavigation({
    onEscape: () => {
      if (isOpen) {
        setIsOpen(false);
        previousFocusRef.current?.focus();
      }
    },
    onArrowDown: () => {
      if (isOpen && focusedIndex < items.length - 1) {
        setFocusedIndex(focusedIndex + 1);
      }
    },
    onArrowUp: () => {
      if (isOpen && focusedIndex > 0) {
        setFocusedIndex(focusedIndex - 1);
      }
    },
    onHome: () => {
      if (isOpen) {
        setFocusedIndex(0);
      }
    },
    onEnd: () => {
      if (isOpen) {
        setFocusedIndex(items.length - 1);
      }
    },
  });

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    switch (e.key) {
      case 'Enter':
      case ' ':
        e.preventDefault();
        if (!items[index].disabled) {
          onSelect?.(items[index]);
          setIsOpen(false);
          previousFocusRef.current?.focus();
        }
        break;
      case 'Escape':
        e.preventDefault();
        setIsOpen(false);
        previousFocusRef.current?.focus();
        break;
    }
  };

  const clonedTrigger = React.cloneElement(trigger, {
    ref: triggerRef,
    onClick: () => setIsOpen(!isOpen),
    onKeyDown: (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
        e.preventDefault();
        setIsOpen(true);
      }
    },
    'aria-haspopup': 'true',
    'aria-expanded': isOpen,
  });

  return (
    <div className="relative inline-block">
      {clonedTrigger}
      {isOpen && (
        <div
          ref={containerRef}
          role="menu"
          aria-label="Dropdown menu"
          className={`absolute z-50 mt-1 bg-white rounded-md shadow-lg border border-gray-200 ${positionClasses[position]} ${widthClasses[width]}`}
        >
          {items.map((item, index) => (
            <button
              key={item.id}
              role="menuitem"
              tabIndex={0}
              onKeyDown={e => handleKeyDown(e, index)}
              onClick={() => {
                if (!item.disabled) {
                  onSelect?.(item);
                  setIsOpen(false);
                  previousFocusRef.current?.focus();
                }
              }}
              className={`w-full px-4 py-2 text-left text-sm ${
                focusedIndex === index
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-gray-700 hover:bg-gray-50'
              } ${
                item.disabled
                  ? 'opacity-50 cursor-not-allowed'
                  : 'cursor-pointer'
              }`}
              disabled={item.disabled}
              aria-disabled={item.disabled}
            >
              <div className="flex items-center">
                {item.icon && (
                  <span className="mr-2" aria-hidden="true">
                    {item.icon}
                  </span>
                )}
                {item.label}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
