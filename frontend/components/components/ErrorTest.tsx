'use client';

import React, { useEffect, useState } from 'react';
import { Button } from './ui/button';
import ErrorDisplay from './ErrorDisplay';
import { reportApiError } from '../api/config.js';

interface AppError {
  id: string;
  message: string;
  timestamp: Date;
  type: 'api' | 'general' | 'network';
}

export default function ErrorTest() {
  const [errors, setErrors] = useState<AppError[]>([]);

  // Add an error to the error state
  const addError = (
    message: string,
    type: 'api' | 'general' | 'network' = 'general'
  ) => {
    const newError: AppError = {
      id: Date.now().toString(),
      message,
      timestamp: new Date(),
      type,
    };

    console.log('Adding error:', newError);
    setErrors(prev => [...prev, newError]);
  };

  // Dismiss an error from the error state
  const dismissError = (id: string) => {
    console.log('Dismissing error with id:', id);
    setErrors(prev => prev.filter(error => error.id !== id));
  };

  // Function to trigger different types of errors
  const triggerApiError = () => {
    reportApiError('This is a test API error', 'test-component');
  };

  const triggerGeneralError = () => {
    addError('This is a general application error');
  };

  const triggerNetworkError = () => {
    addError('Failed to connect to the server', 'network');
  };

  // Listen for API errors
  useEffect(() => {
    const handleApiError = (event: CustomEvent) => {
      const errorDetail = event.detail;
      addError(errorDetail.message, 'api');
    };

    // Add event listener with type assertion
    document.addEventListener(
      'ultra-api-error',
      handleApiError as EventListener
    );

    // Cleanup function
    return () => {
      document.removeEventListener(
        'ultra-api-error',
        handleApiError as EventListener
      );
    };
  }, []);

  return (
    <div className="p-6 max-w-4xl mx-auto bg-gray-100 rounded-lg">
      <h1 className="text-2xl font-bold mb-4">Error Handling Test</h1>

      <div className="flex flex-col gap-4 mb-6">
        <Button onClick={triggerApiError} variant="destructive">
          Trigger API Error
        </Button>

        <Button onClick={triggerGeneralError} variant="destructive">
          Trigger General Error
        </Button>

        <Button onClick={triggerNetworkError} variant="destructive">
          Trigger Network Error
        </Button>
      </div>

      <div className="mt-8">
        <ErrorDisplay errors={errors} onDismiss={dismissError} />
      </div>
    </div>
  );
}
