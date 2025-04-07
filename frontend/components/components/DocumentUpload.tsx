'use client'

import React, { useState, useCallback, useMemo } from 'react'
import { FileIcon, UploadIcon, X, AlertCircle } from 'lucide-react'

interface DocumentUploadProps {
  onFilesSelected: (files: File[]) => void;
  maxFiles?: number;
  maxSizeMB?: number;
  acceptedTypes?: string[];
}

// Memoized FilePreview component
const FilePreview = React.memo(({ 
  file, 
  onRemove 
}: { 
  file: File, 
  onRemove: () => void 
}) => {
  // Format file size for display
  const formattedSize = useMemo(() => {
    const size = file.size;
    if (size < 1024) return `${size} B`;
    if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  }, [file.size]);
  
  // Get appropriate icon color based on file type
  const iconColor = useMemo(() => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    if (['pdf'].includes(extension || '')) return 'text-red-400';
    if (['doc', 'docx'].includes(extension || '')) return 'text-blue-400';
    if (['txt', 'md'].includes(extension || '')) return 'text-green-400';
    return 'text-gray-400';
  }, [file.name]);
  
  return (
    <div className="flex items-center justify-between p-2 bg-gray-900/30 rounded-md border border-gray-800 my-1">
      <div className="flex items-center">
        <FileIcon className={`w-4 h-4 mr-2 ${iconColor}`} />
        <div className="text-sm mr-2 text-gray-300 truncate max-w-[200px]">
          {file.name}
        </div>
        <div className="text-xs text-gray-500">{formattedSize}</div>
      </div>
      <button 
        onClick={onRemove}
        className="text-gray-500 hover:text-red-400 p-1 rounded-full hover:bg-gray-800"
        aria-label="Remove file"
      >
        <X className="w-3 h-3" />
      </button>
    </div>
  );
});

FilePreview.displayName = 'FilePreview';

// Main component with memoization
export const DocumentUpload = React.memo(({
  onFilesSelected,
  maxFiles = 5,
  maxSizeMB = 10,
  acceptedTypes = ['.pdf', '.txt', '.doc', '.docx', '.md']
}: DocumentUploadProps) => {
  const [files, setFiles] = useState<File[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Convert max size to bytes for internal validation
  const maxSizeBytes = useMemo(() => maxSizeMB * 1024 * 1024, [maxSizeMB]);
  
  // Formatted accepted types for display
  const formattedTypes = useMemo(() => {
    return acceptedTypes.map(type => type.replace('.', '').toUpperCase()).join(', ');
  }, [acceptedTypes]);
  
  // Handle file validation and addition
  const processFiles = useCallback((newFiles: FileList | null) => {
    if (!newFiles || newFiles.length === 0) return;
    
    setError(null);
    
    // Check if adding these files would exceed the limit
    if (files.length + newFiles.length > maxFiles) {
      setError(`You can only upload up to ${maxFiles} files`);
      return;
    }
    
    // Validate and add each file
    const validFiles: File[] = [];
    const invalidFiles: string[] = [];
    
    Array.from(newFiles).forEach(file => {
      // Validate file size
      if (file.size > maxSizeBytes) {
        invalidFiles.push(`${file.name} (exceeds ${maxSizeMB}MB)`);
        return;
      }
      
      // Validate file type
      const fileExt = `.${file.name.split('.').pop()?.toLowerCase()}`;
      if (!acceptedTypes.includes(fileExt)) {
        invalidFiles.push(`${file.name} (invalid type)`);
        return;
      }
      
      validFiles.push(file);
    });
    
    if (invalidFiles.length > 0) {
      setError(`Some files couldn't be added: ${invalidFiles.join(', ')}`);
    }
    
    if (validFiles.length > 0) {
      const updatedFiles = [...files, ...validFiles];
      setFiles(updatedFiles);
      onFilesSelected(updatedFiles);
    }
  }, [files, maxFiles, maxSizeBytes, acceptedTypes, onFilesSelected]);
  
  // Event handlers with useCallback to prevent unnecessary re-renders
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  }, []);
  
  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  }, []);
  
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);
  
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    processFiles(e.dataTransfer.files);
  }, [processFiles]);
  
  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    processFiles(e.target.files);
    // Reset the input value so the same file can be uploaded again if removed
    e.target.value = '';
  }, [processFiles]);
  
  const handleRemoveFile = useCallback((index: number) => {
    const newFiles = [...files];
    newFiles.splice(index, 1);
    setFiles(newFiles);
    onFilesSelected(newFiles);
  }, [files, onFilesSelected]);
  
  return (
    <div className="space-y-4">
      <div 
        className={`
          border-2 border-dashed rounded-lg p-6 text-center transition-colors
          ${dragActive ? 'border-cyan-500 bg-cyan-950/20' : 'border-gray-700 hover:border-gray-600'}
        `}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-upload"
          className="hidden"
          multiple
          accept={acceptedTypes.join(',')}
          onChange={handleChange}
        />
        <label 
          htmlFor="file-upload"
          className="flex flex-col items-center justify-center cursor-pointer py-4"
        >
          <UploadIcon className="w-10 h-10 text-cyan-500 mb-2" />
          <p className="text-cyan-300 font-medium mb-1">Drop files here or click to upload</p>
          <p className="text-xs text-gray-400">
            {formattedTypes} files up to {maxSizeMB}MB ({maxFiles} max)
          </p>
        </label>
      </div>
      
      {error && (
        <div className="flex items-center gap-2 text-red-400 bg-red-900/20 p-2 rounded-md">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span className="text-sm">{error}</span>
        </div>
      )}
      
      {files.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-cyan-400 mb-2">Selected files ({files.length}/{maxFiles})</h3>
          <div className="space-y-1 max-h-60 overflow-y-auto p-1">
            {files.map((file, index) => (
              <FilePreview
                key={`${file.name}-${index}`}
                file={file}
                onRemove={() => handleRemoveFile(index)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
});

DocumentUpload.displayName = 'DocumentUpload'; 