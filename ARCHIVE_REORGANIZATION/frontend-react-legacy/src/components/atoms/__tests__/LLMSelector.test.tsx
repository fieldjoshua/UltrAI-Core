import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { LLMSelector } from '../LLMSelector';

const mockModels = [
  {
    id: 'gpt4',
    name: 'GPT-4',
    description: 'Most capable model',
    cost: 0.03,
    status: 'available' as const,
  },
  {
    id: 'claude',
    name: 'Claude',
    description: 'Good at analysis',
    cost: 0.02,
    status: 'available' as const,
  },
  {
    id: 'unavailable',
    name: 'Unavailable Model',
    status: 'unavailable' as const,
  },
];

describe('LLMSelector', () => {
  const mockOnModelChange = jest.fn();
  const mockOnUltraChange = jest.fn();

  beforeEach(() => {
    mockOnModelChange.mockClear();
    mockOnUltraChange.mockClear();
  });

  it('renders all available models', () => {
    render(
      <LLMSelector
        models={mockModels}
        selectedModels={[]}
        ultraModel={null}
        onModelChange={mockOnModelChange}
        onUltraChange={mockOnUltraChange}
      />
    );

    expect(screen.getByText('GPT-4')).toBeInTheDocument();
    expect(screen.getByText('Claude')).toBeInTheDocument();
    expect(screen.getByText('Unavailable Model')).toBeInTheDocument();
  });

  it('shows model descriptions and costs when available', () => {
    render(
      <LLMSelector
        models={mockModels}
        selectedModels={[]}
        ultraModel={null}
        onModelChange={mockOnModelChange}
        onUltraChange={mockOnUltraChange}
      />
    );

    expect(screen.getByText('Most capable model')).toBeInTheDocument();
    expect(screen.getByText('Good at analysis')).toBeInTheDocument();
    expect(screen.getByText('$0.0300 / 1K tokens')).toBeInTheDocument();
    expect(screen.getByText('$0.0200 / 1K tokens')).toBeInTheDocument();
  });

  it('calls onModelChange when a model is clicked', () => {
    render(
      <LLMSelector
        models={mockModels}
        selectedModels={[]}
        ultraModel={null}
        onModelChange={mockOnModelChange}
        onUltraChange={mockOnUltraChange}
      />
    );

    fireEvent.click(screen.getByText('GPT-4'));
    expect(mockOnModelChange).toHaveBeenCalledWith('gpt4');
  });

  it('disables unavailable models', () => {
    render(
      <LLMSelector
        models={mockModels}
        selectedModels={[]}
        ultraModel={null}
        onModelChange={mockOnModelChange}
        onUltraChange={mockOnUltraChange}
      />
    );

    const unavailableModel = screen
      .getByText('Unavailable Model')
      .closest('div');
    expect(unavailableModel).toHaveClass('opacity-50', 'cursor-not-allowed');
  });

  it('shows Ultra button for selected models', () => {
    render(
      <LLMSelector
        models={mockModels}
        selectedModels={['gpt4']}
        ultraModel={null}
        onModelChange={mockOnModelChange}
        onUltraChange={mockOnUltraChange}
      />
    );

    expect(screen.getByText('Set as Ultra')).toBeInTheDocument();
  });

  it('shows Ultra status for the selected Ultra model', () => {
    render(
      <LLMSelector
        models={mockModels}
        selectedModels={['gpt4']}
        ultraModel="gpt4"
        onModelChange={mockOnModelChange}
        onUltraChange={mockOnUltraChange}
      />
    );

    expect(screen.getByText('Ultra Model')).toBeInTheDocument();
  });

  it('calls onUltraChange when Ultra button is clicked', () => {
    render(
      <LLMSelector
        models={mockModels}
        selectedModels={['gpt4']}
        ultraModel={null}
        onModelChange={mockOnModelChange}
        onUltraChange={mockOnUltraChange}
      />
    );

    fireEvent.click(screen.getByText('Set as Ultra'));
    expect(mockOnUltraChange).toHaveBeenCalledWith('gpt4');
  });

  it('disables all interactions when disabled prop is true', () => {
    render(
      <LLMSelector
        models={mockModels}
        selectedModels={[]}
        ultraModel={null}
        disabled={true}
        onModelChange={mockOnModelChange}
        onUltraChange={mockOnUltraChange}
      />
    );

    const checkboxes = screen.getAllByRole('checkbox');
    checkboxes.forEach(checkbox => {
      expect(checkbox).toBeDisabled();
    });
  });

  it('shows loading state when isLoading is true', () => {
    render(
      <LLMSelector
        models={mockModels}
        selectedModels={[]}
        ultraModel={null}
        isLoading={true}
        onModelChange={mockOnModelChange}
        onUltraChange={mockOnUltraChange}
      />
    );

    const checkboxes = screen.getAllByRole('checkbox');
    checkboxes.forEach(checkbox => {
      expect(checkbox).toBeDisabled();
    });
  });
});
