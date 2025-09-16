/**
 * API Configuration for UltraAI
 */

// Default ports to try for API connection in order of preference
const API_PORTS = [8087, 8088, 8085, 8086, 8089];

// Default API base URL template
const API_BASE_URL_TEMPLATE = 'http://localhost:PORT';

// Production API URL
const PRODUCTION_API_URL = 'https://ultrai-core.onrender.com';

// Check if running in production
const isProduction =
  import.meta?.env?.PROD || process.env.NODE_ENV === 'production';

// Time to cache server availability check (5 seconds)
const SERVER_CACHE_TIME = 5000;

// Cache for server availability
let serverCache = {
  port: 8087, // Force use of port 8087 initially
  timestamp: 0, // Set to 0 to force a fresh check
};

// Create a custom event for API errors that components can listen to
const API_ERROR_EVENT = 'ultra-api-error';

/**
 * Dispatch an API error event that can be captured by components
 * @param {string} message - Error message
 * @param {string} source - Source of the error (e.g. 'findAvailableServer', 'getApiBaseUrl')
 */
export const reportApiError = (message, source = 'api') => {
  // Log to console
  console.error(`[API Error] ${source}: ${message}`);

  // Create and dispatch a custom event that components can listen for
  const errorEvent = new CustomEvent(API_ERROR_EVENT, {
    detail: {
      message,
      source,
      timestamp: new Date(),
      id: Date.now().toString(),
    },
  });

  document.dispatchEvent(errorEvent);
};

/**
 * Find an available backend server
 * @returns {Promise<string>} The base URL for the API
 */
export const findAvailableServer = async () => {
  // If we have a cached server that's still valid, use it
  const now = Date.now();
  if (serverCache.port && now - serverCache.timestamp < SERVER_CACHE_TIME) {
    return API_BASE_URL_TEMPLATE.replace('PORT', serverCache.port);
  }

  // Try each port in order
  for (const port of API_PORTS) {
    try {
      const url = API_BASE_URL_TEMPLATE.replace('PORT', port);
      const response = await fetch(`${url}/api/health`, {
        method: 'GET',
        headers: { Accept: 'application/json' },
        // Short timeout to quickly move to next port if this one is unavailable
        signal: AbortSignal.timeout(500),
      });

      if (response.ok) {
        // Cache the working port
        serverCache = {
          port,
          timestamp: now,
        };
        console.log(`Found API server at ${url}`);
        return url;
      }
    } catch (error) {
      // Connection failed, try next port
      console.log(`API server not available at port ${port}`);
    }
  }

  // If no server was found, return the default port
  // This will likely fail, but at least the client will have a URL to try
  const errorMessage = 'No API server found, using default port';
  console.warn(errorMessage);
  reportApiError(errorMessage, 'server-discovery');
  return API_BASE_URL_TEMPLATE.replace('PORT', API_PORTS[0]);
};

/**
 * Get the API base URL
 * @returns {Promise<string>} The base URL for the API
 */
export const getApiBaseUrl = async () => {
  // In production, always use the production URL
  if (isProduction) {
    return PRODUCTION_API_URL;
  }

  // In development, try to find an available local server
  try {
    return await findAvailableServer();
  } catch (error) {
    const errorMessage = `Failed to find available server: ${error.message}`;
    reportApiError(errorMessage, 'get-api-base-url');
    return API_BASE_URL_TEMPLATE.replace('PORT', API_PORTS[0]);
  }
};

// Helper function to add a listener for API errors
export const addApiErrorListener = callback => {
  document.addEventListener(API_ERROR_EVENT, event => {
    callback(event.detail);
  });
};

// Helper function to remove a listener for API errors
export const removeApiErrorListener = callback => {
  document.removeEventListener(API_ERROR_EVENT, callback);
};

export default {
  getApiBaseUrl,
  findAvailableServer,
  reportApiError,
  addApiErrorListener,
  removeApiErrorListener,
  API_ERROR_EVENT,
};
