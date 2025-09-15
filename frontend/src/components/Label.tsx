import React from 'react';
import { screenReader } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';
import { tokens } from '../design-tokens/tokens';

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
      style={{ ['--label-spacing' as any]: tokens.spacing.xs } as React.CSSProperties}
      className={`block text-sm font-medium ${
        disabled ? 'text-gray-400' : 'text-gray-700'
      }`}
      aria-describedby={ariaDescribedBy}
    >
      {children}
      {required && (
        <span className="text-red-500" style={{ marginLeft: 'var(--label-spacing)' }} aria-hidden="true">
          *
        </span>
      )}
      {error && (
        <span className="text-red-600" style={{ marginLeft: tokens.spacing.sm }} role="alert">
          {error}
        </span>
      )}
    </label>
  );
};
