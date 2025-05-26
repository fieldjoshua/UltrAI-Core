import React from 'react';
import { screenReader } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  label?: string;
  isFullScreen?: boolean;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'medium',
  label = 'Loading...',
  isFullScreen = false,
}) => {
  const sizeClasses = {
    small: 'h-4 w-4',
    medium: 'h-8 w-8',
    large: 'h-12 w-12',
  };

  React.useEffect(() => {
    screenReader.announce(label, 'polite');
  }, [label]);

  const spinner = (
    <div
      role="status"
      aria-label={label}
      className={`inline-block animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite] ${sizeClasses[size]}`}
    >
      <span className="sr-only">{label}</span>
    </div>
  );

  if (isFullScreen) {
    return (
      <div
        role="alert"
        aria-live="polite"
        className="fixed inset-0 flex items-center justify-center bg-white bg-opacity-75 z-50"
      >
        <div className="text-center">
          {spinner}
          <p className="mt-2 text-sm text-gray-600">{label}</p>
        </div>
      </div>
    );
  }

  return spinner;
};
