import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';

// Mock the components
jest.mock('./components/layout/NavBar', () => {
  return function MockNavBar() {
    return (
      <nav data-testid="navbar" className="bg-primary">
        Navigation Bar
      </nav>
    );
  };
});

// Create a mock for DocumentsPage that can be dynamically updated
const mockDocumentsPage = jest.fn(() => (
  <div data-testid="documents-page" className="page-content">
    Documents Page
  </div>
));

jest.mock('./pages/DocumentsPage', () => ({
  __esModule: true,
  default: () => mockDocumentsPage(),
}));

jest.mock('./pages/SimpleAnalysis', () => {
  return function MockSimpleAnalysis() {
    return (
      <div data-testid="analysis-page" className="page-content">
        Analysis Page
      </div>
    );
  };
});

// Helper function to render with router
const renderWithRouter = (initialRoute = '/') => {
  return render(
    <App RouterComponent={MemoryRouter} initialEntries={[initialRoute]} />
  );
};

describe('App', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    // Reset the DocumentsPage mock to its default implementation
    mockDocumentsPage.mockImplementation(() => (
      <div data-testid="documents-page" className="page-content">
        Documents Page
      </div>
    ));
  });

  it('renders without crashing', () => {
    renderWithRouter();
    expect(screen.getByTestId('navbar')).toBeInTheDocument();
  });

  it('renders main element with proper class', () => {
    renderWithRouter();
    const mainElement = screen.getByRole('main');
    expect(mainElement).toBeInTheDocument();
    expect(mainElement).toHaveClass('pt-6');
  });

  it('redirects root to documents page', () => {
    renderWithRouter('/');
    expect(screen.getByTestId('documents-page')).toBeInTheDocument();
  });

  it('renders documents page on /documents route', () => {
    renderWithRouter('/documents');
    const documentsPage = screen.getByTestId('documents-page');
    expect(documentsPage).toBeInTheDocument();
    expect(documentsPage).toHaveClass('page-content');
  });

  it('renders analysis page on /analyze route', () => {
    renderWithRouter('/analyze');
    const analysisPage = screen.getByTestId('analysis-page');
    expect(analysisPage).toBeInTheDocument();
    expect(analysisPage).toHaveClass('page-content');
  });
});

// Separate describe block for error boundary tests
describe('App Error Boundary', () => {
  const originalError = console.error;
  const originalConsoleLog = console.log;

  beforeEach(() => {
    console.error = jest.fn(); // Suppress console.error
    console.log = jest.fn(); // Suppress console.log
    // Make DocumentsPage throw an error
    mockDocumentsPage.mockImplementation(() => {
      throw new Error('Test error');
    });
  });

  afterEach(() => {
    console.error = originalError;
    console.log = originalConsoleLog;
    // Reset the DocumentsPage mock
    mockDocumentsPage.mockReset();
  });

  it('handles errors with ErrorBoundary', () => {
    renderWithRouter('/documents');
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('Test error')).toBeInTheDocument();
  });
});
