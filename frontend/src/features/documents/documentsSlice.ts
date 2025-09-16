import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import apiClient from '../../services/api'; // Import the configured axios instance
import { endpoints } from '../../services/api'; // Import endpoints definition

// Define types
export interface Document {
  id: string;
  name: string;
  size: number;
  type: string;
  status: string;
  uploadDate: string;
}

interface DocumentsState {
  documents: Document[];
  selectedDocuments: string[];
  isLoading: boolean;
  error: string | null;
  uploadProgress: number;
}

// Initial state
const initialState: DocumentsState = {
  documents: [],
  selectedDocuments: [],
  isLoading: false,
  error: null,
  uploadProgress: 0,
};

// Async thunks
export const fetchDocuments = createAsyncThunk<
  Document[], // Return type when fulfilled
  void, // Argument type (none in this case)
  { rejectValue: string } // Type for rejection payload
>('documents/fetchDocuments', async (_, { rejectWithValue }) => {
  try {
    // Debug message to show exact endpoint
    console.log('Fetching documents from:', endpoints.documents.getAll);
    console.log('API client base URL:', apiClient.defaults.baseURL);

    // Use the configured API client instead of hardcoded localhost
    const response = await apiClient.get<Document[] | { error: string }>(
      endpoints.documents.getAll
    );

    // Check if response contains an error
    if (
      response.data &&
      typeof response.data === 'object' &&
      'error' in response.data
    ) {
      throw new Error(
        response.data.error || 'Documents endpoint not available'
      );
    }

    // Ensure response.data is an array
    if (!Array.isArray(response.data)) {
      console.warn(
        'Documents endpoint returned non-array data:',
        response.data
      );
      return []; // Return empty array as fallback
    }

    return response.data; // Return the fetched documents
  } catch (error: any) {
    console.error('Failed to fetch documents:', error);
    const message =
      error.response?.data?.message ||
      error.message ||
      'Failed to fetch documents';
    return rejectWithValue(message);
  }
});

export const uploadDocument = createAsyncThunk(
  'documents/uploadDocument',
  async (file: File, { rejectWithValue }) => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      // Use the configured API client instead of hardcoded localhost
      const response = await apiClient.post(
        endpoints.documents.upload,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: progressEvent => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / (progressEvent.total || 100)
            );
            // You could dispatch an action here to update upload progress if needed
          },
        }
      );

      return response.data;
    } catch (error: any) {
      console.error('Failed to upload document:', error);
      const message =
        error.response?.data?.message ||
        error.message ||
        'Failed to upload document';
      return rejectWithValue(message);
    }
  }
);

export const deleteDocument = createAsyncThunk(
  'documents/deleteDocument',
  async (documentId: string, { rejectWithValue }) => {
    try {
      // Use the configured API client instead of hardcoded localhost
      await apiClient.delete(endpoints.documents.delete(documentId));
      return documentId;
    } catch (error: any) {
      console.error('Failed to delete document:', error);
      const message =
        error.response?.data?.message ||
        error.message ||
        'Failed to delete document';
      return rejectWithValue(message);
    }
  }
);

// Create the slice
const documentsSlice = createSlice({
  name: 'documents',
  initialState,
  reducers: {
    setSelectedDocuments: (state, action: PayloadAction<string[]>) => {
      state.selectedDocuments = action.payload;
    },
    toggleDocumentSelection: (state, action: PayloadAction<string>) => {
      const documentId = action.payload;
      if (state.selectedDocuments.includes(documentId)) {
        state.selectedDocuments = state.selectedDocuments.filter(
          id => id !== documentId
        );
      } else {
        state.selectedDocuments.push(documentId);
      }
    },
    setUploadProgress: (state, action: PayloadAction<number>) => {
      state.uploadProgress = action.payload;
    },
    clearError: state => {
      state.error = null;
    },
    addDocument: (state, action) => {
      state.documents.push(action.payload);
    },
    removeDocument: (state, action) => {
      state.documents = state.documents.filter(
        doc => doc.id !== action.payload
      );
    },
    clearDocuments: state => {
      state.documents = [];
    },
  },
  extraReducers: builder => {
    builder
      // Fetch documents
      .addCase(fetchDocuments.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(
        fetchDocuments.fulfilled,
        (state, action: PayloadAction<Document[]>) => {
          state.documents = action.payload;
          state.isLoading = false;
        }
      )
      .addCase(fetchDocuments.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload ?? 'Failed to fetch documents'; // Use nullish coalescing
      })

      // Upload document
      .addCase(uploadDocument.pending, state => {
        state.isLoading = true;
        state.error = null;
        state.uploadProgress = 0;
      })
      .addCase(uploadDocument.fulfilled, (state, action) => {
        state.isLoading = false;
        state.documents.push(action.payload);
        state.uploadProgress = 100;
      })
      .addCase(uploadDocument.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
        state.uploadProgress = 0;
      })

      // Delete document
      .addCase(deleteDocument.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(deleteDocument.fulfilled, (state, action) => {
        state.isLoading = false;
        state.documents = state.documents.filter(
          doc => doc.id !== action.payload
        );
        state.selectedDocuments = state.selectedDocuments.filter(
          id => id !== action.payload
        );
      })
      .addCase(deleteDocument.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

// Export actions and reducer
export const {
  setSelectedDocuments,
  toggleDocumentSelection,
  setUploadProgress,
  clearError,
  addDocument,
  removeDocument,
  clearDocuments,
} = documentsSlice.actions;

export default documentsSlice.reducer;
