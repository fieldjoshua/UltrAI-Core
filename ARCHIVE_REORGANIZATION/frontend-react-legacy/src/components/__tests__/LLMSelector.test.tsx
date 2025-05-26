import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { LLMSelector } from '../LLMSelector';

describe('LLMSelector', () => {
  const mockOptions = [
    {
      id: 'gpt-4',
      name: 'GPT-4',
      description: "OpenAI's most advanced model",
    },
    {
      id: 'claude-3',
      name: 'Claude 3',
      description: "Anthropic's latest model",
    },
  ];

  const mockOnSelectionChange = jest.fn();

  beforeEach(() => {
    mockOnSelectionChange.mockClear();
  });

  it('renders correctly', () => {
    render(
      <LLMSelector
        options={mockOptions}
        selectedModels={[]}
        onSelectionChange={mockOnSelectionChange}
      />
    );

    expect(screen.getByText('Select LLMs for Analysis')).toBeInTheDocument();
    expect(screen.getByText('GPT-4')).toBeInTheDocument();
    expect(screen.getByText('Claude 3')).toBeInTheDocument();
  });

  it('handles model selection', () => {
    render(
      <LLMSelector
        options={mockOptions}
        selectedModels={[]}
        onSelectionChange={mockOnSelectionChange}
      />
    );

    const checkbox = screen.getByLabelText('GPT-4');
    fireEvent.click(checkbox);

    expect(mockOnSelectionChange).toHaveBeenCalledWith(['gpt-4']);
  });

  it('handles model deselection', () => {
    render(
      <LLMSelector
        options={mockOptions}
        selectedModels={['gpt-4']}
        onSelectionChange={mockOnSelectionChange}
      />
    );

    const checkbox = screen.getByLabelText('GPT-4');
    fireEvent.click(checkbox);

    expect(mockOnSelectionChange).toHaveBeenCalledWith([]);
  });

  it('disables checkboxes when loading', () => {
    render(
      <LLMSelector
        options={mockOptions}
        selectedModels={[]}
        onSelectionChange={mockOnSelectionChange}
        disabled={true}
      />
    );

    const checkboxes = screen.getAllByRole('checkbox');
    checkboxes.forEach(checkbox => {
      expect(checkbox).toBeDisabled();
    });
  });

  it('shows selected models as checked', () => {
    render(
      <LLMSelector
        options={mockOptions}
        selectedModels={['gpt-4']}
        onSelectionChange={mockOnSelectionChange}
      />
    );

    const gpt4Checkbox = screen.getByLabelText('GPT-4');
    const claudeCheckbox = screen.getByLabelText('Claude 3');

    expect(gpt4Checkbox).toBeChecked();
    expect(claudeCheckbox).not.toBeChecked();
  });

  it('handles multiple model selection', () => {
    render(
      <LLMSelector
        options={mockOptions}
        selectedModels={['gpt-4']}
        onSelectionChange={mockOnSelectionChange}
      />
    );

    const claudeCheckbox = screen.getByLabelText('Claude 3');
    fireEvent.click(claudeCheckbox);

    expect(mockOnSelectionChange).toHaveBeenCalledWith(['gpt-4', 'claude-3']);
  });
});
