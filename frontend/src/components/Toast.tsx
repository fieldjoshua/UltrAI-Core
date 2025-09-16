import React from 'react';
import { useUIStore } from '../stores/uiStore';
import { AlertCircle, CheckCircle, Info, X, AlertTriangle } from 'lucide-react';

export const Toast: React.FC = () => {
  const { toasts, removeToast } = useUIStore();

  if (toasts.length === 0) return null;

  const getIcon = (type: string) => {
    switch (type) {
      case 'error':
        return <AlertCircle className="h-5 w-5" />;
      case 'success':
        return <CheckCircle className="h-5 w-5" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5" />;
      case 'info':
      default:
        return <Info className="h-5 w-5" />;
    }
  };

  const getBackgroundColor = (type: string) => {
    switch (type) {
      case 'error':
        return 'bg-red-100 border-red-400 text-red-700';
      case 'success':
        return 'bg-green-100 border-green-400 text-green-700';
      case 'warning':
        return 'bg-yellow-100 border-yellow-400 text-yellow-700';
      case 'info':
      default:
        return 'bg-blue-100 border-blue-400 text-blue-700';
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      {toasts.map(toast => (
        <div key={toast.id} className="animate-fade-in-up">
          <div
            className={`rounded-md border px-4 py-3 shadow-md ${getBackgroundColor(toast.type)}`}
          >
            <div className="flex items-center">
              <div className="mr-3">{getIcon(toast.type)}</div>
              <div className="mr-2 max-w-[300px] break-words">
                {toast.message}
              </div>
              <button
                onClick={() => removeToast(toast.id)}
                className="ml-auto rounded-full p-1 transition-colors hover:bg-opacity-20 hover:bg-gray-500"
                aria-label="Close notification"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default Toast;
