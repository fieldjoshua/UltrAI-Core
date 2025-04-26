import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';
import { DocumentsPage } from '../pages/DocumentsPage';

// Mock the components
jest.mock('../components/layout/NavBar', () => {
  return function MockNavBar() {
    return <nav data-testid="navbar">Navigation Bar</nav>;
  };
});

jest.mock('../pages/DocumentsPage', () => ({
  DocumentsPage: jest.fn(() => (
    <div data-testid="documents-page">Documents Page</div>
  )),
}));

const renderWithRouter = (ui: React.ReactElement, { route = '/' } = {}) => {
  return render(
    <MemoryRouter
      initialEntries={[route]}
      future={{ v7_startTransition: true }}
    >
      {ui}
    </MemoryRouter>
  );
};

describe('App', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('renders navigation and main content', () => {
    renderWithRouter(<App />);
    expect(screen.getByTestId('navbar')).toBeInTheDocument();
    expect(screen.getByRole('main')).toBeInTheDocument();
  });

  it('redirects to documents page from root', () => {
    renderWithRouter(<App />);
    expect(screen.getByTestId('documents-page')).toBeInTheDocument();
  });

  it('handles errors with error boundary', () => {
    const ErrorComponent = () => {
      throw new Error('Test error');
      return null;
    };

    // Temporarily replace DocumentsPage with error-throwing component
    (DocumentsPage as jest.Mock).mockImplementationOnce(ErrorComponent);

    renderWithRouter(<App />);
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });
});
