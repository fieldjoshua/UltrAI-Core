import { useState, useCallback } from 'react';

interface ErrorState {
    hasError: boolean;
    message: string;
}

export const useErrorHandler = () => {
    const [error, setError] = useState<ErrorState>({ hasError: false, message: '' });

    const handleError = useCallback((err: unknown) => {
        console.error('Error occurred:', err);
        const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
        setError({ hasError: true, message: errorMessage });
    }, []);

    const clearError = useCallback(() => {
        setError({ hasError: false, message: '' });
    }, []);

    return { error, handleError, clearError };
};

export default useErrorHandler;