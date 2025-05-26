import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { PromptInput } from '../PromptInput';

describe('PromptInput', () => {
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  it('renders correctly', () => {
    render(<PromptInput onSubmit={mockOnSubmit} />);

    expect(
      screen.getByPlaceholderText('Enter your prompt here...')
    ).toBeInTheDocument();
    expect(screen.getByRole('button')).toHaveTextContent('Analyze Prompt');
  });

  it('handles empty prompt submission', () => {
    render(<PromptInput onSubmit={mockOnSubmit} />);

    const submitButton = screen.getByRole('button');
    fireEvent.click(submitButton);

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('handles valid prompt submission', () => {
    render(<PromptInput onSubmit={mockOnSubmit} />);

    const textarea = screen.getByPlaceholderText('Enter your prompt here...');
    const submitButton = screen.getByRole('button');

    fireEvent.change(textarea, { target: { value: 'Test prompt' } });
    fireEvent.click(submitButton);

    expect(mockOnSubmit).toHaveBeenCalledWith('Test prompt');
  });

  it('trims whitespace from prompt', () => {
    render(<PromptInput onSubmit={mockOnSubmit} />);

    const textarea = screen.getByPlaceholderText('Enter your prompt here...');
    const submitButton = screen.getByRole('button');

    fireEvent.change(textarea, { target: { value: '  Test prompt  ' } });
    fireEvent.click(submitButton);

    expect(mockOnSubmit).toHaveBeenCalledWith('Test prompt');
  });

  it('disables input and button when loading', () => {
    render(<PromptInput onSubmit={mockOnSubmit} isLoading={true} />);

    const textarea = screen.getByPlaceholderText('Enter your prompt here...');
    const submitButton = screen.getByRole('button');

    expect(textarea).toBeDisabled();
    expect(submitButton).toBeDisabled();
    expect(submitButton).toHaveTextContent('Analyzing...');
  });

  it('handles form submission', () => {
    render(<PromptInput onSubmit={mockOnSubmit} />);

    const textarea = screen.getByPlaceholderText('Enter your prompt here...');
    const form = screen.getByRole('form');

    fireEvent.change(textarea, { target: { value: 'Test prompt' } });
    fireEvent.submit(form);

    expect(mockOnSubmit).toHaveBeenCalledWith('Test prompt');
  });
});
