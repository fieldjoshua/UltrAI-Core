import React from 'react';
import { cn } from '../../lib/utils';

interface TouchTargetProps extends React.HTMLAttributes<HTMLDivElement> {
  as?: React.ElementType;
  children: React.ReactNode;
  minSize?: number;
}

/**
 * TouchTarget ensures a minimum touch target size of 44x44px for accessibility
 * while maintaining the visual size of the child element
 */
export const TouchTarget: React.FC<TouchTargetProps> = ({
  as: Component = 'div',
  children,
  className,
  minSize = 44,
  ...props
}) => {
  return (
    <Component
      className={cn(
        'relative inline-flex items-center justify-center',
        className
      )}
      {...props}
    >
      {/* Invisible touch area extender */}
      <span
        className="absolute inset-0 pointer-events-none"
        style={{
          minWidth: `${minSize}px`,
          minHeight: `${minSize}px`,
          margin: 'auto',
        }}
        aria-hidden="true"
      />
      {/* Actual content */}
      <span className="relative pointer-events-auto">
        {children}
      </span>
    </Component>
  );
};

export default TouchTarget;