import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import PromptStep from '../components/steps/PromptStep';

describe('PromptStep', () => {
  const mockProps = {
    prompt: '',
    setPrompt: jest.fn(),
    isProcessing: false,
    isOffline: false,
    error: null,
    goToNextStep: jest.fn(),
    goToPreviousStep: jest.fn(),
  };

  it('renders without crashing', () => {
    render(<PromptStep {...mockProps} />);
    expect(
      screen.getByText('What would you like Ultra to analyze?')
    ).toBeInTheDocument();
  });

  it('handles prompt input', () => {
    render(<PromptStep {...mockProps} />);
    const textarea = screen.getByRole('textbox');
    fireEvent.change(textarea, { target: { value: 'Test prompt' } });
    expect(mockProps.setPrompt).toHaveBeenCalledWith('Test prompt');
  });

  it('displays character count', () => {
    render(<PromptStep {...mockProps} prompt="Test prompt" />);
    expect(screen.getByText('11 characters')).toBeInTheDocument();
  });

  it('shows error message when provided', () => {
    render(<PromptStep {...mockProps} error="Invalid prompt" />);
    expect(screen.getByText('Invalid prompt')).toBeInTheDocument();
  });

  it('disables input when processing', () => {
    render(<PromptStep {...mockProps} isProcessing={true} />);
    const textarea = screen.getByRole('textbox');
    expect(textarea).toBeDisabled();
  });

  it('disables input when offline', () => {
    render(<PromptStep {...mockProps} isOffline={true} />);
    const textarea = screen.getByRole('textbox');
    expect(textarea).toBeDisabled();
  });
});
