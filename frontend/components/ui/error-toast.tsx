import React from 'react';
import { AlertCircle, X } from 'lucide-react';
import { cn } from './utils';

interface ErrorToastProps {
  title: string;
  message?: string;
  onClose?: () => void;
  className?: string;
  autoClose?: boolean;
  autoCloseDelay?: number;
}

/**
 * A toast component for displaying error messages
 */
const ErrorToast: React.FC<ErrorToastProps> = ({
  title,
  message,
  onClose,
  className,
  autoClose = true,
  autoCloseDelay = 5000,
}) => {
  const [isVisible, setIsVisible] = React.useState(true);

  React.useEffect(() => {
    let timeoutId: NodeJS.Timeout | null = null;

    if (autoClose) {
      timeoutId = setTimeout(() => {
        setIsVisible(false);
        if (onClose) onClose();
      }, autoCloseDelay);
    }

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [autoClose, autoCloseDelay, onClose]);

  const handleClose = () => {
    setIsVisible(false);
    if (onClose) onClose();
  };

  if (!isVisible) return null;

  return (
    <div
      className={cn(
        'flex w-full max-w-sm items-center space-x-4 rounded-lg border border-destructive bg-destructive/10 p-4 text-destructive shadow-lg',
        className
      )}
      role="alert"
    >
      <div className="flex-shrink-0">
        <AlertCircle className="h-5 w-5" />
      </div>
      <div className="flex-1">
        <div className="font-medium">{title}</div>
        {message && <div className="mt-1 text-sm opacity-90">{message}</div>}
      </div>
      <button
        onClick={handleClose}
        className="inline-flex flex-shrink-0 items-center justify-center rounded-lg p-1 hover:bg-destructive/20 focus:outline-none focus:ring-2 focus:ring-destructive/50"
        aria-label="Close"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
};

export { ErrorToast };
