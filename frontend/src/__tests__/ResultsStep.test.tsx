import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ResultsStep from '../components/steps/ResultsStep';

describe('ResultsStep', () => {
  const mockProps = {
    prompt: 'Test prompt',
    output: 'Test output',
    isOffline: false,
    outputRef: { current: null },
    onStartNewAnalysis: jest.fn(),
    onShowHistory: jest.fn(),
    onShareAnalysis: jest.fn(),
    onSaveToHistory: jest.fn(),
  };

  it('renders without crashing', () => {
    render(<ResultsStep {...mockProps} />);
    expect(screen.getByText('Ultra Analysis Results')).toBeInTheDocument();
  });

  it('displays prompt and output', () => {
    render(<ResultsStep {...mockProps} />);
    expect(screen.getByText('Test prompt')).toBeInTheDocument();
    expect(screen.getByText('Test output')).toBeInTheDocument();
  });

  it('handles new analysis button click', () => {
    render(<ResultsStep {...mockProps} />);
    const newAnalysisButton = screen.getByText('Start New Analysis');
    fireEvent.click(newAnalysisButton);
    expect(mockProps.onStartNewAnalysis).toHaveBeenCalled();
  });

  it('handles history button click', () => {
    render(<ResultsStep {...mockProps} />);
    const historyButton = screen.getByText('View History');
    fireEvent.click(historyButton);
    expect(mockProps.onShowHistory).toHaveBeenCalled();
  });

  it('handles share button click', () => {
    render(<ResultsStep {...mockProps} />);
    const shareButton = screen.getByText('Share');
    fireEvent.click(shareButton);
    expect(mockProps.onShareAnalysis).toHaveBeenCalled();
  });

  it('handles save button click', () => {
    render(<ResultsStep {...mockProps} />);
    const saveButton = screen.getByText('Save');
    fireEvent.click(saveButton);
    expect(mockProps.onSaveToHistory).toHaveBeenCalled();
  });

  it('disables buttons when offline', () => {
    render(<ResultsStep {...mockProps} isOffline={true} />);
    const newAnalysisButton = screen.getByText('Start New Analysis');
    const shareButton = screen.getByText('Share');
    const saveButton = screen.getByText('Save');

    expect(newAnalysisButton).toBeDisabled();
    expect(shareButton).toBeDisabled();
    expect(saveButton).toBeDisabled();
  });

  it('shows no output message when output is empty', () => {
    render(<ResultsStep {...mockProps} output="" />);
    expect(
      screen.getByText('No output generated or loaded.')
    ).toBeInTheDocument();
  });
});
