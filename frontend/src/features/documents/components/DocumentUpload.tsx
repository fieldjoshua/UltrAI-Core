import React, { useState, useRef, ChangeEvent } from 'react';
import { useAppDispatch, useAppSelector } from '../../../hooks/redux';
import { uploadDocument, setUploadProgress } from '../documentsSlice';
import * as documentService from '../../../services/documentService';

const DocumentUpload: React.FC = () => {
  const dispatch = useAppDispatch();
  const { isLoading, uploadProgress, error } = useAppSelector(
    state => state.documents
  );
  const [dragActive, setDragActive] = useState<boolean>(false);
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
    try {
      // Update progress via Redux
      const onUploadProgress = (progressEvent: any) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        dispatch(setUploadProgress(percentCompleted));
      };

      // Use our service to upload and our Redux action to dispatch
      const uploadedDoc = await documentService.uploadDocument(file);
      dispatch(uploadDocument(file));

      // Reset the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Upload failed:', error);
      // Error handling is managed by Redux through uploadDocument thunk
    }
  };

  // Open file selector on button click
  const openFileSelector = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

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

      {isLoading && (
        <div className="mt-4">
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className="bg-indigo-600 h-2.5 rounded-full"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-600 mt-2">
            Uploading: {uploadProgress}%
          </p>
        </div>
      )}

      {error && (
        <div className="mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          Error: {error}
        </div>
      )}

      <button
        type="button"
        onClick={openFileSelector}
        disabled={isLoading}
        className={`mt-4 w-full inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white ${
          isLoading
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
        }`}
      >
        {isLoading ? 'Uploading...' : 'Select File'}
      </button>
    </div>
  );
};

export default DocumentUpload;
