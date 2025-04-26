import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  MemoryRouter,
} from 'react-router-dom';
import ErrorFallback from './components/ErrorFallback';
import DocumentsPage from './pages/DocumentsPage';
import SimpleAnalysis from './pages/SimpleAnalysis';
import NavBar from './components/layout/NavBar';

// Simple error boundary component
class SimpleErrorBoundary extends React.Component<{
  children: React.ReactNode;
}> {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error: any) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <ErrorFallback
          error={this.state.error}
          resetErrorBoundary={() => this.setState({ hasError: false })}
        />
      );
    }

    return this.props.children;
  }
}

interface AppProps {
  RouterComponent?: typeof Router | typeof MemoryRouter;
  initialEntries?: string[];
}

const App: React.FC<AppProps> = ({
  RouterComponent = Router,
  initialEntries,
}) => {
  const content = (
    <SimpleErrorBoundary>
      <NavBar />
      <main className="pt-6">
        <Routes>
          <Route path="/" element={<Navigate to="/documents" replace />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/analyze" element={<SimpleAnalysis />} />
        </Routes>
      </main>
    </SimpleErrorBoundary>
  );

  if (RouterComponent === MemoryRouter && initialEntries) {
    return (
      <MemoryRouter initialEntries={initialEntries}>{content}</MemoryRouter>
    );
  }

  return <RouterComponent>{content}</RouterComponent>;
};

export default App;
