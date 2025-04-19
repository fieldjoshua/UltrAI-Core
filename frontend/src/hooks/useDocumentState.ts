import { useState, useCallback, useRef } from 'react';

// Define types used by the hook
interface UploadedDoc {
    id: string;
    name: string;
}

interface UploadProgress {
    [key: string]: number;
}

// Custom hook for managing document state and logic
export const useDocumentState = (initialIsUsingDocuments = false) => {
    const [documents, setDocuments] = useState<File[]>([]);
    const [uploadProgress, setUploadProgress] = useState<UploadProgress>({});
    const [uploadedDocuments, setUploadedDocuments] = useState<UploadedDoc[]>([]);
    const [isUsingDocuments, setIsUsingDocuments] = useState<boolean>(
        initialIsUsingDocuments
    );
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [documentError, setDocumentError] = useState<string | null>(null);

    // Handler for file selection with size validation
    const handleFileSelect = useCallback(
        (e: React.ChangeEvent<HTMLInputElement>) => {
            setDocumentError(null); // Clear previous errors
            const fileList = e.target.files;
            if (fileList) {
                const MAX_FILE_SIZE = 4 * 1024 * 1024; // 4MB
                const validFiles: File[] = [];
                let hasOversize = false;

                Array.from(fileList).forEach((file) => {
                    if (file.size > MAX_FILE_SIZE) {
                        hasOversize = true;
                    } else {
                        validFiles.push(file);
                    }
                });

                if (hasOversize) {
                    setDocumentError(
                        `Some files exceed the 4MB size limit. Only smaller files were added.`
                    );
                }

                if (validFiles.length > 0) {
                    setDocuments((prev) => [...prev, ...validFiles]);
                }
            }
            // Reset file input
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        },
        []
    );

    // Handler to remove a document from the selection list
    const removeDocument = useCallback((indexToRemove: number) => {
        setDocuments((docs) =>
            docs.filter((_, index) => index !== indexToRemove)
        );
    }, []);

    // Handler to simulate document upload (replace with API call later)
    const uploadDocuments = useCallback(async () => {
        if (documents.length === 0) return;
        setDocumentError(null);
        const currentUploadedDocs = [...uploadedDocuments]; // Copy current state

        for (let i = 0; i < documents.length; i++) {
            const file = documents[i];
            try {
                setUploadProgress((prev) => ({ ...prev, [file.name]: 0 }));
                for (let progress = 0; progress <= 100; progress += 10) {
                    setUploadProgress((prev) => ({ ...prev, [file.name]: progress }));
                    await new Promise((r) => setTimeout(r, 50)); // Shorter delay
                }
                const mockDocId = `doc-${Math.random().toString(36).substring(2, 9)}`;
                currentUploadedDocs.push({ id: mockDocId, name: file.name });
            } catch (err: any) {
                setDocumentError(`Failed to upload ${file.name}: ${err.message}`);
            }
        }
        setUploadedDocuments(currentUploadedDocs); // Update state once after loop
        setDocuments([]); // Clear selection list after upload
    }, [documents, uploadedDocuments]); // Include dependencies

    // Handler to toggle the document usage mode
    const toggleDocumentMode = useCallback(() => {
        setIsUsingDocuments((prev) => !prev);
    }, []);

    // Function to reset document state, e.g., for starting a new analysis
    const resetDocumentState = useCallback(() => {
        setDocuments([]);
        setUploadProgress({});
        setUploadedDocuments([]);
        setIsUsingDocuments(initialIsUsingDocuments);
        setDocumentError(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    }, [initialIsUsingDocuments]);

    return {
        documents,
        uploadProgress,
        uploadedDocuments,
        isUsingDocuments,
        fileInputRef, // Expose the ref
        documentError, // Expose error state
        handleFileSelect,
        removeDocument,
        uploadDocuments,
        toggleDocumentMode,
        resetDocumentState, // Expose the reset function
    };
};