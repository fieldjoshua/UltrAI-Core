import { configureStore } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';
import { combineReducers } from 'redux';
import documentsReducer from '../features/documents/documentsSlice';
import errorsReducer from '../features/errors/errorsSlice';

// Import reducers as they are created
// import authReducer from '../features/auth/authSlice';
// import analysisReducer from '../features/analysis/analysisSlice';
// import uiReducer from '../features/ui/uiSlice';

// Combine reducers
const rootReducer = combineReducers({
  // auth: authReducer,
  documents: documentsReducer,
  errors: errorsReducer,
  // analysis: analysisReducer,
  // ui: uiReducer,
});

// Create and configure the store
export const store = configureStore({
  reducer: rootReducer,
  middleware: getDefaultMiddleware =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types
        ignoredActions: ['persist/PERSIST'],
        // Ignore these field paths in all actions
        ignoredActionPaths: ['meta.arg', 'payload.timestamp'],
        // Ignore these paths in the state
        ignoredPaths: [],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

// Enable listener behavior for the store
setupListeners(store.dispatch);

// Export types
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
