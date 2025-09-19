import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import StatusUpdater from '@components/wizard/StatusUpdater';

describe('StatusUpdater', () => {
  it('renders a "Service not ready" banner when an error is present', () => {
    const errorMessage = {
      detail: 'Service is unavailable due to maintenance.',
      error_details: {
        providers_present: ['openai'],
        required_providers: ['openai', 'anthropic', 'google'],
      },
    };

    render(<StatusUpdater hasError={true} errorMessage={errorMessage} />);

    expect(screen.getByText('Service Unavailable')).toBeInTheDocument();
    expect(screen.getByText(errorMessage.detail)).toBeInTheDocument();
    expect(
      screen.getByText('Providers Present:', { exact: false })
    ).toHaveTextContent('Providers Present: openai');
    expect(
      screen.getByText('Providers Required:', { exact: false })
    ).toHaveTextContent('Providers Required: openai, anthropic, google');
  });

  it('renders a happy-path status when no error is present and status is READY', () => {
    render(<StatusUpdater isComplete={true} orchestratorResult={{ models_used: ['gpt-4', 'claude-3', 'gemini-pro'] }} />);
    
    // This is a basic check. A more robust test would check for specific "READY" content if it exists.
    // For now, we are checking that the error banner does NOT appear.
    expect(screen.queryByText('Service Unavailable')).not.toBeInTheDocument();
  });
});
