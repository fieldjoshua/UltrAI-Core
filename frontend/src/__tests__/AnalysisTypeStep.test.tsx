import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import AnalysisTypeStep from '../components/steps/AnalysisTypeStep';
import { Search } from 'lucide-react';

describe('AnalysisTypeStep', () => {
  const mockProps = {
    analysisTypes: [
      {
        id: 'comprehensive',
        name: 'Comprehensive Analysis',
        description: 'Detailed analysis of the topic',
        icon: Search,
      },
      {
        id: 'concise',
        name: 'Concise Analysis',
        description: 'Brief overview of key points',
        icon: Search,
      },
    ],
    selectedAnalysisType: '',
    onAnalysisTypeChange: jest.fn(),
  };

  it('renders without crashing', () => {
    render(<AnalysisTypeStep {...mockProps} />);
    expect(screen.getByText('Select Analysis Method')).toBeInTheDocument();
  });

  it('displays all analysis types', () => {
    render(<AnalysisTypeStep {...mockProps} />);
    mockProps.analysisTypes.forEach((type) => {
      expect(screen.getByText(type.name)).toBeInTheDocument();
      expect(screen.getByText(type.description)).toBeInTheDocument();
    });
  });

  it('handles analysis type selection', () => {
    render(<AnalysisTypeStep {...mockProps} />);
    const firstType = screen.getByText('Comprehensive Analysis');
    fireEvent.click(firstType);
    expect(mockProps.onAnalysisTypeChange).toHaveBeenCalledWith(
      'comprehensive'
    );
  });

  it('shows selected state correctly', () => {
    render(
      <AnalysisTypeStep {...mockProps} selectedAnalysisType="comprehensive" />
    );
    const selectedType = screen
      .getByText('Comprehensive Analysis')
      .closest('div[class*="border"]');
    expect(selectedType).toHaveClass('border-purple-500');
  });
});
