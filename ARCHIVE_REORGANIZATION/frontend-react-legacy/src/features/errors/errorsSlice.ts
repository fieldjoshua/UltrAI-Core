import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { v4 as uuidv4 } from 'uuid';

export type ToastType = 'error' | 'success' | 'info';

interface ToastState {
  id: string;
  message: string;
  type: ToastType;
}

interface ErrorsState {
  globalError: Error | null;
  toast: ToastState;
  pendingRequests: number;
}

const initialState: ErrorsState = {
  globalError: null,
  toast: {
    id: '',
    message: '',
    type: 'info',
  },
  pendingRequests: 0,
};

export const errorsSlice = createSlice({
  name: 'errors',
  initialState,
  reducers: {
    setGlobalError: (state, action: PayloadAction<Error | null>) => {
      state.globalError = action.payload;

      // If an error is set and it's not null, also show a toast
      if (action.payload) {
        state.toast = {
          id: uuidv4(),
          message: action.payload.message || 'An unexpected error occurred',
          type: 'error',
        };
      }
    },
    showToast: (
      state,
      action: PayloadAction<{ message: string; type?: ToastType }>
    ) => {
      state.toast = {
        id: uuidv4(),
        message: action.payload.message,
        type: action.payload.type || 'info',
      };
    },
    clearToast: state => {
      state.toast = initialState.toast;
    },
    incrementPendingRequests: state => {
      state.pendingRequests += 1;
    },
    decrementPendingRequests: state => {
      state.pendingRequests = Math.max(0, state.pendingRequests - 1);
    },
  },
});

export const {
  setGlobalError,
  showToast,
  clearToast,
  incrementPendingRequests,
  decrementPendingRequests,
} = errorsSlice.actions;

export default errorsSlice.reducer;
