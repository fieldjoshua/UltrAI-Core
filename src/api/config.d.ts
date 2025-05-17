/**
 * Declaration file for API Configuration
 */

export const API_ERROR_EVENT: string;

/**
 * Report an API error that components can capture
 */
export function reportApiError(message: string, source?: string): void;

/**
 * Find an available backend server
 */
export function findAvailableServer(): Promise<string>;

/**
 * Get the API base URL
 */
export function getApiBaseUrl(): Promise<string>;

/**
 * Add a listener for API errors
 */
export function addApiErrorListener(callback: (errorDetail: any) => void): void;

/**
 * Remove a listener for API errors
 */
export function removeApiErrorListener(callback: (errorDetail: any) => void): void;

/**
 * Default export configuration
 */
declare const _default: {
  getApiBaseUrl: typeof getApiBaseUrl;
  findAvailableServer: typeof findAvailableServer;
  reportApiError: typeof reportApiError;
  addApiErrorListener: typeof addApiErrorListener;
  removeApiErrorListener: typeof removeApiErrorListener;
  API_ERROR_EVENT: string;
};

export default _default;
