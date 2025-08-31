import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { jest } from '@jest/globals';
import { Navigation } from '@/components/Navigation';

describe('Navigation', () => {
  it('handles click selection', () => {
    const items = [
      { id: 'home', label: 'Home', href: '/' },
      { id: 'wizard', label: 'Wizard', href: '/wizard' },
    ];
    const onItemSelect = jest.fn();
    render(<Navigation items={items as any} onItemSelect={onItemSelect} />);
    fireEvent.click(screen.getByRole('menuitem', { name: 'Wizard' }));
    expect(onItemSelect).toHaveBeenCalledWith(expect.objectContaining({ id: 'wizard' }));
  });
})
