# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Frontend Development Commands

### Development
- `npm run dev` - Start Vite dev server (port 3009)
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally

### Testing
- `npm test` - Run Jest tests
- `npm run test:watch` - Run tests in watch mode
- `npm run test:coverage` - Generate test coverage report
- `npm test src/__tests__/components/specific.test.tsx` - Run a specific test file

### Code Quality
- `npm run lint` - Run ESLint (max warnings: 0)

## High-Level Frontend Architecture

### Core Stack
- **React 18.3** with TypeScript 5.2
- **Vite 6.3** for bundling and dev server
- **Tailwind CSS** with custom design tokens
- **Zustand** for global state management
- **Redux Toolkit** for complex state (documents, errors)
- **Lucide React** for all icons (no emojis in production)

### Application Structure

**Component Organization:**
- `src/components/ui/` - Base Radix UI components with Tailwind styling
- `src/components/atoms/` - Small, reusable components
- `src/components/auth/` - Authentication flows (login, JWT management)
- `src/components/steps/` - Wizard step components
- `src/components/wizard/` - Main wizard orchestration components
- `src/components/branding/` - Logo animations and brand elements
- `src/components/panels/` - Complex panel components

**Key Architectural Decisions:**
1. **Multi-step Wizard Pattern**: The main UX is a guided wizard (CyberWizard.tsx) that walks users through:
   - Goal selection
   - Query input
   - Model selection
   - Add-on features
   - Results display with iteration viewing

2. **Skin System**: 6 themes (night, morning, afternoon, sunset, minimalist, business)
   - Skins load CSS dynamically from `public/skins/`
   - Background images in `public/backgrounds/`
   - Design tokens for consistent spacing/colors

3. **State Management Layers**:
   - Zustand: Auth state, theme preferences
   - Redux: Document management, error handling
   - Local component state: UI interactions
   - URL state: Navigation via React Router

4. **API Integration**:
   - Axios client configured for `https://ultrai-core.onrender.com/api`
   - Mock orchestrator for demo mode
   - JWT token handling in auth store
   - Request/response interceptors for auth

### Critical Frontend Patterns

**Error Handling:**
- Error boundaries wrap major components
- Redux error slice for centralized error state
- Toast notifications for user feedback
- Fallback UI components for graceful degradation

**Performance Optimizations:**
- Route-based code splitting
- Lazy loading for heavy components
- Memoized selectors for Redux state
- Optimized re-renders with React.memo
- Background image compression (130-221KB JPEGs)

**Accessibility:**
- ARIA labels on interactive elements
- Keyboard navigation support
- Screen reader announcements
- Focus management in wizard flow
- Semantic HTML structure

**Component Communication:**
- Props for parent-child
- Zustand/Redux for cross-component
- Custom events for specific interactions
- URL params for shareable state

### Testing Strategy

**Test Organization:**
- Unit tests: `src/__tests__/`
- Component tests: `src/components/__tests__/`
- Service tests: `src/services/__tests__/`
- A11y tests: `src/tests/a11y/`

**Testing Patterns:**
- Jest + React Testing Library
- Mock API responses with MSW
- Component isolation with test utils
- Accessibility testing with jest-axe
- Snapshot tests for UI consistency

### Build Configuration

**Vite Config Highlights:**
- Port 3009 for dev server
- Production sourcemaps enabled (for React error debugging)
- Path aliases: @/, @components/, @api/, @internal/, @skins/
- SVG support via vite-plugin-svgr
- CSS modules with TypeScript support

**TypeScript Config:**
- Strict mode enabled
- Path aliases match Vite config
- JSX: react-jsx (no import React needed)
- Target: ES2020 for modern browsers

### Current Focus Areas

**Recent Changes:**
- Major restructuring with files moved to `legacy/` directory
- CyberWizard.tsx actively being modified
- Results display now supports viewing initial/meta/final iterations
- Transparent glass-morphism UI elements
- Smaller, receipt-style results panel

**Known Issues:**
- Left panel visibility during processing (being fixed)
- White-on-white text in textarea (resolved with native textarea)
- Scrolling issues in step 3 (resolved with tighter spacing)

### Deployment Notes
- Frontend is built and served by the FastAPI backend in production
- Static files served from `/` route
- API calls go to `/api/*` routes
- Render.com handles continuous deployment from GitHub
- Build artifacts in `dist/` are gitignored