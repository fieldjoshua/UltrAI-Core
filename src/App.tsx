import React, { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';

// Lazy load components for code splitting
const UltraWithDocuments = lazy(() => import('./components/UltraWithDocuments'));
const PerformanceDashboard = lazy(() => import('./components/PerformanceDashboard'));
const SharedAnalysis = lazy(() => import('./components/SharedAnalysis'));

// Loading component for lazy-loaded routes
const RouteLoading = () => (
  <div className="flex justify-center items-center h-screen">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
  </div>
);

function App() {
  return (
    <Router>
      <ErrorBoundary>
        <Suspense fallback={<RouteLoading />}>
          <Routes>
            <Route path="/" element={<UltraWithDocuments />} />
            <Route path="/dashboard" element={<PerformanceDashboard />} />
            <Route path="/shared/:shareId" element={<SharedAnalysis />} />
            <Route path="*" element={<UltraWithDocuments />} />
          </Routes>
        </Suspense>
      </ErrorBoundary>
    </Router>
  );
}

export default App;
