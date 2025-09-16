import React, { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { LoginForm } from '../components/auth/LoginForm';
import { CheckCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

export const LoginPage: React.FC = () => {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const justRegistered = searchParams.get('registered') === 'true';

  useEffect(() => {
    // Clear the registered param after showing the message
    if (justRegistered) {
      const timer = setTimeout(() => {
        window.history.replaceState({}, '', '/login');
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [justRegistered]);

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-gray-900">
      <div className="w-full max-w-md space-y-8">
        {justRegistered && (
          <Alert className="bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800">
            <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
            <AlertDescription className="text-green-800 dark:text-green-200">
              Registration successful! Please log in with your new account.
            </AlertDescription>
          </Alert>
        )}

        <LoginForm />
      </div>
    </div>
  );
};
