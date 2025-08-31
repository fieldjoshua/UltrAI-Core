import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { jest } from '@jest/globals';
import ErrorBoundary from '@/components/ErrorBoundary';

// Minimal connected component fallback by mocking connect to a passthrough
jest.mock('react-redux', () => ({ connect: () => (c: any) => c }));
jest.mock('@/features/errors/errorsSlice', () => ({ setGlobalError: () => ({ type: 'noop' }) }));
jest.mock('../../features/errors/errorsSlice', () => ({ setGlobalError: () => ({ type: 'noop' }) }));
jest.mock('@reduxjs/toolkit', () => ({ createSlice: (...args: any[]) => ({ actions: {}, reducer: () => ({}) }) }));

const Boom: React.FC = () => {
  throw new Error('boom');
};

describe('ErrorBoundary', () => {
  it('catches errors and shows fallback', () => {
    render(
      <ErrorBoundary>
        <Boom />
      </ErrorBoundary>
    );
    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
  });
});


