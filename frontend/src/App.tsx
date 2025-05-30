import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import ErrorFallback from './components/ErrorFallback';
import DocumentsPage from './pages/DocumentsPage';
import SimpleAnalysis from './pages/SimpleAnalysis';
import ModelRunnerDemo from './pages/ModelRunnerDemo';
import OrchestratorPage from './pages/OrchestratorPage';
import UIPrototype from './pages/UIPrototype';
import UniversalUI from './pages/UniversalUI';
import NavBar from './components/layout/NavBar';
import CyberpunkDemo from './components/CyberpunkDemo';
import CyberpunkIntegration from './components/CyberpunkIntegration';
import CyberpunkDebug from './components/CyberpunkDebug';

// Simple error boundary component since the imported one is causing TypeScript errors
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

const App: React.FC = () => {
  return (
    <SimpleErrorBoundary>
      <Router>
        <div className="min-h-screen bg-background text-foreground">
          <NavBar />
          <main className="pt-6">
            <Routes>
              <Route path="/documents" element={<DocumentsPage />} />
              <Route path="/analyze" element={<SimpleAnalysis />} />
              <Route path="/modelrunner" element={<ModelRunnerDemo />} />
              <Route path="/orchestrator" element={<OrchestratorPage />} />
              <Route path="/prototype" element={<UIPrototype />} />
              <Route path="/universal-ui" element={<UniversalUI />} />
              <Route path="/cyberpunk" element={<CyberpunkDemo />} />
              <Route path="/cyberpunk-integration" element={<CyberpunkIntegration />} />
              <Route path="/cyberpunk-debug" element={<CyberpunkDebug />} />
              <Route path="/" element={<Navigate to="/cyberpunk-debug" replace />} />
            </Routes>
          </main>
        </div>
      </Router>
    </SimpleErrorBoundary>
  );
};

export default App;
