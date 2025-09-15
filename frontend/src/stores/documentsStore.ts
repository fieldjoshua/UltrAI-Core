import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import axios from 'axios';

// Types
export interface Document {
  id: string;
  filename: string;
  file_size: number;
  mime_type: string;
  uploaded_at: string;
  description?: string;
  tags?: string[];
}

interface DocumentsState {
  // State
  documents: Document[];
  selectedDocuments: string[];
  isLoading: boolean;
  error: string | null;
  uploadProgress: Record<string, number>;
  
  // Actions
  fetchDocuments: () => Promise<void>;
  uploadDocument: (file: File, description?: string, tags?: string[]) => Promise<void>;
  deleteDocument: (documentId: string) => Promise<void>;
  setSelectedDocuments: (documentIds: string[]) => void;
  toggleDocumentSelection: (documentId: string) => void;
  setUploadProgress: (fileId: string, progress: number) => void;
  clearError: () => void;
  addDocument: (document: Document) => void;
  removeDocument: (documentId: string) => void;
  clearDocuments: () => void;
}

// @ts-ignore
const API_URL = (globalThis.import?.meta?.env?.VITE_API_URL) || 'http://localhost:8000/api';

export const useDocumentsStore = create<DocumentsState>()(
  devtools(
    (set, get) => ({
      // Initial state
      documents: [],
      selectedDocuments: [],
      isLoading: false,
      error: null,
      uploadProgress: {},

      // Fetch documents from API
      fetchDocuments: async () => {
        set({ isLoading: true, error: null });
        try {
          const response = await axios.get(`${API_URL}/documents`);
          set({ 
            documents: response.data.documents || [], 
            isLoading: false 
          });
        } catch (error: any) {
          set({ 
            error: error.response?.data?.error || 'Failed to fetch documents',
            isLoading: false 
          });
        }
      },

      // Upload document
      uploadDocument: async (file: File, description?: string, tags?: string[]) => {
        const fileId = `${file.name}-${Date.now()}`;
        set({ error: null });

        const formData = new FormData();
        formData.append('file', file);
        if (description) formData.append('description', description);
        if (tags?.length) formData.append('tags', JSON.stringify(tags));

        try {
          // Set initial progress
          set((state) => ({
            uploadProgress: { ...state.uploadProgress, [fileId]: 0 }
          }));

          const response = await axios.post(`${API_URL}/documents/upload`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: (progressEvent) => {
              const progress = progressEvent.total
                ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
                : 0;
              get().setUploadProgress(fileId, progress);
            }
          });

          // Add the new document to the list
          get().addDocument(response.data);

          // Clear upload progress
          set((state) => {
            const { [fileId]: _, ...rest } = state.uploadProgress;
            return { uploadProgress: rest };
          });
        } catch (error: any) {
          set({ 
            error: error.response?.data?.error || 'Failed to upload document' 
          });
          // Clear upload progress on error
          set((state) => {
            const { [fileId]: _, ...rest } = state.uploadProgress;
            return { uploadProgress: rest };
          });
          throw error;
        }
      },

      // Delete document
      deleteDocument: async (documentId: string) => {
        set({ error: null });
        try {
          await axios.delete(`${API_URL}/documents/${documentId}`);
          get().removeDocument(documentId);
        } catch (error: any) {
          set({ 
            error: error.response?.data?.error || 'Failed to delete document' 
          });
          throw error;
        }
      },

      // Set selected documents
      setSelectedDocuments: (documentIds: string[]) => {
        set({ selectedDocuments: documentIds });
      },

      // Toggle document selection
      toggleDocumentSelection: (documentId: string) => {
        set((state) => ({
          selectedDocuments: state.selectedDocuments.includes(documentId)
            ? state.selectedDocuments.filter(id => id !== documentId)
            : [...state.selectedDocuments, documentId]
        }));
      },

      // Set upload progress
      setUploadProgress: (fileId: string, progress: number) => {
        set((state) => ({
          uploadProgress: { ...state.uploadProgress, [fileId]: progress }
        }));
      },

      // Clear error
      clearError: () => {
        set({ error: null });
      },

      // Add document
      addDocument: (document: Document) => {
        set((state) => ({
          documents: [...state.documents, document]
        }));
      },

      // Remove document
      removeDocument: (documentId: string) => {
        set((state) => ({
          documents: state.documents.filter(doc => doc.id !== documentId),
          selectedDocuments: state.selectedDocuments.filter(id => id !== documentId)
        }));
      },

      // Clear all documents
      clearDocuments: () => {
        set({ documents: [], selectedDocuments: [] });
      }
    }),
    {
      name: 'documents-store'
    }
  )
);