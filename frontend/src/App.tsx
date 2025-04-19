import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ErrorFallback from './components/ErrorFallback';
import DocumentsPage from './pages/DocumentsPage';
import SimpleAnalysis from './pages/SimpleAnalysis';
import NavBar from './components/layout/NavBar';

// Simple error boundary component since the imported one is causing TypeScript errors
class SimpleErrorBoundary extends React.Component<{ children: React.ReactNode }> {
    state = { hasError: false, error: null };

    static getDerivedStateFromError(error: any) {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.error("Uncaught error:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return <ErrorFallback error={this.state.error} resetErrorBoundary={() => this.setState({ hasError: false })} />;
        }

        return this.props.children;
    }
}

const App: React.FC = () => {
    return (
        <SimpleErrorBoundary>
            <Router>
                <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
                    <NavBar />
                    <main className="pt-6">
                        <Routes>
                            <Route path="/documents" element={<DocumentsPage />} />
                            <Route path="/analyze" element={<SimpleAnalysis />} />
                            <Route path="/" element={<Navigate to="/documents" replace />} />
                        </Routes>
                    </main>
                </div>
            </Router>
        </SimpleErrorBoundary>
    );
};

export default App;
