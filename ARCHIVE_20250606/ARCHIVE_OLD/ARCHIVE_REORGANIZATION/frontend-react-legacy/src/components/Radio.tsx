import React, { useRef } from 'react';
import { useKeyboardNavigation } from '../hooks/useKeyboardNavigation';
import { screenReader } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';

interface RadioProps {
  id: string;
  name: string;
  label: string;
  value: string;
  checked: boolean;
  onChange: (value: string) => void;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  ariaDescribedBy?: string;
}

export const Radio: React.FC<RadioProps> = ({
  id,
  name,
  label,
  value,
  checked,
  onChange,
  disabled = false,
  required = false,
  error,
  ariaDescribedBy,
}) => {
  const radioRef = useRef<HTMLInputElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      if (!disabled) {
        onChange(value);
        screenReader.announce(`${label} selected`, 'polite');
      }
    }
  };

  useKeyboardNavigation({
    onEnter: () => {
      if (!disabled) {
        onChange(value);
        screenReader.announce(`${label} selected`, 'polite');
      }
    },
  });

  return (
    <div className="flex items-start">
      <div className="flex items-center h-5">
        <input
          ref={radioRef}
          id={id}
          type="radio"
          name={name}
          value={value}
          checked={checked}
          onChange={e => onChange(e.target.value)}
          disabled={disabled}
          required={required}
          aria-required={required}
          aria-invalid={!!error}
          aria-describedby={ariaDescribedBy}
          className={`h-4 w-4 border-gray-300 text-blue-600 focus:ring-blue-500 ${
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
