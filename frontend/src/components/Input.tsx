import React, { useRef } from 'react';
import { useKeyboardNavigation } from '../hooks/useKeyboardNavigation';
import { screenReader } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';
import { tokens } from '../design-tokens/tokens';

interface InputProps {
  id: string;
  label: string;
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url';
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  placeholder?: string;
  maxLength?: number;
  min?: number;
  max?: number;
  step?: number;
  ariaDescribedBy?: string;
  autoComplete?: string;
}

export const Input: React.FC<InputProps> = ({
  id,
  label,
  type = 'text',
  value,
  onChange,
  disabled = false,
  required = false,
  error,
  placeholder,
  maxLength,
  min,
  max,
  step,
  ariaDescribedBy,
  autoComplete,
}) => {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const input = inputRef.current;
      if (input) {
        input.blur();
      }
    }
  };

  useKeyboardNavigation({
    onEnter: () => {
      if (inputRef.current) {
        inputRef.current.focus();
      }
    },
  });

  return (
    <div>
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
      <div className="relative">
        <input
          ref={inputRef}
          id={id}
          type={type}
          value={value}
          onChange={e => onChange(e.target.value)}
          disabled={disabled}
          required={required}
          aria-required={required}
          aria-invalid={!!error}
          aria-describedby={ariaDescribedBy}
          placeholder={placeholder}
          maxLength={maxLength}
          min={min}
          max={max}
          step={step}
          autoComplete={autoComplete}
          onKeyDown={handleKeyDown}
          style={
            {
              ['--input-radius' as any]: tokens.borderRadius.base,
              ['--input-pad-y' as any]:
                tokens.components.input.padding.split(' ')[0],
              ['--input-pad-x' as any]:
                tokens.components.input.padding.split(' ')[1],
            } as React.CSSProperties
          }
          className={`w-full bg-white border shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-[var(--input-radius)] py-[var(--input-pad-y)] px-[var(--input-pad-x)] ${
            error ? 'border-red-300' : 'border-gray-300'
          } ${disabled ? 'cursor-not-allowed opacity-50' : ''}`}
        />
        {maxLength && (
          <div
            className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-gray-500"
            aria-live="polite"
          >
            {value.length}/{maxLength}
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
