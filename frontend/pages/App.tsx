import React from 'react';
import UltraWithDocuments from './components/UltraWithDocuments';
import ErrorBoundary from './components/ErrorBoundary';

export default function App() {
  return (
    <ErrorBoundary>
      <div className="app-container">
        <UltraWithDocuments />
      </div>
    </ErrorBoundary>
  );
}
