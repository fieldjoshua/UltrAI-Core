import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { AnalysisPatternSelector } from '../AnalysisPatternSelector';

describe('AnalysisPatternSelector', () => {
  const mockPatterns = [
    {
      id: 'basic',
      name: 'Basic Analysis',
      description: 'Standard analysis of the prompt',
    },
    {
      id: 'detailed',
      name: 'Detailed Analysis',
      description: 'In-depth analysis with additional insights',
    },
  ];

  const mockOnPatternChange = jest.fn();

  beforeEach(() => {
    mockOnPatternChange.mockClear();
  });

  it('renders correctly', () => {
    render(
      <AnalysisPatternSelector
        patterns={mockPatterns}
        selectedPattern="basic"
        onPatternChange={mockOnPatternChange}
      />
    );

    expect(screen.getByText('Select Analysis Pattern')).toBeInTheDocument();
    expect(screen.getByText('Basic Analysis')).toBeInTheDocument();
    expect(screen.getByText('Detailed Analysis')).toBeInTheDocument();
  });

  it('handles pattern selection', () => {
    render(
      <AnalysisPatternSelector
        patterns={mockPatterns}
        selectedPattern="basic"
        onPatternChange={mockOnPatternChange}
      />
    );

    const detailedRadio = screen.getByLabelText('Detailed Analysis');
    fireEvent.click(detailedRadio);

    expect(mockOnPatternChange).toHaveBeenCalledWith('detailed');
  });

  it('shows selected pattern as checked', () => {
    render(
      <AnalysisPatternSelector
        patterns={mockPatterns}
        selectedPattern="basic"
        onPatternChange={mockOnPatternChange}
      />
    );

    const basicRadio = screen.getByLabelText('Basic Analysis');
    const detailedRadio = screen.getByLabelText('Detailed Analysis');

    expect(basicRadio).toBeChecked();
    expect(detailedRadio).not.toBeChecked();
  });

  it('disables radio buttons when loading', () => {
    render(
      <AnalysisPatternSelector
        patterns={mockPatterns}
        selectedPattern="basic"
        onPatternChange={mockOnPatternChange}
        disabled={true}
      />
    );

    const radioButtons = screen.getAllByRole('radio');
    radioButtons.forEach(radio => {
      expect(radio).toBeDisabled();
    });
  });

  it('displays pattern descriptions', () => {
    render(
      <AnalysisPatternSelector
        patterns={mockPatterns}
        selectedPattern="basic"
        onPatternChange={mockOnPatternChange}
      />
    );

    expect(
      screen.getByText('Standard analysis of the prompt')
    ).toBeInTheDocument();
    expect(
      screen.getByText('In-depth analysis with additional insights')
    ).toBeInTheDocument();
  });

  it('maintains selection state after re-render', () => {
    const { rerender } = render(
      <AnalysisPatternSelector
        patterns={mockPatterns}
        selectedPattern="basic"
        onPatternChange={mockOnPatternChange}
      />
    );

    const basicRadio = screen.getByLabelText('Basic Analysis');
    expect(basicRadio).toBeChecked();

    rerender(
      <AnalysisPatternSelector
        patterns={mockPatterns}
        selectedPattern="basic"
        onPatternChange={mockOnPatternChange}
      />
    );

    expect(basicRadio).toBeChecked();
  });
});
