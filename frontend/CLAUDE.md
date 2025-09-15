# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Frontend Development Commands

### Development
```bash
npm run dev          # Start Vite dev server (port 3009)
npm run build        # Build for production
npm run preview      # Preview production build locally
npm run storybook    # Start Storybook on port 6006
```

### Testing
```bash
npm test                                    # Run all Jest tests
npm run test:watch                          # Run tests in watch mode
npm run test:coverage                       # Generate test coverage report
npm test src/__tests__/components/Button    # Run a specific test file
npm test -- --testNamePattern="renders"     # Run tests matching pattern
```

### Code Quality
```bash
npm run lint                # Run ESLint (max warnings: 0)
npm run build-storybook     # Build Storybook for deployment
```

## High-Level Frontend Architecture

### Core Technology Stack
- **React 18.3** with TypeScript 5.2
- **Vite 6.3** for bundling and dev server
- **Tailwind CSS** with custom design tokens
- **Zustand** for global state management
- **Redux Toolkit** for complex state (documents, errors)
- **Radix UI** for accessible primitives
- **Lucide React** for icons (no emojis in production)
- **Storybook** for component documentation

### Multi-Step Wizard Architecture

The application's main interface is a sophisticated multi-step wizard (`src/components/wizard/CyberWizard.tsx`) that orchestrates the entire user experience:

1. **Step Management**: Steps are loaded from `public/wizard_steps.json` and managed through local state
2. **Data Flow**: User selections accumulate in a receipt-style summary with running cost calculations
3. **Model Selection**: Supports both automatic (Premium/Speed/Budget) and manual model selection
4. **Processing Pipeline**: Transitions from wizard → status updates → results display
5. **Demo Mode**: Detects `VITE_API_MODE=mock` and loads demo data from `public/demo/ultrai_demo.json`

### State Management Layers

The application uses multiple state management patterns for different concerns:

1. **Zustand** (`src/stores/`):
   - `authStore.ts`: JWT tokens, user authentication state
   - Theme preferences and UI settings
   - Cross-component communication

2. **Redux Toolkit** (`src/store/`):
   - `documentsSlice.ts`: Document upload/management
   - `errorsSlice.ts`: Centralized error handling
   - Complex state that requires time-travel debugging

3. **Local Component State**:
   - Wizard step progression
   - Form inputs and UI interactions
   - Animation states

4. **URL State** (React Router):
   - Navigation between pages
   - Shareable links with state

### Theme System Architecture

The application supports 6 distinct themes with a sophisticated loading mechanism:

1. **Theme Types**: `night`, `morning`, `afternoon`, `sunset`, `minimalist`, `business`
2. **Dynamic Loading**: Themes are loaded via `loadSkin()` in `src/skins/index.ts`
3. **CSS Organization**:
   - Base styles in `src/skins/[theme].css`
   - Background images in `public/backgrounds/`
   - Glassmorphism effects adjust based on theme brightness

4. **Design Tokens** (`src/design-tokens/tokens.ts`):
   ```typescript
   {
     spacing: { xs: '0.25rem', sm: '0.5rem', ... },
     typography: { fontSize: { xs: {...}, sm: {...} } },
     colors: { wcag compliant color system }
   }
   ```

### API Integration Architecture

1. **Base Configuration** (`src/api/config.ts`):
   - Production: `https://ultrai-core.onrender.com/api`
   - Development: Uses Vite proxy to backend
   - Demo mode: Returns mock data

2. **Service Layer** (`src/api/`):
   - `orchestrator.ts`: Main orchestration endpoints
   - `auth.ts`: Authentication flows
   - `models.ts`: Model availability and health

3. **Request Flow**:
   - Axios interceptors add JWT tokens
   - Error responses trigger Redux error actions
   - 401 responses clear auth and redirect to login

### Performance Architecture

1. **Code Splitting**:
   - Route-based splitting with React.lazy()
   - Heavy components lazy-loaded on demand
   - Storybook separate build

2. **Image Optimization**:
   - WebP/AVIF formats for backgrounds
   - Responsive image loading
   - Lazy loading with Intersection Observer

3. **Rendering Optimizations**:
   - React.memo for expensive components
   - useMemo/useCallback for derived state
   - Virtual scrolling for long lists

### Accessibility Architecture

1. **Component Patterns**:
   - All interactive elements have ARIA labels
   - Focus management in wizard flow
   - Keyboard navigation support throughout

2. **Utilities** (`src/utils/accessibility.ts`):
   - `a11yLabels`: Centralized label generation
   - `announce()`: Screen reader announcements
   - Focus trap utilities

3. **Testing**:
   - jest-axe for automated a11y testing
   - Manual testing with screen readers

### Build & Deployment Architecture

1. **Vite Configuration**:
   - Path aliases: `@/`, `@components/`, `@api/`, `@internal/`, `@skins/`
   - Environment variables: `VITE_API_URL`, `VITE_API_MODE`, `VITE_DEMO_MODE`
   - Production sourcemaps enabled for debugging

2. **Build Process**:
   ```bash
   npm run build
   # Outputs to dist/
   # Served by FastAPI backend in production
   ```

3. **Deployment**:
   - Frontend built as static files
   - Served by backend at root path
   - API calls proxied through `/api/*`
   - Render.com auto-deploys from GitHub

### Critical Implementation Patterns

1. **Error Boundaries**: Wrap all major components to prevent full app crashes
2. **Loading States**: Skeleton screens for better perceived performance
3. **Optimistic Updates**: Update UI before API confirms for snappy feel
4. **Request Deduplication**: Prevent duplicate API calls during rapid interactions
5. **Animation Control**: Respect `prefers-reduced-motion` with toggle override

### Testing Patterns

1. **Component Testing**:
   ```typescript
   // Use testing-library for behavior-driven tests
   render(<Component />, { wrapper: AllTheProviders });
   await userEvent.click(screen.getByRole('button'));
   expect(screen.getByText('Result')).toBeInTheDocument();
   ```

2. **Mock Strategies**:
   - MSW for API mocking
   - Custom test utilities in `src/test-utils/`
   - Mock Zustand/Redux stores

3. **Coverage Requirements**:
   - Components: 80% coverage
   - Utilities: 100% coverage
   - Focus on user interactions over implementation

### Current Development Context

**Active Work Areas**:
- Mobile responsiveness improvements
- WCAG AA compliance
- Performance optimizations (WebP/AVIF, lazy loading)
- Prefers-reduced-motion support
- Results iteration viewing (initial/meta/final)

**Technical Debt**:
- Some components in `legacy/` need migration
- Storybook stories incomplete for newer components
- Test coverage gaps in wizard flow