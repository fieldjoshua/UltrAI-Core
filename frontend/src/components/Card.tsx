import React from 'react';
import { screenReader } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';
import { tokens } from '../design-tokens/tokens';

interface CardProps {
  title?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  onClick?: () => void;
  isInteractive?: boolean;
  ariaLabel?: string;
  ariaDescribedBy?: string;
}

export const Card: React.FC<CardProps> = ({
  title,
  children,
  footer,
  onClick,
  isInteractive = false,
  ariaLabel,
  ariaDescribedBy,
}) => {
  const cardContent = (
    <>
      {title && (
        <div className="px-4 py-3 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">{title}</h3>
        </div>
      )}
      <div className="p-4">{children}</div>
      {footer && (
        <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
          {footer}
        </div>
      )}
    </>
  );

  const baseClasses =
    'bg-white shadow-sm border border-gray-200 overflow-hidden rounded-[var(--card-radius)]';
  const tokenVars = {
    ['--card-radius' as any]: tokens.borderRadius.base,
  } as React.CSSProperties;
  const interactiveClasses = isInteractive
    ? 'cursor-pointer hover:shadow-md transition-shadow duration-200'
    : '';

  if (onClick || isInteractive) {
    return (
      <button
        onClick={onClick}
        style={tokenVars}
        className={`w-full text-left ${baseClasses} ${interactiveClasses}`}
        aria-label={ariaLabel}
        aria-describedby={ariaDescribedBy}
      >
        {cardContent}
      </button>
    );
  }

  return (
    <div
      role="article"
      style={tokenVars}
      className={baseClasses}
      aria-label={ariaLabel}
      aria-describedby={ariaDescribedBy}
    >
      {cardContent}
    </div>
  );
};
