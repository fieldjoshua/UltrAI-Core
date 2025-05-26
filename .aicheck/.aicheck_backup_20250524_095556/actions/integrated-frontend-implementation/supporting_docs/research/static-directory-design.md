# Static Directory Structure Design

**Date**: 2025-05-22
**ACTION**: integrated-frontend-implementation

## Proposed Directory Structure

```
static/
├── index.html              # Main application entry point
├── login.html              # Authentication page
├── dashboard.html          # Main application interface
├── css/
│   ├── main.css           # Primary stylesheet
│   ├── auth.css           # Authentication-specific styles
│   ├── components.css     # Reusable component styles
│   └── themes.css         # Color themes and variables
├── js/
│   ├── app.js             # Main application logic
│   ├── auth.js            # Authentication handling
│   ├── api.js             # API interaction layer
│   ├── upload.js          # File upload functionality
│   ├── analysis.js        # Analysis workflow
│   └── utils.js           # Utility functions
├── assets/
│   ├── images/
│   │   ├── logo.svg       # Application logo
│   │   └── icons/         # Custom icons if needed
│   └── fonts/             # Custom fonts (if any)
└── components/
    ├── navigation.html    # Header/navigation partial
    ├── upload-form.html   # File upload component
    └── analysis-form.html # Analysis form component
```

## File Descriptions

### HTML Pages

#### `index.html`
- Landing page with auth check
- Redirects to login or dashboard
- Minimal loading state

#### `login.html`  
- Authentication forms (login/register)
- Form validation
- Error message display

#### `dashboard.html`
- Main application interface
- Document management
- Analysis interface
- Navigation header

### CSS Organization

#### `main.css`
- Reset/normalize styles
- Base typography and layout
- Grid and flexbox utilities
- Responsive breakpoints

#### `auth.css`
- Authentication form styling
- Login/register page layout
- Form validation states

#### `components.css`
- Button styles
- Form input styles
- Card components
- Modal/dialog styles

#### `themes.css`
- CSS custom properties for theming
- Dark/light mode variables
- Color palette definitions

### JavaScript Modules

#### `app.js`
- Main application initialization
- Page routing logic
- Global state management
- Event listeners setup

#### `auth.js`
- JWT token management
- Login/logout functionality
- Authentication state
- Protected route handling

#### `api.js`
- HTTP request abstraction
- Error handling
- Retry logic
- Response formatting

#### `upload.js`
- File upload handling
- Drag-and-drop functionality
- Progress tracking
- File validation

#### `analysis.js`
- Analysis form handling
- Results display
- Progress monitoring
- Export functionality

## Design Principles

### 1. Modular Architecture
- Separate concerns by functionality
- Reusable components
- Clear file organization

### 2. Progressive Enhancement
- Works without JavaScript (basic forms)
- Enhanced with JavaScript interactions
- Graceful degradation

### 3. Performance Optimization
- Minimal HTTP requests
- CSS/JS concatenation strategy
- Lazy loading for large components

### 4. Maintainability
- Clear naming conventions
- Consistent code structure
- Documentation within code

## Integration with FastAPI

### Static File Serving
```python
# In app_production.py
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

### Route Priority
1. API routes defined first (`/auth/*`, `/documents/*`, etc.)
2. Static files serve as fallback
3. `html=True` enables SPA routing

### Development vs Production
- Development: Direct file serving
- Production: Same approach, cached by Render
- No build step required (vanilla HTML/CSS/JS)