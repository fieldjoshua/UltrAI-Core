import apiClient, { endpoints, request } from './api';
import { Document } from '../features/documents/documentsSlice';

/**
 * Get all documents
 * @returns Array of documents
 */
export const getAllDocuments = async (): Promise<Document[]> => {
    return request<Document[]>({
        url: endpoints.documents.getAll,
        method: 'GET',
    });
};

/**
 * Get document by ID
 * @param id Document ID
 * @returns Document details
 */
export const getDocumentById = async (id: string): Promise<Document> => {
    return request<Document>({
        url: endpoints.documents.getById(id),
        method: 'GET',
    });
};

/**
 * Upload a document
 * @param file File to upload
 * @returns Uploaded document details
 */
export const uploadDocument = async (file: File): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);

    return request<Document>({
        url: endpoints.documents.upload,
        method: 'POST',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
};

/**
 * Upload multiple documents with progress tracking
 * @param files Files to upload
 * @param onUploadProgress Progress callback
 * @returns Array of uploaded document details
 */
export const uploadMultipleDocuments = async (
    files: File[],
    onUploadProgress?: (progressEvent: any) => void
): Promise<Document[]> => {
    const formData = new FormData();

    files.forEach((file) => {
        formData.append('files', file);
    });

    return request<Document[]>({
        url: endpoints.documents.upload,
        method: 'POST',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        onUploadProgress,
    });
};

/**
 * Delete a document
 * @param id Document ID to delete
 * @returns Success message
 */
export const deleteDocument = async (id: string): Promise<{ success: boolean; message: string }> => {
    return request<{ success: boolean; message: string }>({
        url: endpoints.documents.delete(id),
        method: 'DELETE',
    });
};

/**
 * Create a chunked upload session
 * @param fileInfo Information about the file
 * @returns Session ID and upload details
 */
export const createUploadSession = async (fileInfo: {
    fileName: string;
    fileSize: number;
    chunkSize: number;
    totalChunks: number;
}): Promise<{
    sessionId: string;
    chunkSize: number;
    totalChunks: number;
}> => {
    return request<{
        sessionId: string;
        chunkSize: number;
        totalChunks: number;
    }>({
        url: '/create-document-session',
        method: 'POST',
        data: fileInfo,
    });
};

/**
 * Upload a chunk in a chunked upload session
 * @param sessionId Session ID
 * @param chunkIndex Chunk index
 * @param chunk File chunk
 * @param onUploadProgress Progress callback
 * @returns Upload status
 */
export const uploadChunk = async (
    sessionId: string,
    chunkIndex: number,
    chunk: Blob,
    onUploadProgress?: (progressEvent: any) => void
): Promise<{
    success: boolean;
    received: number;
    total: number;
}> => {
    const formData = new FormData();
    formData.append('sessionId', sessionId);
    formData.append('chunkIndex', chunkIndex.toString());
    formData.append('chunk', chunk);

    return request<{
        success: boolean;
        received: number;
        total: number;
    }>({
        url: '/upload-document-chunk',
        method: 'POST',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        onUploadProgress,
    });
};

/**
 * Finalize a chunked upload
 * @param sessionId Session ID
 * @param fileName Original file name
 * @returns Uploaded document details
 */
export const finalizeUpload = async (
    sessionId: string,
    fileName: string
): Promise<Document> => {
    return request<Document>({
        url: '/finalize-document-upload',
        method: 'POST',
        data: {
            sessionId,
            fileName,
        },
    });
};