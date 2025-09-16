import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { jest } from '@jest/globals';
import { ModelSelector, type Model } from '@/components/atoms/ModelSelector';

const models: Model[] = [
  { id: 'gpt-4o', name: 'GPT-4o', provider: 'openai', isAvailable: true },
  {
    id: 'claude-3',
    name: 'Claude 3',
    provider: 'anthropic',
    isAvailable: true,
  },
  { id: 'gemini', name: 'Gemini', provider: 'google', isAvailable: false },
];

describe('ModelSelector', () => {
  it('renders groups and toggles selection', () => {
    const onChange = jest.fn();
    render(
      <ModelSelector
        availableModels={models}
        selectedModels={[]}
        onSelectionChange={onChange}
        isLoading={false}
      />
    );

    expect(screen.getByText(/Select AI Models/i)).toBeInTheDocument();
    // Click on GPT-4o row (available)
    fireEvent.click(screen.getByText('GPT-4o'));
    expect(onChange).toHaveBeenCalledWith(['gpt-4o']);
  });
});
