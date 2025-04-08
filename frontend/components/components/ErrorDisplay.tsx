import React, { useState, useEffect } from 'react';
import { AlertCircle, X } from 'lucide-react';

interface ErrorDisplayProps {
  errors: Array<{
    id: string;
    message: string;
    timestamp: Date;
    type: 'api' | 'general' | 'network';
  }>;
  onDismiss?: (id: string) => void;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  errors,
  onDismiss,
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  // If there are no errors, don't render anything
  if (!errors || errors.length === 0) {
    return null;
  }

  return (
    <div
      className="fixed bottom-0 left-0 right-0 bg-red-950/90 border-t border-red-800 text-white p-2 z-50 transition-all duration-300 shadow-lg"
      style={{
        maxHeight: isCollapsed ? '42px' : '300px',
        overflow: 'hidden',
      }}
    >
      <div className="flex items-center justify-between py-1 px-2">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-red-400" />
          <span className="font-bold text-red-400">
            {errors.length} Error{errors.length !== 1 ? 's' : ''}
          </span>
          <span className="text-xs text-red-300">DEVELOPMENT MODE</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="text-red-400 hover:text-red-200 focus:outline-none"
          >
            {isCollapsed ? 'Expand' : 'Collapse'}
          </button>
        </div>
      </div>

      {!isCollapsed && (
        <div className="mt-2 max-h-[240px] overflow-y-auto">
          {errors.map((error) => (
            <div
              key={error.id}
              className="bg-red-900/50 mb-2 p-3 rounded border border-red-800 flex items-start justify-between"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono bg-red-800 px-1.5 py-0.5 rounded">
                    {error.type.toUpperCase()}
                  </span>
                  <span className="text-xs text-red-300">
                    {error.timestamp.toLocaleTimeString()}
                  </span>
                </div>
                <p className="mt-1 text-sm">{error.message}</p>
              </div>
              {onDismiss && (
                <button
                  onClick={() => onDismiss(error.id)}
                  className="text-red-400 hover:text-red-200 focus:outline-none"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ErrorDisplay;
