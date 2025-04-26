import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import DocumentStep from '../components/steps/DocumentStep';

describe('DocumentStep', () => {
  const mockProps = {
    isUsingDocuments: false,
    uploadedDocuments: [],
    onToggleDocumentMode: jest.fn(),
    onFileUpload: jest.fn(),
    onFileRemove: jest.fn(),
  };

  it('renders without crashing', () => {
    render(<DocumentStep {...mockProps} />);
    expect(
      screen.getByText('Include documents in your analysis')
    ).toBeInTheDocument();
  });

  it('handles document mode toggle', () => {
    render(<DocumentStep {...mockProps} />);
    const checkbox = screen.getByRole('checkbox', {
      name: /include documents/i,
    });
    fireEvent.click(checkbox);
    expect(mockProps.onToggleDocumentMode).toHaveBeenCalledWith(true);
  });

  it('displays uploaded documents', () => {
    const props = {
      ...mockProps,
      isUsingDocuments: true,
      uploadedDocuments: [{ id: '1', name: 'test.pdf', size: 1024 }],
    };
    render(<DocumentStep {...props} />);
    expect(screen.getByText('test.pdf')).toBeInTheDocument();
  });

  it('handles file removal', () => {
    const props = {
      ...mockProps,
      isUsingDocuments: true,
      uploadedDocuments: [{ id: '1', name: 'test.pdf', size: 1024 }],
    };
    render(<DocumentStep {...props} />);
    const removeButton = screen.getByLabelText('Remove test.pdf');
    fireEvent.click(removeButton);
    expect(mockProps.onFileRemove).toHaveBeenCalledWith('1');
  });
});
