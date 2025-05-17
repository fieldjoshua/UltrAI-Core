'use client'

import React, { useState, useCallback, useMemo } from 'react'
import { FileText, ChevronDown, ChevronUp, AlertCircle, Loader2 } from 'lucide-react'

interface DocumentChunk {
  text: string;
  relevance: number;
  page?: number;
}

interface ProcessedDocument {
  id: string;
  name: string;
  chunks: DocumentChunk[];
  totalChunks: number;
  type: string;
}

interface DocumentViewerProps {
  documents: ProcessedDocument[];
  isLoading?: boolean;
  error?: string | null;
}

// Memoized DocumentChunk component to prevent unnecessary re-renders
const DocumentChunkItem = React.memo(({ chunk }: { chunk: DocumentChunk }) => {
  return (
    <div className="p-2 border border-gray-800 rounded my-1 text-xs bg-gray-900/40">
      <div className="flex justify-between mb-1">
        <span className="text-cyan-400">
          {chunk.page ? `Page ${chunk.page}` : 'Section'}
        </span>
        <span className="text-pink-400">
          Relevance: {(chunk.relevance * 100).toFixed(0)}%
        </span>
      </div>
      <p className="whitespace-pre-wrap text-gray-300">{chunk.text.length > 300 ? `${chunk.text.substring(0, 300)}...` : chunk.text}</p>
    </div>
  );
});

DocumentChunkItem.displayName = 'DocumentChunkItem';

// Memoized Document Item component
const DocumentItem = React.memo(({ document }: { document: ProcessedDocument }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpand = useCallback(() => {
    setIsExpanded(prev => !prev);
  }, []);

  // Only render visible chunks to improve performance
  const visibleChunks = useMemo(() => {
    return isExpanded ? document.chunks : document.chunks.slice(0, 2);
  }, [isExpanded, document.chunks]);

  return (
    <div className="mb-4 border border-gray-800 rounded-lg p-3 bg-gray-900/40">
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={toggleExpand}
      >
        <div className="flex items-center">
          <FileText className="w-4 h-4 mr-2 text-cyan-500" />
          <span className="font-medium text-cyan-300">{document.name}</span>
          <span className="ml-2 text-xs text-gray-500">({document.type})</span>
        </div>
        <div className="flex items-center">
          <span className="text-xs text-gray-500 mr-2">{document.totalChunks} chunks</span>
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-gray-500" />
          ) : (
            <ChevronDown className="w-4 h-4 text-gray-500" />
          )}
        </div>
      </div>

      {visibleChunks.length > 0 && (
        <div className="mt-2">
          {visibleChunks.map((chunk, index) => (
            <DocumentChunkItem key={`${document.id}-chunk-${index}`} chunk={chunk} />
          ))}

          {!isExpanded && document.chunks.length > 2 && (
            <button
              className="w-full text-center text-xs text-cyan-500 hover:text-cyan-400 mt-1 p-1"
              onClick={toggleExpand}
            >
              Show {document.chunks.length - 2} more chunks...
            </button>
          )}
        </div>
      )}
    </div>
  );
});

DocumentItem.displayName = 'DocumentItem';

// Main component with memoization
export const DocumentViewer = React.memo(({
  documents,
  isLoading = false,
  error = null
}: DocumentViewerProps) => {
  // Calculate total chunks across all documents
  const totalChunks = useMemo(() => {
    return documents.reduce((acc, doc) => acc + doc.totalChunks, 0);
  }, [documents]);

  // Empty state - no documents yet
  if (!isLoading && documents.length === 0 && !error) {
    return (
      <div className="text-center py-8 text-gray-500">
        <FileText className="mx-auto w-10 h-10 mb-3 text-gray-600" />
        <p>Upload documents to analyze them with your prompt.</p>
      </div>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="text-center py-8">
        <Loader2 className="mx-auto w-8 h-8 animate-spin text-cyan-500 mb-3" />
        <p className="text-cyan-300">Processing documents...</p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="text-center py-8 text-red-400">
        <AlertCircle className="mx-auto w-8 h-8 mb-3 text-red-500" />
        <p>{error}</p>
      </div>
    );
  }

  // Loaded state with documents
  return (
    <div>
      <div className="mb-4 flex justify-between items-center">
        <h3 className="font-bold text-cyan-400">Processed Documents</h3>
        <span className="text-xs text-gray-500">{documents.length} documents, {totalChunks} total chunks</span>
      </div>

      <div className="space-y-2">
        {documents.map(document => (
          <DocumentItem key={document.id} document={document} />
        ))}
      </div>
    </div>
  );
});

DocumentViewer.displayName = 'DocumentViewer';
