import React from 'react';
import { render, screen } from '@testing-library/react';

describe('Smoke test', () => {
  it('renders trivial content without crashing', () => {
    render(<div data-testid="ok">ok</div>);
    expect(screen.getByTestId('ok')).toHaveTextContent('ok');
  });
});
