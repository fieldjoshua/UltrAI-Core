import React, { useState, useEffect } from 'react';
import { Progress } from '../ui/progress';
import { AlertCircle, CheckCircle, Clock, X } from 'lucide-react';
import { Button } from '../ui/button';

export interface AnalysisProgressProps {
  status: 'idle' | 'preparing' | 'analyzing' | 'complete' | 'error';
  currentStep?: number;
  totalSteps?: number;
  estimatedTimeRemaining?: number;
  statusMessage?: string;
  error?: Error;
  onCancel?: () => void;
}

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({
  status,
  currentStep = 0,
  totalSteps = 1,
  estimatedTimeRemaining,
  statusMessage,
  error,
  onCancel,
}) => {
  const [progress, setProgress] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [startTime] = useState(Date.now());

  // Calculate progress percentage
  useEffect(() => {
    if (status === 'idle') {
      setProgress(0);
    } else if (status === 'complete') {
      setProgress(100);
    } else if (status === 'error') {
      // Keep the progress where it was when the error occurred
    } else {
      // Calculate progress based on steps
      const stepProgress =
        totalSteps > 0 ? (currentStep / totalSteps) * 100 : 0;
      setProgress(Math.min(Math.max(stepProgress, 0), 99)); // Cap between 0-99% until complete
    }
  }, [status, currentStep, totalSteps]);

  // Track elapsed time
  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (status === 'preparing' || status === 'analyzing') {
      interval = setInterval(() => {
        setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [status, startTime]);

  // Format time for display
  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  // Status indicator based on current status
  const renderStatusIndicator = () => {
    switch (status) {
      case 'idle':
        return <Clock className="h-5 w-5 text-gray-500" />;
      case 'preparing':
      case 'analyzing':
        return (
          <svg
            className="animate-spin h-5 w-5 text-blue-500"
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
        );
      case 'complete':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return null;
    }
  };

  // Status text based on current status
  const getStatusText = (): string => {
    if (statusMessage) return statusMessage;

    switch (status) {
      case 'idle':
        return 'Waiting to start analysis...';
      case 'preparing':
        return 'Preparing analysis...';
      case 'analyzing':
        return currentStep && totalSteps
          ? `Analyzing (Step ${currentStep} of ${totalSteps})...`
          : 'Analyzing...';
      case 'complete':
        return 'Analysis complete';
      case 'error':
        return error?.message || 'An error occurred during analysis';
      default:
        return '';
    }
  };

  return (
    <div
      className={`rounded-lg p-4 ${
        status === 'error'
          ? 'bg-red-50'
          : status === 'complete'
            ? 'bg-green-50'
            : 'bg-blue-50'
      }`}
    >
      <div className="flex items-center mb-3">
        {renderStatusIndicator()}
        <span
          className={`ml-2 font-medium ${
            status === 'error'
              ? 'text-red-700'
              : status === 'complete'
                ? 'text-green-700'
                : 'text-blue-700'
          }`}
        >
          {getStatusText()}
        </span>
      </div>

      {/* Progress bar */}
      <Progress
        value={progress}
        className={`h-2 ${
          status === 'error'
            ? 'bg-red-100'
            : status === 'complete'
              ? 'bg-green-100'
              : 'bg-blue-100'
        }`}
      />

      {/* Time information */}
      <div className="flex justify-between mt-2 text-sm">
        <div className="text-gray-600">
          {status === 'preparing' || status === 'analyzing' ? (
            <>Elapsed time: {formatTime(elapsedTime)}</>
          ) : status === 'complete' ? (
            <>Total time: {formatTime(elapsedTime)}</>
          ) : null}
        </div>
        <div className="text-gray-600">
          {estimatedTimeRemaining !== undefined &&
            status !== 'complete' &&
            status !== 'error' && (
              <>Est. remaining: {formatTime(estimatedTimeRemaining)}</>
            )}
        </div>
      </div>

      {/* Step indicators for multi-stage processes */}
      {totalSteps > 1 && status !== 'idle' && (
        <div className="mt-4">
          <div className="flex justify-between mb-1">
            <span className="text-xs text-gray-600">Progress</span>
            <span className="text-xs text-gray-600">
              {currentStep} of {totalSteps} steps
            </span>
          </div>
          <div className="flex space-x-1">
            {Array.from({ length: totalSteps }).map((_, i) => (
              <div
                key={i}
                className={`h-1.5 rounded-full flex-1 ${
                  i < currentStep
                    ? 'bg-blue-500'
                    : i === currentStep &&
                        (status === 'preparing' || status === 'analyzing')
                      ? 'bg-blue-300'
                      : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
        </div>
      )}

      {/* Error details */}
      {status === 'error' && error && (
        <div className="mt-3 p-2 bg-red-100 rounded text-sm text-red-800">
          {error.message}
        </div>
      )}

      {/* Cancel button */}
      {(status === 'preparing' || status === 'analyzing') && onCancel && (
        <div className="mt-3 flex justify-end">
          <Button
            variant="ghost"
            size="sm"
            onClick={onCancel}
            className="text-gray-500 hover:text-gray-700"
          >
            <X className="h-4 w-4 mr-1" />
            Cancel
          </Button>
        </div>
      )}
    </div>
  );
};

export default AnalysisProgress;
