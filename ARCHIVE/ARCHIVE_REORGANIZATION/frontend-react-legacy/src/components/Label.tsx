import React from 'react';
import { screenReader } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';

interface LabelProps {
  htmlFor: string;
  children: React.ReactNode;
  required?: boolean;
  disabled?: boolean;
  error?: string;
  ariaDescribedBy?: string;
}

export const Label: React.FC<LabelProps> = ({
  htmlFor,
  children,
  required = false,
  disabled = false,
  error,
  ariaDescribedBy,
}) => {
  return (
    <label
      htmlFor={htmlFor}
      className={`block text-sm font-medium ${
        disabled ? 'text-gray-400' : 'text-gray-700'
      }`}
      aria-describedby={ariaDescribedBy}
    >
      {children}
      {required && (
        <span className="ml-1 text-red-500" aria-hidden="true">
          *
        </span>
      )}
      {error && (
        <span className="ml-2 text-red-600" role="alert">
          {error}
        </span>
      )}
    </label>
  );
};
