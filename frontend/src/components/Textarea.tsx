import React, { useRef } from 'react';
import { useKeyboardNavigation } from '../hooks/useKeyboardNavigation';
import { screenReader } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';
import { tokens } from '../design-tokens/tokens';

interface TextareaProps {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  placeholder?: string;
  rows?: number;
  maxLength?: number;
  ariaDescribedBy?: string;
}

export const Textarea: React.FC<TextareaProps> = ({
  id,
  label,
  value,
  onChange,
  disabled = false,
  required = false,
  error,
  placeholder,
  rows = 3,
  maxLength,
  ariaDescribedBy,
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.shiftKey) {
      e.preventDefault();
      const textarea = textareaRef.current;
      if (textarea) {
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const newValue =
          value.substring(0, start) + '\n' + value.substring(end);
        onChange(newValue);
        setTimeout(() => {
          textarea.selectionStart = textarea.selectionEnd = start + 1;
        }, 0);
      }
    }
  };

  useKeyboardNavigation({
    onEnter: () => {
      if (textareaRef.current) {
        textareaRef.current.focus();
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
        <textarea
          ref={textareaRef}
          id={id}
          value={value}
          onChange={e => onChange(e.target.value)}
          disabled={disabled}
          required={required}
          aria-required={required}
          aria-invalid={!!error}
          aria-describedby={ariaDescribedBy}
          placeholder={placeholder}
          rows={rows}
          maxLength={maxLength}
          onKeyDown={handleKeyDown}
          style={{ ['--ta-radius' as any]: tokens.borderRadius.base, ['--ta-pad-y' as any]: tokens.spacing.sm, ['--ta-pad-x' as any]: tokens.spacing.md } as React.CSSProperties}
          className={`w-full bg-white border rounded-[var(--ta-radius)] shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 py-[var(--ta-pad-y)] px-[var(--ta-pad-x)] ${
            error ? 'border-red-300' : 'border-gray-300'
          } ${disabled ? 'cursor-not-allowed opacity-50' : 'resize-none'}`}
        />
        {maxLength && (
          <div
            className="absolute bottom-2 right-2 text-xs text-gray-500"
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
