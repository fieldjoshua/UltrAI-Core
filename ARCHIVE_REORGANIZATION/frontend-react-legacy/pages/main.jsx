import React from 'react';
import ReactDOM from 'react-dom/client';
import * as Sentry from '@sentry/react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import App from './App.tsx';
import { SpeedInsights } from '@vercel/speed-insights/react';
import './index.css';

// Initialize Sentry for performance monitoring and error tracking
Sentry.init({
  dsn: 'https://8548991d103a44411e3e95f92f3dc2d1@o4509109008531456.ingest.us.sentry.io/4509109056045056',
  integrations: [Sentry.browserTracingIntegration()],

  // Set tracesSampleRate to 1.0 to capture 100% of transactions
  // We recommend adjusting this value in production
  tracesSampleRate: 1.0,

  // Set tracePropagationTargets to control which URLs distributed tracing is enabled for
  tracePropagationTargets: [
    'localhost',
    /^https:\/\/yourserver\.io\/api/,
    /^\/api\//,
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
  },
]);

// Simple, direct rendering without StrictMode
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
    <SpeedInsights />
  </React.StrictMode>
);
