/**
 * API Error Handler Utility for UltraAI
 *
 * This utility provides functions for handling API errors consistently
 * and provides retry capability for transient errors.
 */

type ErrorResponse = {
  status: string;
  message: string;
  code: string;
  details?: Array<{
    type: string;
    msg: string;
    loc?: string[];
    ctx?: Record<string, any>;
  }>;
  request_id?: string;
};

// Error severity levels
export enum ErrorSeverity {
  CRITICAL = 'critical',
  ERROR = 'error',
  WARNING = 'warning',
  INFO = 'info',
}

// Custom API Error class
export class ApiError extends Error {
  status: number;
  errorResponse: ErrorResponse;
  severity: ErrorSeverity;
  isRetryable: boolean;

  constructor(
    status: number,
    errorResponse: ErrorResponse,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    isRetryable: boolean = false
  ) {
    super(errorResponse.message || 'API Error');
    this.name = 'ApiError';
    this.status = status;
    this.errorResponse = errorResponse;
    this.severity = severity;
    this.isRetryable = isRetryable;
  }

  get code(): string {
    return this.errorResponse.code;
  }

  get requestId(): string | undefined {
    return this.errorResponse.request_id;
  }

  get details(): any[] | undefined {
    return this.errorResponse.details;
  }
}

// Determine if an error is retryable based on status code and error code
export function isRetryableError(status: number, errorCode?: string): boolean {
  // Network errors and timeouts are retryable
  if (
    status === 0 ||
    status === 408 ||
    status === 429 ||
    status === 503 ||
    status === 504
  ) {
    return true;
  }

  // Certain error codes indicate retryable errors
  if (errorCode) {
    const retryableCodes = [
      'timeout',
      'service_unavailable',
      'rate_limit_exceeded',
      'network_error',
      'connection_error',
      'gateway_timeout',
    ];
    return retryableCodes.includes(errorCode);
  }

  return false;
}

// Determine severity based on status code
export function getErrorSeverity(status: number): ErrorSeverity {
  if (status >= 500) return ErrorSeverity.ERROR;
  if (status >= 400) return ErrorSeverity.WARNING;
  return ErrorSeverity.INFO;
}

// Parse error response from fetch API
export async function parseErrorResponse(
  response: Response
): Promise<ApiError> {
  let errorResponse: ErrorResponse;

  try {
    // Try to parse as JSON
    errorResponse = await response.json();
  } catch (e) {
    // If not JSON, create a generic error response
    errorResponse = {
      status: 'error',
      message: response.statusText || 'Unknown error',
      code: `http_${response.status}`,
    };
  }

  const severity = getErrorSeverity(response.status);
  const isRetryable = isRetryableError(response.status, errorResponse.code);

  return new ApiError(response.status, errorResponse, severity, isRetryable);
}

// Retry function with exponential backoff
export async function retryFetch(
  url: string,
  options: RequestInit,
  maxRetries: number = 3,
  initialDelayMs: number = 300
): Promise<Response> {
  let lastError: ApiError | Error | null = null;
  let retries = 0;
  let delay = initialDelayMs;

  while (retries <= maxRetries) {
    try {
      const response = await fetch(url, options);

      if (response.ok) {
        return response;
      }

      // Parse error response
      const error = await parseErrorResponse(response);

      // If not retryable, throw immediately
      if (!error.isRetryable) {
        throw error;
      }

      lastError = error;
    } catch (error) {
      // If it's an ApiError and not retryable, rethrow
      if (error instanceof ApiError && !error.isRetryable) {
        throw error;
      }

      // For network errors or retryable API errors, continue retry loop
      lastError = error instanceof Error ? error : new Error(String(error));
    }

    // If we've used all retries, throw the last error
    if (retries === maxRetries) {
      if (lastError) throw lastError;
      throw new Error('Request failed after multiple retries');
    }

    // Wait before retrying (exponential backoff with jitter)
    const jitter = Math.random() * 0.2 * delay;
    await new Promise(resolve => setTimeout(resolve, delay + jitter));

    // Increase delay for next attempt
    delay *= 2;
    retries++;
  }

  // This should never be reached due to the throw in the retry loop
  throw new Error('Unexpected error in retry logic');
}

// Format validation errors into a user-friendly message
export function formatValidationErrors(details?: any[]): string {
  if (!details || details.length === 0) {
    return 'Validation error';
  }

  return details
    .map(detail => {
      const location = detail.loc ? detail.loc.join('.') : '';
      return location ? `${location}: ${detail.msg}` : detail.msg;
    })
    .join('\n');
}

// Default error handler that could be used across the application
export function handleApiError(
  error: unknown,
  onError?: (error: ApiError) => void
): string {
  // Network errors
  if (error instanceof TypeError && error.message === 'Failed to fetch') {
    return 'Network error: Could not connect to the server. Please check your internet connection.';
  }

  // API errors
  if (error instanceof ApiError) {
    // Call the onError callback if provided
    if (onError) onError(error);

    // For validation errors, format the details
    if (error.code === 'validation_error' && error.details) {
      return formatValidationErrors(error.details);
    }

    return error.message;
  }

  // Other errors
  if (error instanceof Error) {
    return error.message;
  }

  return 'An unexpected error occurred';
}

export default {
  ApiError,
  isRetryableError,
  getErrorSeverity,
  parseErrorResponse,
  retryFetch,
  formatValidationErrors,
  handleApiError,
  ErrorSeverity,
};
