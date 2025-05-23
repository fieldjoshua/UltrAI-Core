import React, { useState, useRef, useEffect } from 'react';
import { useKeyboardNavigation } from '../hooks/useKeyboardNavigation';
import { screenReader } from '../utils/accessibility';
import { focusManagement } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';

interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

interface SelectProps {
  id: string;
  label: string;
  options: SelectOption[];
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  placeholder?: string;
  ariaDescribedBy?: string;
}

export const Select: React.FC<SelectProps> = ({
  id,
  label,
  options,
  value,
  onChange,
  disabled = false,
  required = false,
  error,
  placeholder = 'Select an option',
  ariaDescribedBy,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState<number>(-1);
  const selectRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  const selectedOption = options.find(option => option.value === value);

  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement as HTMLElement;
      screenReader.announce('Select dropdown opened', 'polite');
    } else {
      screenReader.announce('Select dropdown closed', 'polite');
    }
  }, [isOpen]);

  useEffect(() => {
    if (isOpen && selectRef.current) {
      const cleanup = focusManagement.trapFocus(selectRef.current);
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
      if (isOpen && focusedIndex < options.length - 1) {
        const nextIndex = focusedIndex + 1;
        if (!options[nextIndex].disabled) {
          setFocusedIndex(nextIndex);
        }
      }
    },
    onArrowUp: () => {
      if (isOpen && focusedIndex > 0) {
        const prevIndex = focusedIndex - 1;
        if (!options[prevIndex].disabled) {
          setFocusedIndex(prevIndex);
        }
      }
    },
    onHome: () => {
      if (isOpen && !options[0].disabled) {
        setFocusedIndex(0);
      }
    },
    onEnd: () => {
      if (isOpen && !options[options.length - 1].disabled) {
        setFocusedIndex(options.length - 1);
      }
    },
  });

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    switch (e.key) {
      case 'Enter':
      case ' ':
        e.preventDefault();
        if (!options[index].disabled) {
          onChange(options[index].value);
          setIsOpen(false);
          previousFocusRef.current?.focus();
          screenReader.announce(`${options[index].label} selected`, 'polite');
        }
        break;
      case 'Escape':
        e.preventDefault();
        setIsOpen(false);
        previousFocusRef.current?.focus();
        break;
    }
  };

  return (
    <div className="relative">
      <label
        htmlFor={id}
        className="block text-sm font-medium text-gray-700 mb-1"
      >
        {label}
        {required && (
          <span className="ml-1 text-red-500" aria-hidden="true">
            *
          </span>
        )}
      </label>
      <div ref={selectRef}>
        <button
          ref={triggerRef}
          type="button"
          id={id}
          onClick={() => {
            if (!disabled) {
              setIsOpen(!isOpen);
            }
          }}
          onKeyDown={e => {
            if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
              e.preventDefault();
              if (!disabled) {
                setIsOpen(true);
              }
            }
          }}
          disabled={disabled}
          required={required}
          aria-required={required}
          aria-invalid={!!error}
          aria-describedby={ariaDescribedBy}
          aria-haspopup="listbox"
          aria-expanded={isOpen}
          className={`w-full px-3 py-2 text-left bg-white border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            error ? 'border-red-300' : 'border-gray-300'
          } ${
            disabled
              ? 'cursor-not-allowed opacity-50'
              : 'cursor-pointer hover:border-gray-400'
          }`}
        >
          <span className="block truncate">
            {selectedOption ? selectedOption.label : placeholder}
          </span>
        </button>
        {isOpen && (
          <div
            role="listbox"
            aria-label={label}
            className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto"
          >
            {options.map((option, index) => (
              <div
                key={option.value}
                role="option"
                tabIndex={0}
                onKeyDown={e => handleKeyDown(e, index)}
                onClick={() => {
                  if (!option.disabled) {
                    onChange(option.value);
                    setIsOpen(false);
                    previousFocusRef.current?.focus();
                    screenReader.announce(`${option.label} selected`, 'polite');
                  }
                }}
                className={`px-3 py-2 cursor-pointer ${
                  option.value === value
                    ? 'bg-blue-100 text-blue-900'
                    : 'text-gray-900 hover:bg-gray-100'
                } ${option.disabled ? 'opacity-50 cursor-not-allowed' : ''} ${
                  focusedIndex === index
                    ? 'ring-2 ring-blue-500 ring-offset-2'
                    : ''
                }`}
                aria-selected={option.value === value}
                aria-disabled={option.disabled}
              >
                {option.label}
              </div>
            ))}
          </div>
        )}
      </div>
      {error && (
        <p
          id={`${id}-error`}
          className="mt-1 text-sm text-red-600"
          role="alert"
        >
          {error}
        </p>
      )}
    </div>
  );
};
