import React, { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../../../hooks/redux';
import {
  fetchDocuments,
  deleteDocument,
  toggleDocumentSelection,
} from '../documentsSlice';

const DocumentList: React.FC = () => {
  const dispatch = useAppDispatch();
  const { documents, selectedDocuments, isLoading, error } = useAppSelector(
    state => state.documents
  );

  useEffect(() => {
    // Fetch documents when component mounts
    dispatch(fetchDocuments());
  }, [dispatch]);

  const handleDeleteDocument = (id: string) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      dispatch(deleteDocument(id));
    }
  };

  const handleToggleSelect = (id: string) => {
    dispatch(toggleDocumentSelection(id));
  };

  if (isLoading && documents.length === 0) {
    return <div className="flex justify-center p-8">Loading documents...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative my-4">
        Error: {error}
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
                    />
                    <div className="ml-4">
                      <div className="flex text-sm font-medium text-indigo-600 truncate">
                        {document.name}
                      </div>
                      <div className="mt-2 flex">
                        <div className="flex items-center text-sm text-gray-500">
                          <span>
                            {document.type} • {formatFileSize(document.size)}
                          </span>
                        </div>
                      </div>
                      <div className="flex mt-1">
                        <span
                          className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            document.status === 'uploaded'
                              ? 'bg-green-100 text-green-800'
                              : document.status === 'processing'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {document.status}
                        </span>
                        <span className="ml-2 text-xs text-gray-500">
                          Uploaded:{' '}
                          {new Date(document.uploadDate).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="ml-4 flex-shrink-0 flex">
                    <button
                      onClick={() => handleDeleteDocument(document.id)}
                      className="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
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
