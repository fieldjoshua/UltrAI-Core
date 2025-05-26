import React, { useRef } from 'react';
import { useKeyboardNavigation } from '../hooks/useKeyboardNavigation';
import { screenReader } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';

interface CheckboxProps {
  id: string;
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  ariaDescribedBy?: string;
}

export const Checkbox: React.FC<CheckboxProps> = ({
  id,
  label,
  checked,
  onChange,
  disabled = false,
  required = false,
  error,
  ariaDescribedBy,
}) => {
  const checkboxRef = useRef<HTMLInputElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      if (!disabled) {
        onChange(!checked);
        screenReader.announce(
          `${label} ${!checked ? 'checked' : 'unchecked'}`,
          'polite'
        );
      }
    }
  };

  useKeyboardNavigation({
    onEnter: () => {
      if (!disabled) {
        onChange(!checked);
        screenReader.announce(
          `${label} ${!checked ? 'checked' : 'unchecked'}`,
          'polite'
        );
      }
    },
  });

  return (
    <div className="flex items-start">
      <div className="flex items-center h-5">
        <input
          ref={checkboxRef}
          id={id}
          type="checkbox"
          checked={checked}
          onChange={e => onChange(e.target.checked)}
          disabled={disabled}
          required={required}
          aria-required={required}
          aria-invalid={!!error}
          aria-describedby={ariaDescribedBy}
          className={`h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 ${
            disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'
          }`}
          onKeyDown={handleKeyDown}
        />
      </div>
      <div className="ml-3">
        <label
          htmlFor={id}
          className={`text-sm font-medium ${
            disabled ? 'text-gray-400' : 'text-gray-700'
          }`}
        >
          {label}
          {required && (
            <span className="ml-1 text-red-500" aria-hidden="true">
              *
            </span>
          )}
        </label>
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
    </div>
  );
};
