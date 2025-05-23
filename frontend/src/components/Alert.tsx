import React from 'react';
import { screenReader } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';

interface AlertProps {
  title?: string;
  message: string;
  type?: 'info' | 'success' | 'warning' | 'error';
  icon?: React.ReactNode;
  onClose?: () => void;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export const Alert: React.FC<AlertProps> = ({
  title,
  message,
  type = 'info',
  icon,
  onClose,
  action,
}) => {
  const typeClasses = {
    info: 'bg-blue-50 text-blue-800 border-blue-200',
    success: 'bg-green-50 text-green-800 border-green-200',
    warning: 'bg-yellow-50 text-yellow-800 border-yellow-200',
    error: 'bg-red-50 text-red-800 border-red-200',
  };

  const iconClasses = {
    info: 'text-blue-400',
    success: 'text-green-400',
    warning: 'text-yellow-400',
    error: 'text-red-400',
  };

  React.useEffect(() => {
    const announcement = title ? `${title}: ${message}` : message;
    screenReader.announce(announcement, 'assertive');
  }, [title, message]);

  return (
    <div
      role="alert"
      aria-live="assertive"
      className={`rounded-lg border p-4 ${typeClasses[type]}`}
    >
      <div className="flex">
        {icon && (
          <div
            className={`flex-shrink-0 ${iconClasses[type]}`}
            aria-hidden="true"
          >
            {icon}
          </div>
        )}
        <div className="ml-3 flex-1">
          {title && <h3 className="text-sm font-medium">{title}</h3>}
          <div className="mt-2 text-sm">{message}</div>
          {action && (
            <div className="mt-4">
              <button
                type="button"
                onClick={action.onClick}
                className={`text-sm font-medium ${
                  type === 'info'
                    ? 'text-blue-600 hover:text-blue-500'
                    : type === 'success'
                      ? 'text-green-600 hover:text-green-500'
                      : type === 'warning'
                        ? 'text-yellow-600 hover:text-yellow-500'
                        : 'text-red-600 hover:text-red-500'
                }`}
              >
                {action.label}
              </button>
            </div>
          )}
        </div>
        {onClose && (
          <div className="ml-auto pl-3">
            <button
              type="button"
              onClick={onClose}
              className={`inline-flex rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                type === 'info'
                  ? 'text-blue-400 hover:text-blue-500 focus:ring-blue-500'
                  : type === 'success'
                    ? 'text-green-400 hover:text-green-500 focus:ring-green-500'
                    : type === 'warning'
                      ? 'text-yellow-400 hover:text-yellow-500 focus:ring-yellow-500'
                      : 'text-red-400 hover:text-red-500 focus:ring-red-500'
              }`}
              aria-label="Close alert"
            >
              <span aria-hidden="true">×</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
