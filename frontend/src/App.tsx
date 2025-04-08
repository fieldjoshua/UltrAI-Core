import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';
import ErrorFallback from './components/ErrorFallback';
import DocumentsPage from './pages/DocumentsPage';
import UltraWithDocuments from './components/UltraWithDocuments';

const App: React.FC = () => {
    return (
        <ErrorBoundary FallbackComponent={ErrorFallback}>
            <Router>
                <Routes>
                    <Route path="/documents" element={<DocumentsPage />} />
                    <Route path="/analyze" element={<UltraWithDocuments />} />
                    <Route path="/" element={<Navigate to="/documents" replace />} />
                </Routes>
            </Router>
        </ErrorBoundary>
    );
};

export default App;