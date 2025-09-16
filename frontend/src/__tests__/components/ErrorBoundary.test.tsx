import React from 'react';
import { render, screen } from '@testing-library/react';
import { jest } from '@jest/globals';
// Mock connect before importing component
jest.mock('react-redux', () => ({ connect: () => (c: any) => c }));
jest.mock('@/features/errors/errorsSlice', () => ({
  setGlobalError: () => ({ type: 'noop' }),
}));
jest.mock('@reduxjs/toolkit', () => ({
  createSlice: (...args: any[]) => ({ actions: {}, reducer: () => ({}) }),
}));
import { UnconnectedErrorBoundary as ErrorBoundary } from '@/components/ErrorBoundary';

const Boom: React.FC = () => {
  throw new Error('boom');
};

describe('ErrorBoundary', () => {
  it('catches errors and shows fallback', () => {
    const originalError = console.error;
    // Silence expected React error logs for boundary test
    // @ts-ignore
    console.error = jest.fn();
    const onSetGlobalError = jest.fn();
    render(
      <ErrorBoundary setGlobalError={onSetGlobalError as any}>
        <Boom />
      </ErrorBoundary>
    );
    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
    console.error = originalError;
  });
});
