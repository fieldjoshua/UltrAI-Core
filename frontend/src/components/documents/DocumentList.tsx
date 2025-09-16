import React, { useEffect } from 'react';
import { useDocumentsStore } from '../../stores/documentsStore';
import { showSuccessToast, showErrorToast } from '../../stores/uiStore';

const DocumentList: React.FC = () => {
  const {
    documents,
    selectedDocuments,
    isLoading,
    error,
    fetchDocuments,
    deleteDocument,
    toggleDocumentSelection,
    clearError,
  } = useDocumentsStore();

  useEffect(() => {
    // Fetch documents when component mounts
    fetchDocuments();
  }, [fetchDocuments]);

  const handleDeleteDocument = async (id: string, filename: string) => {
    if (window.confirm(`Are you sure you want to delete ${filename}?`)) {
      try {
        await deleteDocument(id);
        showSuccessToast(`Successfully deleted ${filename}`);
      } catch (error) {
        showErrorToast('Failed to delete document');
      }
    }
  };

  const handleToggleSelect = (id: string) => {
    toggleDocumentSelection(id);
  };

  if (isLoading && documents.length === 0) {
    return <div className="flex justify-center p-8">Loading documents...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative my-4">
        <span className="block sm:inline">{error}</span>
        <button
          className="absolute top-0 bottom-0 right-0 px-4 py-3"
          onClick={clearError}
        >
          <span className="text-xl">&times;</span>
        </button>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="text-center p-8 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-medium text-gray-500">No documents yet</h3>
        <p className="mt-2 text-sm text-gray-400">
          Upload documents to get started with analysis
        </p>
      </div>
    );
  }

  return (
    <div className="mt-4">
      <h2 className="text-xl font-semibold mb-4">Your Documents</h2>

      <div className="overflow-hidden bg-white shadow sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {documents.map(document => (
            <li key={document.id} className="relative">
              <div className="flex items-center px-4 py-4 sm:px-6 hover:bg-gray-50">
                <div className="min-w-0 flex-1 sm:flex sm:items-center sm:justify-between">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                      checked={selectedDocuments.includes(document.id)}
                      onChange={() => handleToggleSelect(document.id)}
                      aria-label={`Select ${document.filename}`}
                    />
                    <div className="ml-4">
                      <div className="flex text-sm font-medium text-indigo-600 truncate">
                        {document.filename}
                      </div>
                      <div className="mt-2 flex">
                        <div className="flex items-center text-sm text-gray-500">
                          <span>
                            {document.mime_type} •{' '}
                            {formatFileSize(document.file_size)}
                          </span>
                        </div>
                      </div>
                      <div className="flex mt-1 items-center">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                          uploaded
                        </span>
                        <span className="ml-2 text-xs text-gray-500">
                          Uploaded:{' '}
                          {new Date(document.uploaded_at).toLocaleDateString()}
                        </span>
                        {document.tags && document.tags.length > 0 && (
                          <div className="ml-2 flex gap-1">
                            {document.tags.map(tag => (
                              <span
                                key={tag}
                                className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      {document.description && (
                        <p className="mt-1 text-sm text-gray-600">
                          {document.description}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="ml-4 flex-shrink-0 flex">
                    <button
                      onClick={() =>
                        handleDeleteDocument(document.id, document.filename)
                      }
                      className="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                      aria-label={`Delete ${document.filename}`}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {selectedDocuments.length > 0 && (
        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-700">
            {selectedDocuments.length} document
            {selectedDocuments.length !== 1 ? 's' : ''} selected
          </p>
        </div>
      )}
    </div>
  );
};

// Helper function to format file size
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export default DocumentList;
