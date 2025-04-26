import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ModelSelectionStep from '../components/steps/ModelSelectionStep';

describe('ModelSelectionStep', () => {
  const mockProps = {
    availableModels: ['gpt4', 'claude3', 'llama2'],
    selectedLLMs: [],
    ultraLLM: null,
    prices: {
      gpt4: 0.03,
      claude3: 0.02,
      llama2: 0.01,
    },
    isProcessing: false,
    isOffline: false,
    onLLMChange: jest.fn(),
    onUltraChange: jest.fn(),
  };

  it('renders without crashing', () => {
    render(<ModelSelectionStep {...mockProps} />);
    expect(screen.getByText('Select AI models')).toBeInTheDocument();
  });

  it('displays all available models', () => {
    render(<ModelSelectionStep {...mockProps} />);
    mockProps.availableModels.forEach((model) => {
      expect(
        screen.getByText(model.charAt(0).toUpperCase() + model.slice(1))
      ).toBeInTheDocument();
    });
  });

  it('handles model selection', () => {
    render(<ModelSelectionStep {...mockProps} />);
    const firstModel = screen.getByText('Gpt4');
    fireEvent.click(firstModel);
    expect(mockProps.onLLMChange).toHaveBeenCalledWith('gpt4');
  });

  it('handles ultra model selection', () => {
    const props = {
      ...mockProps,
      selectedLLMs: ['gpt4'],
    };
    render(<ModelSelectionStep {...props} />);
    const ultraButton = screen.getByLabelText('Set gpt4 as Ultra Model');
    fireEvent.click(ultraButton);
    expect(mockProps.onUltraChange).toHaveBeenCalled();
  });

  it('displays prices correctly', () => {
    render(<ModelSelectionStep {...mockProps} />);
    expect(screen.getByText('$0.0300 / 1K tokens')).toBeInTheDocument();
  });
});
