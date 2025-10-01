import React from 'react';
import { render, screen } from '../../../test/test-utils';
import Receipt from '../../../components/wizard/Receipt';

describe('Receipt', () => {
  it('renders items and total', () => {
    const items = [
      { label: 'Model usage', amount: 1.23 },
      { label: 'Tools', amount: 0.77 },
    ];
    render(<Receipt items={items} total={2.0} />);
    expect(screen.getByText('Receipt')).toBeInTheDocument();
    expect(screen.getByText('Model usage')).toBeInTheDocument();
    expect(screen.getByText('$1.23')).toBeInTheDocument();
    expect(screen.getByText('$0.77')).toBeInTheDocument();
    expect(screen.getByText('$2.00')).toBeInTheDocument();
  });
});


