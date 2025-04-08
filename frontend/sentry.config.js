// Sentry Configuration
const { withSentryConfig } = require('@sentry/nextjs');

const sentryWebpackPluginOptions = {
  // Additional config options for the Sentry webpack plugin.
  // Keep in mind that webpack plugin comes with sensible defaults,
  // but you can customize them if needed.
  silent: process.env.NODE_ENV === 'production', // Suppresses all logs
  authToken: process.env.SENTRY_AUTH_TOKEN,
  org: process.env.SENTRY_ORG,
  project: process.env.SENTRY_PROJECT,

  // Upload source maps only in production
  include: '.next',
  ignore: ['node_modules', 'webpack.config.js'],

  // Strip development paths for better anonymized issue tracking
  stripPrefix: ['webpack://_N_E/'],
  urlPrefix: '~/_next',

  // Enable performance monitoring
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.2 : 1.0,

  // Set specific environment for better grouping
  environment: process.env.ENVIRONMENT || process.env.NODE_ENV || 'development',

  // Error handling and security settings
  beforeSend(event) {
    // Don't send PII data
    if (event.request && event.request.headers) {
      // Delete sensitive headers
      delete event.request.headers.Authorization;
      delete event.request.headers.Cookie;
      delete event.request.headers['X-Forwarded-For'];
    }

    // Don't report 404 errors
    if (
      event.exception &&
      event.exception.values &&
      event.exception.values[0] &&
      event.exception.values[0].type === 'NotFoundError'
    ) {
      return null;
    }

    return event;
  },
};

// Export the Sentry config
module.exports = {
  sentryWebpackPluginOptions,

  // For applying to Next.js or other frameworks
  withSentryConfig: (config) =>
    withSentryConfig(config, sentryWebpackPluginOptions),
};
