import React from 'react';
import { render, screen } from '@testing-library/react';
import { AnalysisResults } from '../AnalysisResults';

describe('AnalysisResults', () => {
  const mockResults = [
    {
      model_id: 'gpt-4',
      model_name: 'GPT-4',
      content: 'Test response from GPT-4',
      timestamp: '2024-04-28T12:00:00Z',
    },
    {
      model_id: 'claude-3',
      model_name: 'Claude 3',
      content: 'Test response from Claude 3',
      timestamp: '2024-04-28T12:00:00Z',
    },
  ];

  it('renders loading state', () => {
    render(<AnalysisResults results={[]} isLoading={true} />);

    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('renders empty state', () => {
    render(<AnalysisResults results={[]} isLoading={false} />);

    expect(
      screen.getByText(
        'No analysis results available. Submit a prompt to begin analysis.'
      )
    ).toBeInTheDocument();
  });

  it('renders results with tabs', () => {
    render(<AnalysisResults results={mockResults} isLoading={false} />);

    // Check tab headers
    expect(screen.getByRole('tab', { name: 'GPT-4' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Claude 3' })).toBeInTheDocument();

    // Check first tab content
    expect(screen.getByText('Test response from GPT-4')).toBeInTheDocument();
    expect(
      screen.getByText('Analysis completed at 4/28/2024, 12:00:00 PM')
    ).toBeInTheDocument();
  });

  it('switches between tabs', () => {
    render(<AnalysisResults results={mockResults} isLoading={false} />);

    // Click on Claude 3 tab
    const claudeTab = screen.getByRole('tab', { name: 'Claude 3' });
    claudeTab.click();

    // Check Claude 3 content
    expect(screen.getByText('Test response from Claude 3')).toBeInTheDocument();
  });

  it('formats timestamps correctly', () => {
    const resultsWithDifferentTimestamps = [
      {
        ...mockResults[0],
        timestamp: '2024-04-28T15:30:00Z',
      },
    ];

    render(
      <AnalysisResults
        results={resultsWithDifferentTimestamps}
        isLoading={false}
      />
    );

    expect(
      screen.getByText('Analysis completed at 4/28/2024, 3:30:00 PM')
    ).toBeInTheDocument();
  });

  it('handles missing timestamps', () => {
    const resultsWithoutTimestamp = [
      {
        ...mockResults[0],
        timestamp: '',
      },
    ];

    render(
      <AnalysisResults results={resultsWithoutTimestamp} isLoading={false} />
    );

    expect(screen.getByText('Test response from GPT-4')).toBeInTheDocument();
  });

  it('maintains tab selection after re-render', () => {
    const { rerender } = render(
      <AnalysisResults results={mockResults} isLoading={false} />
    );

    // Click on Claude 3 tab
    const claudeTab = screen.getByRole('tab', { name: 'Claude 3' });
    claudeTab.click();

    // Re-render with same props
    rerender(<AnalysisResults results={mockResults} isLoading={false} />);

    // Check if Claude 3 content is still visible
    expect(screen.getByText('Test response from Claude 3')).toBeInTheDocument();
  });
});
