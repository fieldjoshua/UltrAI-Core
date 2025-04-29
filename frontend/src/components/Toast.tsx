import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../app/store';
import { clearToast } from '../features/errors/errorsSlice';
import { AlertCircle, CheckCircle, Info, X } from 'lucide-react';

export const Toast: React.FC = () => {
  const dispatch = useDispatch();
  const { id, message, type } = useSelector(
    (state: RootState) => state.errors.toast
  );

  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => {
        dispatch(clearToast());
      }, 5000); // Auto-dismiss after 5 seconds

      return () => clearTimeout(timer);
    }
  }, [id, dispatch]);

  const handleClose = () => {
    dispatch(clearToast());
  };

  if (!message) return null;

  const getIcon = () => {
    switch (type) {
      case 'error':
        return <AlertCircle className="h-5 w-5" />;
      case 'success':
        return <CheckCircle className="h-5 w-5" />;
      case 'info':
      default:
        return <Info className="h-5 w-5" />;
    }
  };

  const getBackgroundColor = () => {
    switch (type) {
      case 'error':
        return 'bg-red-100 border-red-400 text-red-700';
      case 'success':
        return 'bg-green-100 border-green-400 text-green-700';
      case 'info':
      default:
        return 'bg-blue-100 border-blue-400 text-blue-700';
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 animate-fade-in-up">
      <div
        className={`rounded-md border px-4 py-3 shadow-md ${getBackgroundColor()}`}
      >
        <div className="flex items-center">
          <div className="mr-3">{getIcon()}</div>
          <div className="mr-2 max-w-[300px] break-words">{message}</div>
          <button
            onClick={handleClose}
            className="ml-auto rounded-full p-1 transition-colors hover:bg-opacity-20 hover:bg-gray-500"
            aria-label="Close notification"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Toast;
