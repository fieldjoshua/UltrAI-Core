import React, { useState, useRef, ChangeEvent } from 'react';
import { useDocumentsStore } from '../../stores/documentsStore';
import { showSuccessToast, showErrorToast } from '../../stores/uiStore';

const DocumentUpload: React.FC = () => {
  const { uploadDocument, uploadProgress, error, clearError } =
    useDocumentsStore();

  const [dragActive, setDragActive] = useState<boolean>(false);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Handle file selection
  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      handleUpload(files[0]);
    }
  };

  // Handle drag events
  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();

    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  // Handle drop event
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleUpload(e.dataTransfer.files[0]);
    }
  };

  // Handle file upload
  const handleUpload = async (file: File) => {
    // Clear any previous errors
    clearError();

    // Validate file size (10MB limit)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      showErrorToast('File size exceeds 10MB limit');
      return;
    }

    setIsUploading(true);

    try {
      await uploadDocument(file);
      showSuccessToast(`Successfully uploaded ${file.name}`);

      // Reset the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Upload failed:', error);
      showErrorToast('Failed to upload document');
    } finally {
      setIsUploading(false);
    }
  };

  // Open file selector on button click
  const openFileSelector = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  // Get the current upload progress
  const currentProgress = Object.values(uploadProgress)[0] || 0;

  return (
    <div className="mt-4">
      <h2 className="text-xl font-semibold mb-4">Upload Document</h2>

      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center ${
          dragActive
            ? 'border-indigo-500 bg-indigo-50'
            : 'border-gray-300 hover:border-indigo-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          className="hidden"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".pdf,.doc,.docx,.txt,.md"
          aria-label="Upload document"
        />

        <div className="space-y-2">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <div className="flex text-sm text-gray-600">
            <label htmlFor="file-upload" className="relative cursor-pointer">
              <span className="text-indigo-600 hover:text-indigo-500">
                Upload a file
              </span>
              <span className="pl-1">or drag and drop</span>
            </label>
          </div>
          <p className="text-xs text-gray-500">
            PDF, DOC, DOCX, TXT, MD up to 10MB
          </p>
        </div>
      </div>

      {isUploading && currentProgress > 0 && (
        <div className="mt-4">
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className="bg-indigo-600 h-2.5 rounded-full transition-all duration-300"
              style={{ width: `${currentProgress}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-600 mt-2">
            Uploading: {currentProgress}%
          </p>
        </div>
      )}

      {error && (
        <div className="mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          <span className="block sm:inline">{error}</span>
          <button
            className="absolute top-0 bottom-0 right-0 px-4 py-3"
            onClick={clearError}
          >
            <span className="text-xl">&times;</span>
          </button>
        </div>
      )}

      <button
        type="button"
        onClick={openFileSelector}
        disabled={isUploading}
        className={`mt-4 w-full inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white ${
          isUploading
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
        }`}
      >
        {isUploading ? 'Uploading...' : 'Select File'}
      </button>
    </div>
  );
};

export default DocumentUpload;
