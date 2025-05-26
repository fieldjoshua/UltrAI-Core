# Frontend Code Cleanup Tasks

After re-enabling the frontend, these code changes may be needed to remove dependencies:

## 1. Framer Motion Removal

### Search for imports:
```typescript
// Remove these imports
import { motion, AnimatePresence } from 'framer-motion';
```

### Replace with CSS:
```typescript
// Before (Framer Motion)
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  exit={{ opacity: 0 }}
>

// After (CSS)
<div className="fade-in">
```

### Add CSS transitions:
```css
.fade-in {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

## 2. Sentry Removal

### Remove initialization:
```typescript
// Remove from main.tsx or App.tsx
import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: "...",
});
```

### Remove error boundaries:
```typescript
// Remove Sentry error boundary
<Sentry.ErrorBoundary>
  <App />
</Sentry.ErrorBoundary>

// Replace with basic error boundary if needed
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

## 3. React Hook Form Removal

### Replace with useState:
```typescript
// Before (react-hook-form)
const { register, handleSubmit } = useForm();

// After (useState)
const [formData, setFormData] = useState({
  email: '',
  password: ''
});

const handleSubmit = (e) => {
  e.preventDefault();
  // Handle form submission
};
```

## 4. Zod Removal

### Replace with basic validation:
```typescript
// Before (zod)
const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
});

// After (basic validation)
const validateForm = (data) => {
  const errors = {};
  if (!data.email.includes('@')) errors.email = 'Invalid email';
  if (data.password.length < 8) errors.password = 'Too short';
  return errors;
};
```

## 5. Chart.js Removal

Remove any chart components and imports:
```typescript
// Remove these
import { Chart, Line, Bar } from 'react-chartjs-2';
```

## 6. UI Library Consolidation

Keep only Tailwind CSS classes, remove:
- `@radix-ui` components
- `@shadcn/ui` components

Use Tailwind for all styling needs.

## Files to Check

Priority files that likely use these dependencies:
1. `src/main.tsx` or `src/index.tsx` - Sentry init
2. `src/components/*` - Framer motion animations
3. `src/pages/auth/*` - React hook form
4. `src/utils/validation.ts` - Zod schemas
5. `src/components/charts/*` - Chart.js usage

## Testing After Cleanup

1. Run TypeScript compiler: `npm run build`
2. Check for import errors
3. Test all major user flows
4. Verify animations still work (CSS)
5. Ensure forms still submit properly