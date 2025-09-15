import React, { InputHTMLAttributes, forwardRef } from 'react';
import { tokens } from '../../design-tokens/tokens';

interface CheckboxProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className = '', label, id, ...props }, ref) => {
    return (
      <div className="relative inline-flex items-center">
        {/* Touch target extender */}
        <span 
          className="absolute inset-0 -m-2 min-w-[44px] min-h-[44px]" 
          aria-hidden="true"
        />
        <input
          type="checkbox"
          id={id}
          ref={ref}
          style={{ ['--cb-radius' as any]: tokens.borderRadius.sm } as React.CSSProperties}
          className={`relative h-5 w-5 md:h-4 md:w-4 border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-[var(--cb-radius)] ${className}`}
          {...props}
        />
        {label && (
          <label 
            htmlFor={id} 
            className="ml-2 text-sm font-medium text-gray-700 select-none"
          >
            {label}
          </label>
        )}
      </div>
    );
  }
);

Checkbox.displayName = 'Checkbox';
