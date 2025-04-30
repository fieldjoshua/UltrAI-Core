import React, { lazy, Suspense } from 'react'
import ReactDOM from 'react-dom/client'
import * as Sentry from "@sentry/react";
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import './index.css'
import ErrorBoundary from './components/ErrorBoundary'

// Initialize Sentry for performance monitoring and error tracking
Sentry.init({
  dsn: "https://8548991d103a44411e3e95f92f3dc2d1@o4509109008531456.ingest.us.sentry.io/4509109056045056",
  integrations: [Sentry.browserTracingIntegration()],

  // Set tracesSampleRate to 1.0 to capture 100% of transactions
  // We recommend adjusting this value in production
  tracesSampleRate: 1.0,

  // Set tracePropagationTargets to control which URLs distributed tracing is enabled for
  tracePropagationTargets: [
    "localhost",
    /^https:\/\/yourserver\.io\/api/,
    /^\/api\//
  ],
});

// Import the components
import UltraWithDocuments from './components/UltraWithDocuments.tsx';
import SharedAnalysis from './components/SharedAnalysis.tsx';
import ErrorBoundary from './components/ErrorBoundary.tsx';

// Create router with routes
const router = createBrowserRouter([
  {
    path: '/',
    element: <UltraWithDocuments />,
    errorElement: <ErrorBoundary />,
  },
  {
    path: '/share/:shareId',
    element: <SharedAnalysis />,
    errorElement: <ErrorBoundary />,
  }
]);

// Lazy-load components for better performance
const App = lazy(() => import('./App'))

// Loading fallback component
const LoadingFallback = () => (
  <div className="flex items-center justify-center min-h-screen bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">
    <div className="text-center">
      <div className="w-16 h-16 border-4 border-t-blue-500 border-r-transparent border-b-blue-500 border-l-transparent rounded-full animate-spin mx-auto"></div>
      <p className="mt-4 text-white text-xl font-semibold">Loading Ultra AI...</p>
    </div>
  </div>
);

// Simple, direct rendering without StrictMode
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <Suspense fallback={<LoadingFallback />}>
        <App />
      </Suspense>
    </ErrorBoundary>
  </React.StrictMode>
)