import { renderHook, act } from '@testing-library/react';
import { useDocumentsStore } from '../../stores/documentsStore';

describe('documentsStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useDocumentsStore.setState({
      documents: [],
      selectedDocuments: [],
      isLoading: false,
      error: null,
      uploadProgress: {},
    });
  });

  describe('document selection', () => {
    it('should toggle document selection', () => {
      const { result } = renderHook(() => useDocumentsStore());

      // Add a test document
      act(() => {
        result.current.addDocument({
          id: '1',
          filename: 'test.pdf',
          file_size: 1024,
          mime_type: 'application/pdf',
          uploaded_at: new Date().toISOString(),
        });
      });

      // Toggle selection
      act(() => {
        result.current.toggleDocumentSelection('1');
      });

      expect(result.current.selectedDocuments).toContain('1');

      // Toggle again to deselect
      act(() => {
        result.current.toggleDocumentSelection('1');
      });

      expect(result.current.selectedDocuments).not.toContain('1');
    });

    it('should set multiple selected documents', () => {
      const { result } = renderHook(() => useDocumentsStore());

      act(() => {
        result.current.setSelectedDocuments(['1', '2', '3']);
      });

      expect(result.current.selectedDocuments).toEqual(['1', '2', '3']);
    });
  });

  describe('document management', () => {
    it('should add a document', () => {
      const { result } = renderHook(() => useDocumentsStore());

      const newDoc = {
        id: '1',
        filename: 'test.pdf',
        file_size: 1024,
        mime_type: 'application/pdf',
        uploaded_at: new Date().toISOString(),
      };

      act(() => {
        result.current.addDocument(newDoc);
      });

      expect(result.current.documents).toHaveLength(1);
      expect(result.current.documents[0]).toEqual(newDoc);
    });

    it('should remove a document', () => {
      const { result } = renderHook(() => useDocumentsStore());

      // Add documents first
      act(() => {
        result.current.addDocument({
          id: '1',
          filename: 'test1.pdf',
          file_size: 1024,
          mime_type: 'application/pdf',
          uploaded_at: new Date().toISOString(),
        });
        result.current.addDocument({
          id: '2',
          filename: 'test2.pdf',
          file_size: 2048,
          mime_type: 'application/pdf',
          uploaded_at: new Date().toISOString(),
        });
      });

      // Remove one document
      act(() => {
        result.current.removeDocument('1');
      });

      expect(result.current.documents).toHaveLength(1);
      expect(result.current.documents[0].id).toBe('2');
    });

    it('should clear all documents', () => {
      const { result } = renderHook(() => useDocumentsStore());

      // Add some documents
      act(() => {
        result.current.addDocument({
          id: '1',
          filename: 'test.pdf',
          file_size: 1024,
          mime_type: 'application/pdf',
          uploaded_at: new Date().toISOString(),
        });
        result.current.setSelectedDocuments(['1']);
      });

      // Clear all
      act(() => {
        result.current.clearDocuments();
      });

      expect(result.current.documents).toHaveLength(0);
      expect(result.current.selectedDocuments).toHaveLength(0);
    });
  });

  describe('upload progress', () => {
    it('should track upload progress', () => {
      const { result } = renderHook(() => useDocumentsStore());

      act(() => {
        result.current.setUploadProgress('file1', 25);
      });

      expect(result.current.uploadProgress['file1']).toBe(25);

      act(() => {
        result.current.setUploadProgress('file1', 75);
      });

      expect(result.current.uploadProgress['file1']).toBe(75);
    });
  });

  describe('error handling', () => {
    it('should set and clear errors', () => {
      const { result } = renderHook(() => useDocumentsStore());

      // Set error through failed action simulation
      act(() => {
        useDocumentsStore.setState({ error: 'Test error' });
      });

      expect(result.current.error).toBe('Test error');

      // Clear error
      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });
});