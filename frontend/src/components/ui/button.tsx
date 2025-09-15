import React, { ButtonHTMLAttributes, forwardRef } from 'react';
import { cn } from '../../lib/utils';
import { tokens } from '../../design-tokens/tokens';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?:
    | 'default'
    | 'primary'
    | 'secondary'
    | 'destructive'
    | 'outline'
    | 'ghost'
    | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  isLoading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'default',
      size = 'default',
      isLoading = false,
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    // Base styles
    const baseStyles =
      'inline-flex items-center justify-center font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed rounded-[var(--btn-radius)] transition-colors';

    // Bridge some token values via CSS variables to avoid large class rewrites
    const tokenVars = {
      ['--btn-radius' as any]: tokens.borderRadius.base,
    } as React.CSSProperties;

    // Variant styles
    const variantMap = {
      default: 'bg-gray-900 text-white hover:bg-gray-800',
      primary: 'bg-blue-600 text-white hover:bg-blue-700',
      secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200',
      destructive: 'bg-red-600 text-white hover:bg-red-700',
      outline: 'border border-gray-300 bg-transparent hover:bg-gray-100',
      ghost: 'bg-transparent hover:bg-gray-100',
      link: 'bg-transparent underline-offset-4 hover:underline text-blue-600',
    };

    // Size styles - ensuring minimum touch target of 44px height
    const sizeMap = {
      default: `min-h-[44px] h-11 py-[${tokens.spacing.sm}] px-[${tokens.spacing.md}]`,
      sm: `min-h-[44px] h-11 px-[${tokens.spacing.sm}] text-sm`,
      lg: `min-h-[48px] h-12 px-[${tokens.spacing.lg}] text-lg`,
      icon: 'min-h-[44px] min-w-[44px] h-11 w-11',
    };

    // Make sure the variant and size values are valid
    const variantStyle = variantMap[variant] || variantMap.default;
    const sizeStyle = sizeMap[size] || sizeMap.default;

    return (
      <button
        ref={ref}
        style={tokenVars}
        className={cn(baseStyles, variantStyle, sizeStyle, className)}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <span className="mr-2">
            <svg
              className="animate-spin h-4 w-4 text-current"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          </span>
        ) : null}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
