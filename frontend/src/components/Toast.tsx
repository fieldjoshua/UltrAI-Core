import React, { useEffect } from 'react';
import { screenReader } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';

interface ToastProps {
  message: string;
  type?: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  onClose?: () => void;
}

export const Toast: React.FC<ToastProps> = ({
  message,
  type = 'info',
  duration = 5000,
  onClose,
}) => {
  const typeClasses = {
    success: 'bg-green-100 text-green-800 border-green-200',
    error: 'bg-red-100 text-red-800 border-red-200',
    warning: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    info: 'bg-blue-100 text-blue-800 border-blue-200',
  };

  const typeIcons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ',
  };

  useEffect(() => {
    screenReader.announce(message, 'assertive');
  }, [message]);

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose?.();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  return (
    <div
      role="alert"
      aria-live="assertive"
      className={`fixed bottom-4 right-4 p-4 rounded-lg shadow-lg border ${typeClasses[type]} max-w-md`}
    >
      <div className="flex items-start">
        <span className="mr-2 text-lg" aria-hidden="true">
          {typeIcons[type]}
        </span>
        <p className="flex-1">{message}</p>
        {onClose && (
          <button
            onClick={onClose}
            className="ml-4 text-current hover:opacity-75 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-current rounded"
            aria-label="Close notification"
          >
            <span aria-hidden="true">×</span>
          </button>
        )}
      </div>
    </div>
  );
};
