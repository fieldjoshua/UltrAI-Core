# Redux to Zustand Migration Guide

## Overview
This guide documents the migration from Redux Toolkit to Zustand for state management in the Ultra frontend.

## Migration Status

### ✅ Completed Migrations

1. **Documents Store** (`documentsStore.ts`)
   - Migrated from `features/documents/documentsSlice.ts`
   - Components migrated:
     - `DocumentUpload.tsx` → `components/documents/DocumentUpload.tsx`
     - `DocumentList.tsx` → `components/documents/DocumentList.tsx`

2. **UI Store** (`uiStore.ts`)
   - Migrated from `features/errors/errorsSlice.ts`
   - Includes toast notifications and global error handling
   - Component migrated:
     - `Toast.tsx` → Updated to use Zustand

3. **Auth Store** (`authStore.ts`)
   - Already using Zustand (no migration needed)

### ⏳ Pending Migrations

1. **Remove Redux dependencies**
   - Remove `@reduxjs/toolkit` and `react-redux` from package.json
   - Delete `src/store/index.ts`
   - Delete `src/hooks/redux.ts`
   - Delete old Redux slices in `src/features/`

2. **Update main.jsx**
   - Remove Redux Provider wrapper
   - Keep only necessary providers

## Key Differences

### Redux Toolkit
```typescript
// Redux slice
const documentsSlice = createSlice({
  name: 'documents',
  initialState,
  reducers: {
    setDocuments: (state, action) => {
      state.documents = action.payload;
    }
  },
  extraReducers: (builder) => {
    builder.addCase(fetchDocuments.fulfilled, (state, action) => {
      state.documents = action.payload;
    });
  }
});

// Component usage
const dispatch = useAppDispatch();
const { documents } = useAppSelector(state => state.documents);
dispatch(fetchDocuments());
```

### Zustand
```typescript
// Zustand store
const useDocumentsStore = create((set) => ({
  documents: [],
  fetchDocuments: async () => {
    const response = await api.get('/documents');
    set({ documents: response.data });
  }
}));

// Component usage
const { documents, fetchDocuments } = useDocumentsStore();
fetchDocuments();
```

## Benefits of Migration

1. **Simpler API** - No need for actions, reducers, or dispatch
2. **Less Boilerplate** - Direct state updates without Redux patterns
3. **Better TypeScript** - Automatic type inference
4. **Smaller Bundle** - Zustand is ~8KB vs Redux Toolkit ~40KB
5. **No Provider Required** - Stores work without wrapping components

## Migration Checklist

- [x] Create Zustand stores for each Redux slice
- [x] Migrate DocumentUpload component
- [x] Migrate DocumentList component
- [x] Migrate Toast component
- [x] Update imports in migrated components
- [ ] Test all migrated functionality
- [ ] Remove Redux from main.jsx
- [ ] Delete old Redux files
- [ ] Update package.json dependencies
- [ ] Update any remaining components using Redux

## Component Import Updates

### Old imports (Redux)
```typescript
import { useAppDispatch, useAppSelector } from '../hooks/redux';
import { fetchDocuments } from '../features/documents/documentsSlice';
```

### New imports (Zustand)
```typescript
import { useDocumentsStore } from '../stores/documentsStore';
import { showSuccessToast, showErrorToast } from '../stores/uiStore';
```

## Testing Considerations

- Zustand stores can be easily tested without providers
- Mock stores using `useDocumentsStore.setState()` in tests
- No need for Redux mock store utilities

## Next Steps

1. Test the migrated components thoroughly
2. Update any components that import from the old Redux files
3. Remove Redux dependencies once all components are migrated
4. Update the main app entry point to remove Redux Provider