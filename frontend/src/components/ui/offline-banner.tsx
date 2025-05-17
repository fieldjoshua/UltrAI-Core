import React, { useState, useEffect } from 'react';
import { Wifi, WifiOff, AlertTriangle } from 'lucide-react';

interface OfflineBannerProps {
  checkInterval?: number; // milliseconds
  customMessage?: string;
  apiEndpoint?: string;
  onStatusChange?: (isOnline: boolean) => void;
}

export const OfflineBanner: React.FC<OfflineBannerProps> = ({
  checkInterval = 30000, // default to 30 seconds
  customMessage,
  apiEndpoint = '/api/health',
  onStatusChange,
}) => {
  const [isOnline, setIsOnline] = useState<boolean>(navigator.onLine);
  const [apiAvailable, setApiAvailable] = useState<boolean>(true);
  const [isVisible, setIsVisible] = useState<boolean>(false);

  // Check network status
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      // When we come back online, check the API
      checkApiStatus();
    };

    const handleOffline = () => {
      setIsOnline(false);
      setApiAvailable(false);
      setIsVisible(true);
      if (onStatusChange) onStatusChange(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Initial API check
    checkApiStatus();

    // Set up interval for API checks
    const intervalId = setInterval(checkApiStatus, checkInterval);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(intervalId);
    };
  }, [checkInterval, apiEndpoint, onStatusChange]);

  // Check API endpoint
  const checkApiStatus = async () => {
    if (!isOnline) {
      setApiAvailable(false);
      setIsVisible(true);
      return;
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(apiEndpoint, {
        method: 'GET',
        signal: controller.signal,
        headers: { 'Cache-Control': 'no-cache' },
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        setApiAvailable(true);
        setIsVisible(false);
        if (onStatusChange) onStatusChange(true);
      } else {
        setApiAvailable(false);
        setIsVisible(true);
        if (onStatusChange) onStatusChange(false);
      }
    } catch (error) {
      console.warn('API check failed:', error);
      setApiAvailable(false);
      setIsVisible(true);
      if (onStatusChange) onStatusChange(false);
    }
  };

  // Handle manual dismiss
  const handleDismiss = () => {
    setIsVisible(false);
  };

  // Don't render anything if everything is online and the banner isn't visible
  if (!isVisible) {
    return null;
  }

  return (
    <div
      className={`fixed bottom-0 left-0 right-0 z-50 p-2 transition-transform duration-200 transform ${
        isVisible ? 'translate-y-0' : 'translate-y-full'
      }`}
    >
      <div
        className={`w-full max-w-4xl mx-auto rounded-lg shadow-lg ${
          !isOnline
            ? 'bg-red-600 text-white'
            : !apiAvailable
              ? 'bg-amber-500 text-amber-950'
              : 'bg-green-600 text-white'
        }`}
      >
        <div className="p-3 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {!isOnline ? (
              <WifiOff className="h-5 w-5" />
            ) : !apiAvailable ? (
              <AlertTriangle className="h-5 w-5" />
            ) : (
              <Wifi className="h-5 w-5" />
            )}

            <span className="font-medium">
              {customMessage ||
                (!isOnline
                  ? 'You are offline. Some features may be unavailable.'
                  : !apiAvailable
                    ? 'Server connection issues. Limited functionality available.'
                    : 'Connected')}
            </span>
          </div>

          <div className="flex items-center space-x-2">
            {!isOnline ? (
              <button
                onClick={checkApiStatus}
                className="px-3 py-1 text-sm bg-red-700 hover:bg-red-800 text-white rounded"
              >
                Retry
              </button>
            ) : !apiAvailable ? (
              <button
                onClick={checkApiStatus}
                className="px-3 py-1 text-sm bg-amber-600 hover:bg-amber-700 text-white rounded"
              >
                Retry
              </button>
            ) : null}

            <button
              onClick={handleDismiss}
              className="p-1 rounded hover:bg-black/10"
              aria-label="Dismiss"
            >
              <svg
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        {(!isOnline || !apiAvailable) && (
          <div className="px-4 pb-3 text-sm">
            <p>
              {!isOnline
                ? 'Local cached data is being used. Changes will sync when you reconnect.'
                : 'Trying to reconnect to the server. Some operations are still available in offline mode.'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default OfflineBanner;
