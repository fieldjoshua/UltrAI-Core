import React, { HTMLAttributes, forwardRef } from 'react';

interface ProgressProps extends HTMLAttributes<HTMLDivElement> {
  value?: number;
  max?: number;
}

export const Progress = forwardRef<HTMLDivElement, ProgressProps>(
  ({ className = '', value = 0, max = 100, ...props }, ref) => {
    const valueString = value.toString();
    const maxString = max.toString();

    return (
      <div
        ref={ref}
        role="progressbar"
        aria-valuemin="0"
        aria-valuemax={maxString}
        aria-valuenow={valueString}
        className={`relative h-2 w-full overflow-hidden rounded-full bg-gray-100 ${className}`}
        {...props}
      >
        <div
          className="h-full w-full flex-1 bg-blue-600 transition-all"
          style={{ transform: `translateX(-${100 - (value / max) * 100}%)` }}
        />
      </div>
    );
  }
);

Progress.displayName = 'Progress';
