import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { PromptInput } from '../PromptInput';

describe('PromptInput', () => {
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  it('renders with default props', () => {
    render(<PromptInput onSubmit={mockOnSubmit} />);

    expect(
      screen.getByPlaceholderText('Enter your prompt here...')
    ).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Submit' })).toBeInTheDocument();
  });

  it('renders with custom placeholder', () => {
    const customPlaceholder = 'Custom placeholder text';
    render(
      <PromptInput onSubmit={mockOnSubmit} placeholder={customPlaceholder} />
    );

    expect(screen.getByPlaceholderText(customPlaceholder)).toBeInTheDocument();
  });

  it('disables input and button when disabled prop is true', () => {
    render(<PromptInput onSubmit={mockOnSubmit} disabled={true} />);

    const textarea = screen.getByRole('textbox');
    const button = screen.getByRole('button');

    expect(textarea).toBeDisabled();
    expect(button).toBeDisabled();
  });

  it('shows loading state when isLoading is true', () => {
    render(<PromptInput onSubmit={mockOnSubmit} isLoading={true} />);

    expect(
      screen.getByRole('button', { name: 'Submitting...' })
    ).toBeInTheDocument();
  });

  it('calls onSubmit with trimmed prompt when submitted', async () => {
    render(<PromptInput onSubmit={mockOnSubmit} />);

    const textarea = screen.getByRole('textbox');
    const button = screen.getByRole('button');

    fireEvent.change(textarea, { target: { value: '  Test prompt  ' } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith('Test prompt');
    });
  });

  it('does not call onSubmit when prompt is empty', () => {
    render(<PromptInput onSubmit={mockOnSubmit} />);

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('disables submit button when prompt is empty', () => {
    render(<PromptInput onSubmit={mockOnSubmit} />);

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });
});
