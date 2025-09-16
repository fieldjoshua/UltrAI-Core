# State Management with Zustand

This directory contains all Zustand stores for the Ultra frontend application.

## Stores

### 🔐 authStore.ts

Manages user authentication state including login, logout, and session management.

**Key features:**

- JWT token management
- User profile state
- Authentication status
- Auto-refresh tokens

### 📄 documentsStore.ts

Handles document upload, listing, and management functionality.

**Key features:**

- Document CRUD operations
- Multi-select functionality
- Upload progress tracking
- Error handling

### 🎨 uiStore.ts

Controls UI state including toast notifications and global loading states.

**Key features:**

- Toast notification system (success, error, warning, info)
- Global error handling
- Pending request tracking
- Loading state management

## Usage Example

```typescript
import { useDocumentsStore } from '@/stores/documentsStore';
import { showSuccessToast } from '@/stores/uiStore';

function MyComponent() {
  const { documents, fetchDocuments, isLoading } = useDocumentsStore();

  const handleRefresh = async () => {
    await fetchDocuments();
    showSuccessToast('Documents refreshed!');
  };

  return (
    <div>
      {isLoading ? <Spinner /> : <DocumentList documents={documents} />}
    </div>
  );
}
```

## Benefits over Redux

1. **No Providers Required** - Stores work globally without wrapping components
2. **Less Boilerplate** - Direct state updates without actions/reducers
3. **Better DevX** - Simpler API with automatic TypeScript inference
4. **Smaller Bundle** - ~8KB vs ~40KB for Redux Toolkit
5. **Easy Testing** - Mock stores with `setState()` in tests

## Testing

```typescript
// Reset store state in tests
beforeEach(() => {
  useDocumentsStore.setState({
    documents: [],
    selectedDocuments: [],
    isLoading: false,
    error: null,
  });
});

// Test store actions
it('should add document', () => {
  const { result } = renderHook(() => useDocumentsStore());

  act(() => {
    result.current.addDocument(mockDocument);
  });

  expect(result.current.documents).toContain(mockDocument);
});
```

## Migration Status

✅ **Migrated from Redux:**

- Documents management (from `features/documents/documentsSlice`)
- UI/Error handling (from `features/errors/errorsSlice`)
- Toast notifications

✅ **Components Updated:**

- DocumentUpload
- DocumentList
- Toast
- DocumentsPage

⚠️ **Redux Dependencies to Remove:**

- `@reduxjs/toolkit`
- `react-redux`
- Old Redux store files in `src/store/`
- Old Redux slices in `src/features/`

## Best Practices

1. Keep stores focused on a single domain
2. Use TypeScript interfaces for all state
3. Implement error handling in async actions
4. Clear errors when appropriate
5. Use devtools middleware in development
6. Reset store state in tests
