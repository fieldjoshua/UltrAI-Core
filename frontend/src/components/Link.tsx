import React from 'react';

interface LinkProps {
  href: string;
  children: React.ReactNode;
  external?: boolean;
  disabled?: boolean;
  onClick?: () => void;
  ariaLabel?: string;
  ariaDescribedBy?: string;
  ariaCurrent?:
    | 'page'
    | 'step'
    | 'location'
    | 'date'
    | 'time'
    | 'true'
    | 'false';
}

export const Link: React.FC<LinkProps> = ({
  href,
  children,
  external = false,
  disabled = false,
  onClick,
  ariaLabel,
  ariaDescribedBy,
  ariaCurrent,
}) => {
  const handleClick = (e: React.MouseEvent) => {
    if (disabled) {
      e.preventDefault();
      return;
    }
    onClick?.();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      if (!disabled) {
        onClick?.();
      }
    }
  };

  return (
    <a
      href={href}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      target={external ? '_blank' : undefined}
      rel={external ? 'noopener noreferrer' : undefined}
      aria-label={ariaLabel}
      aria-describedby={ariaDescribedBy}
      aria-current={ariaCurrent}
      aria-disabled={disabled ? 'true' : 'false'}
      className={`text-blue-600 hover:text-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
        disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'
      }`}
    >
      {children}
      {external && (
        <span className="ml-1" aria-hidden="true">
          ↗
        </span>
      )}
    </a>
  );
};
