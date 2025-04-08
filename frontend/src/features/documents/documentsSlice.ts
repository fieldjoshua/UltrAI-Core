import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

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
export const fetchDocuments = createAsyncThunk(
    'documents/fetchDocuments',
    async (_, { rejectWithValue }) => {
        try {
            // This will be replaced with actual API calls
            const response = await fetch('/api/documents');

            if (!response.ok) {
                throw new Error('Failed to fetch documents');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            return rejectWithValue(error instanceof Error ? error.message : 'An unknown error occurred');
        }
    }
);

export const uploadDocument = createAsyncThunk(
    'documents/uploadDocument',
    async (file: File, { rejectWithValue }) => {
        try {
            const formData = new FormData();
            formData.append('file', file);

            // This will be replaced with actual API calls
            const response = await fetch('/api/upload-document', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Failed to upload document');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            return rejectWithValue(error instanceof Error ? error.message : 'An unknown error occurred');
        }
    }
);

export const deleteDocument = createAsyncThunk(
    'documents/deleteDocument',
    async (documentId: string, { rejectWithValue }) => {
        try {
            // This will be replaced with actual API calls
            const response = await fetch(`/api/documents/${documentId}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                throw new Error('Failed to delete document');
            }

            return documentId;
        } catch (error) {
            return rejectWithValue(error instanceof Error ? error.message : 'An unknown error occurred');
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
                state.selectedDocuments = state.selectedDocuments.filter(id => id !== documentId);
            } else {
                state.selectedDocuments.push(documentId);
            }
        },
        setUploadProgress: (state, action: PayloadAction<number>) => {
            state.uploadProgress = action.payload;
        },
        clearError: (state) => {
            state.error = null;
        },
    },
    extraReducers: (builder) => {
        builder
            // Fetch documents
            .addCase(fetchDocuments.pending, (state) => {
                state.isLoading = true;
                state.error = null;
            })
            .addCase(fetchDocuments.fulfilled, (state, action) => {
                state.isLoading = false;
                state.documents = action.payload;
            })
            .addCase(fetchDocuments.rejected, (state, action) => {
                state.isLoading = false;
                state.error = action.payload as string;
            })

            // Upload document
            .addCase(uploadDocument.pending, (state) => {
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
            .addCase(deleteDocument.pending, (state) => {
                state.isLoading = true;
                state.error = null;
            })
            .addCase(deleteDocument.fulfilled, (state, action) => {
                state.isLoading = false;
                state.documents = state.documents.filter(doc => doc.id !== action.payload);
                state.selectedDocuments = state.selectedDocuments.filter(id => id !== action.payload);
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
    clearError
} = documentsSlice.actions;

export default documentsSlice.reducer;