import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

// Types
export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface Toast {
  id: string;
  message: string;
  type: ToastType;
  duration?: number;
}

interface UIState {
  // Global error state
  globalError: string | null;

  // Toast notifications
  toasts: Toast[];

  // Loading states
  pendingRequests: number;

  // Actions
  setGlobalError: (error: string | null) => void;
  showToast: (message: string, type?: ToastType, duration?: number) => void;
  removeToast: (id: string) => void;
  clearAllToasts: () => void;
  incrementPendingRequests: () => void;
  decrementPendingRequests: () => void;

  // Computed
  isLoading: () => boolean;
}

export const useUIStore = create<UIState>()(
  devtools(
    (set, get) => ({
      // Initial state
      globalError: null,
      toasts: [],
      pendingRequests: 0,

      // Set global error
      setGlobalError: (error: string | null) => {
        set({ globalError: error });
      },

      // Show toast notification
      showToast: (
        message: string,
        type: ToastType = 'info',
        duration: number = 5000
      ) => {
        const id = `${Date.now()}-${Math.random()}`;
        const toast: Toast = { id, message, type, duration };

        set(state => ({
          toasts: [...state.toasts, toast],
        }));

        // Auto-remove toast after duration
        if (duration > 0) {
          setTimeout(() => {
            get().removeToast(id);
          }, duration);
        }
      },

      // Remove specific toast
      removeToast: (id: string) => {
        set(state => ({
          toasts: state.toasts.filter(toast => toast.id !== id),
        }));
      },

      // Clear all toasts
      clearAllToasts: () => {
        set({ toasts: [] });
      },

      // Increment pending requests
      incrementPendingRequests: () => {
        set(state => ({
          pendingRequests: state.pendingRequests + 1,
        }));
      },

      // Decrement pending requests
      decrementPendingRequests: () => {
        set(state => ({
          pendingRequests: Math.max(0, state.pendingRequests - 1),
        }));
      },

      // Check if any requests are loading
      isLoading: () => {
        return get().pendingRequests > 0;
      },
    }),
    {
      name: 'ui-store',
    }
  )
);

// Helper functions for common toast patterns
export const showSuccessToast = (message: string) => {
  useUIStore.getState().showToast(message, 'success');
};

export const showErrorToast = (message: string) => {
  useUIStore.getState().showToast(message, 'error');
};

export const showWarningToast = (message: string) => {
  useUIStore.getState().showToast(message, 'warning');
};

export const showInfoToast = (message: string) => {
  useUIStore.getState().showToast(message, 'info');
};
