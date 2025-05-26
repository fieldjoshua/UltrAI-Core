import React from 'react';
import * as Sentry from '@sentry/react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      eventId: null,
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Capture error details for logging and debugging
    this.setState({ errorInfo });

    // Report to Sentry
    Sentry.withScope((scope) => {
      scope.setExtras(errorInfo);
      const eventId = Sentry.captureException(error);
      this.setState({ eventId });
    });

    // You could also log to an error reporting service here
    console.error('Error caught by ErrorBoundary:', error, errorInfo);
  }

  handleReportFeedback = () => {
    Sentry.showReportDialog({ eventId: this.state.eventId });
  };

  handleRetry = () => {
    // Reset the error state and retry rendering
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  renderErrorUI() {
    // You can customize this error UI as needed
    return (
      <div className="error-boundary-container" style={styles.container}>
        <div className="error-boundary-content" style={styles.content}>
          <h2 style={styles.heading}>Something went wrong</h2>
          <p style={styles.message}>
            We're sorry, but an unexpected error occurred. Our team has been
            notified.
          </p>

          {this.state.error && (
            <div className="error-details" style={styles.details}>
              <p style={styles.detailsHeading}>Error details:</p>
              <pre style={styles.code}>{this.state.error.toString()}</pre>
            </div>
          )}

          <div className="error-actions" style={styles.actions}>
            <button onClick={this.handleRetry} style={styles.retryButton}>
              Try Again
            </button>
            <button
              onClick={this.handleReportFeedback}
              style={styles.reportButton}
            >
              Report Feedback
            </button>
          </div>
        </div>
      </div>
    );
  }

  render() {
    if (this.state.hasError) {
      return this.renderErrorUI();
    }

    return this.props.children;
  }
}

// Styles for the error UI
const styles = {
  container: {
    padding: '20px',
    backgroundColor: '#f8f9fa',
    border: '1px solid #e3e3e3',
    borderRadius: '4px',
    margin: '20px 0',
    fontFamily:
      '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
  },
  content: {
    maxWidth: '600px',
    margin: '0 auto',
  },
  heading: {
    color: '#dc3545',
    fontSize: '24px',
    marginBottom: '10px',
    fontWeight: 600,
  },
  message: {
    fontSize: '16px',
    lineHeight: 1.5,
    color: '#343a40',
    marginBottom: '20px',
  },
  details: {
    marginBottom: '20px',
    padding: '10px',
    backgroundColor: '#f1f1f1',
    borderRadius: '4px',
  },
  detailsHeading: {
    fontWeight: 600,
    marginBottom: '5px',
    fontSize: '14px',
  },
  code: {
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
    fontSize: '12px',
    padding: '10px',
    backgroundColor: '#f8f9fa',
    border: '1px solid #e3e3e3',
    borderRadius: '4px',
    maxHeight: '200px',
    overflow: 'auto',
  },
  actions: {
    display: 'flex',
    gap: '10px',
    marginTop: '20px',
  },
  retryButton: {
    padding: '8px 16px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: 500,
  },
  reportButton: {
    padding: '8px 16px',
    backgroundColor: '#6c757d',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: 500,
  },
};

// Create a Sentry wrapped error boundary
const SentryErrorBoundary = Sentry.withErrorBoundary(ErrorBoundary, {
  showDialog: false, // We'll control this manually with the "Report Feedback" button
});

export default SentryErrorBoundary;
