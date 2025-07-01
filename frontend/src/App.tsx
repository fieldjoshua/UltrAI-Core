import React, { Suspense, lazy } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import ErrorFallback from './components/ErrorFallback';

// Lazy load components for code splitting
const MultimodalAnalysis = lazy(() => import('./components/MultimodalAnalysis'));

// Archive unused components as lazy imports for potential future use
const DocumentsPage = lazy(() => import('./pages/DocumentsPage'));
const SimpleAnalysis = lazy(() => import('./pages/SimpleAnalysis'));
const ModelRunnerDemo = lazy(() => import('./pages/ModelRunnerDemo'));
const OrchestratorPage = lazy(() => import('./pages/OrchestratorPage'));

// Components marked for archival (multiple UIs - keep only one active)
const UIPrototype = lazy(() => import('./pages/UIPrototype'));
const UniversalUI = lazy(() => import('./pages/UniversalUI'));
const CyberpunkDemo = lazy(() => import('./pages/CyberpunkDemo'));
const CyberpunkTest = lazy(() => import('./pages/CyberpunkTest'));
const CyberpunkIntegration = lazy(() => import('./components/CyberpunkIntegration'));
const CyberpunkDebug = lazy(() => import('./components/CyberpunkDebug'));

// Loading component
const LoadingSpinner = () => (
  <div className="min-h-screen flex items-center justify-center bg-background">
    <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
  </div>
);

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
        <div className="min-h-screen bg-background text-foreground site-background">
          {/* NavBar removed for immersive skyline header */}
          <main className="pt-6">
            <Suspense fallback={<LoadingSpinner />}>
              <Routes>
                {/* Primary route - main interface */}
                <Route path="/multimodal" element={<MultimodalAnalysis />} />
                <Route path="/" element={<Navigate to="/multimodal" replace />} />
                
                {/* Archive routes - available but not actively used */}
                <Route path="/documents" element={<DocumentsPage />} />
                <Route path="/analyze" element={<SimpleAnalysis />} />
                <Route path="/modelrunner" element={<ModelRunnerDemo />} />
                <Route path="/orchestrator" element={<OrchestratorPage />} />
                
                {/* Deprecated UI variants - marked for cleanup */}
                <Route path="/prototype" element={<UIPrototype />} />
                <Route path="/universal-ui" element={<UniversalUI />} />
                <Route path="/cyberpunk" element={<CyberpunkDemo />} />
                <Route path="/cyberpunk-test" element={<CyberpunkTest />} />
                <Route path="/cyberpunk-integration" element={<CyberpunkIntegration />} />
                <Route path="/cyberpunk-debug" element={<CyberpunkDebug />} />
              </Routes>
            </Suspense>
          </main>
        </div>
      </Router>
    </SimpleErrorBoundary>
  );
};

export default App;
