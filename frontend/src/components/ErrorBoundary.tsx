import React from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { screenReader } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';

interface ErrorBoundaryProps {
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    this.setState({
      error,
      errorInfo,
    });
    screenReader.announce(
      'An error has occurred. Please try again or contact support.',
      'assertive'
    );
  }

  handleRetry = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
    screenReader.announce('Retrying...', 'polite');
  };

  render(): React.ReactNode {
    if (this.state.hasError) {
      return (
        <Card className="w-full p-4">
          <div role="alert" aria-live="assertive" className="space-y-4">
            <h2 className="text-xl font-semibold text-red-600">
              Something went wrong
            </h2>
            <div className="space-y-2">
              <p className="text-gray-700">
                {this.state.error?.message || 'An unexpected error occurred'}
              </p>
              {process.env.NODE_ENV === 'development' &&
                this.state.errorInfo && (
                  <details className="mt-4">
                    <summary className="cursor-pointer text-sm text-gray-500">
                      Error details
                    </summary>
                    <pre
                      className="mt-2 p-4 bg-gray-100 rounded-lg overflow-auto text-sm"
                      aria-label="Error stack trace"
                    >
                      {this.state.errorInfo.componentStack}
                    </pre>
                  </details>
                )}
            </div>
            <div className="flex space-x-4">
              <Button
                onClick={this.handleRetry}
                className="bg-blue-600 text-white hover:bg-blue-700"
                aria-label="Retry loading the component"
              >
                Try again
              </Button>
              <Button
                onClick={() => window.location.reload()}
                className="bg-gray-600 text-white hover:bg-gray-700"
                aria-label="Reload the page"
              >
                Reload page
              </Button>
            </div>
          </div>
        </Card>
      );
    }

    return this.props.children;
  }
}
