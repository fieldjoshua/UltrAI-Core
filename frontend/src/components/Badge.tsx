import React from 'react';
import { screenReader } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';

interface BadgeProps {
  label: string;
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info';
  size?: 'small' | 'medium' | 'large';
  icon?: React.ReactNode;
  onClick?: () => void;
  ariaLabel?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  label,
  variant = 'default',
  size = 'medium',
  icon,
  onClick,
  ariaLabel,
}) => {
  const variantClasses = {
    default: 'bg-gray-100 text-gray-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800',
    info: 'bg-blue-100 text-blue-800',
  };

  const sizeClasses = {
    small: 'text-xs px-2 py-0.5',
    medium: 'text-sm px-2.5 py-0.5',
    large: 'text-base px-3 py-1',
  };

  const iconSizeClasses = {
    small: 'w-3 h-3',
    medium: 'w-4 h-4',
    large: 'w-5 h-5',
  };

  const badgeContent = (
    <>
      {icon && (
        <span className={`mr-1 ${iconSizeClasses[size]}`} aria-hidden="true">
          {icon}
        </span>
      )}
      {label}
    </>
  );

  if (onClick) {
    return (
      <button
        onClick={onClick}
        className={`inline-flex items-center rounded-full font-medium ${variantClasses[variant]} ${sizeClasses[size]}`}
        aria-label={ariaLabel || label}
      >
        {badgeContent}
      </button>
    );
  }

  return (
    <span
      role="status"
      aria-label={ariaLabel || label}
      className={`inline-flex items-center rounded-full font-medium ${variantClasses[variant]} ${sizeClasses[size]}`}
    >
      {badgeContent}
    </span>
  );
};
