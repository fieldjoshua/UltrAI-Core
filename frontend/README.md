# Ultra Frontend

This directory contains the frontend code for the Ultra AI Framework.

## Directory Structure

- **components/**: React components
  - `ui/`: UI components and primitives
  - `AnimatedLogo.tsx`: Logo animations and branding elements
  - `DocumentUpload.tsx`: Document handling interface
  - `DocumentViewer.tsx`: Document viewing and rendering
  - `ErrorBoundary.tsx`: Error handling components
  - `PerformanceDashboard.tsx`: Performance monitoring visualizations
  - `PricingDisplay.tsx`: Token pricing and usage visualization

- **pages/**: Page definitions and layouts
  - `App.tsx`: Main application component
  - `main.jsx`: Application entry point

- **api/**: Frontend API clients
  - `config.js`: API configuration
  - `index.js`: API client implementations

- **styles/**: CSS and styling files
  - `index.css`: Global styles

- **public/**: Static assets and resources

## Build and Development

To run the frontend in development mode:

```bash
cd frontend
npm install
npm run dev
```

For production build:

```bash
npm run build
```

## Technologies

- React
- TypeScript
- CSS Modules
- Vite
