import React, { useRef } from 'react';
import { useKeyboardNavigation } from '../hooks/useKeyboardNavigation';
import { screenReader } from '../utils/accessibility';

interface SwitchProps {
  id: string;
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  ariaDescribedBy?: string;
}

export const Switch: React.FC<SwitchProps> = ({
  id,
  label,
  checked,
  onChange,
  disabled = false,
  ariaDescribedBy,
}) => {
  const switchRef = useRef<HTMLButtonElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      if (!disabled) {
        onChange(!checked);
        screenReader.announce(
          `${label} ${!checked ? 'enabled' : 'disabled'}`,
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
          `${label} ${!checked ? 'enabled' : 'disabled'}`,
          'polite'
        );
      }
    },
  });

  return (
    <div className="flex items-center">
      <button
        ref={switchRef}
        type="button"
        role="switch"
        id={id}
        aria-checked={checked ? 'true' : 'false'}
        aria-disabled={disabled ? 'true' : 'false'}
        aria-describedby={ariaDescribedBy}
        onClick={() => {
          if (!disabled) {
            onChange(!checked);
          }
        }}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
          checked ? 'bg-blue-600' : 'bg-gray-200'
        } ${disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            checked ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
      <label
        htmlFor={id}
        className={`ml-3 text-sm font-medium ${
          disabled ? 'text-gray-400' : 'text-gray-700'
        }`}
      >
        {label}
      </label>
    </div>
  );
};
