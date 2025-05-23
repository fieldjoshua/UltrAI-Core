import React from 'react';
import { Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from './button';
import { cn } from './utils';

interface FallbackProps {
  title?: string;
  message?: string;
  isLoading?: boolean;
  isError?: boolean;
  retry?: () => void;
  className?: string;
  icon?: React.ReactNode;
}

/**
 * Fallback component to display during loading states, errors, or when content is unavailable
 */
const Fallback: React.FC<FallbackProps> = ({
  title,
  message,
  isLoading = false,
  isError = false,
  retry,
  className,
  icon,
}) => {
  // Determine icon based on state
  const IconComponent = React.useMemo(() => {
    if (icon) return icon;
    if (isLoading)
      return (
        <Loader2 className="h-10 w-10 animate-spin text-muted-foreground" />
      );
    if (isError) return <AlertCircle className="h-10 w-10 text-destructive" />;
    return null;
  }, [icon, isLoading, isError]);

  // Determine default title based on state
  const defaultTitle = isLoading
    ? 'Loading...'
    : isError
      ? 'Something went wrong'
      : 'No content available';

  return (
    <div
      className={cn(
        'flex min-h-[200px] w-full flex-col items-center justify-center rounded-lg border border-dashed p-8 text-center',
        isError
          ? 'border-destructive/30 bg-destructive/5'
          : 'border-border bg-muted/50',
        className
      )}
    >
      {IconComponent && <div className="mb-4">{IconComponent}</div>}

      <h3 className="text-lg font-medium text-foreground">
        {title || defaultTitle}
      </h3>

      {message && (
        <p className="mt-2 max-w-md text-sm text-muted-foreground">{message}</p>
      )}

      {retry && !isLoading && (
        <Button variant="outline" size="sm" className="mt-4" onClick={retry}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Try again
        </Button>
      )}
    </div>
  );
};

// Loading variant
const LoadingFallback: React.FC<
  Omit<FallbackProps, 'isLoading' | 'isError'>
> = props => <Fallback {...props} isLoading={true} isError={false} />;

// Error variant
const ErrorFallback: React.FC<
  Omit<FallbackProps, 'isLoading' | 'isError'>
> = props => <Fallback {...props} isLoading={false} isError={true} />;

export { Fallback, LoadingFallback, ErrorFallback };
