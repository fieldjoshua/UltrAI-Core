import React, { LabelHTMLAttributes, forwardRef } from 'react';

interface LabelProps extends LabelHTMLAttributes<HTMLLabelElement> {
    htmlFor?: string;
}

export const Label = forwardRef<HTMLLabelElement, LabelProps>(
    ({ className = '', children, ...props }, ref) => {
        return (
            <label
                ref={ref}
                className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${className}`}
                {...props}
            >
                {children}
            </label>
        );
    }
);

Label.displayName = 'Label';