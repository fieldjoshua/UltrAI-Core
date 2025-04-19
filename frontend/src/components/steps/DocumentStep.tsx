import React, { RefObject } from 'react';
import { Button } from '../ui/button'; // Adjust path
import { Checkbox } from '../ui/checkbox'; // Adjust path
import { Label } from '../ui/label'; // Adjust path
import { Progress } from '../ui/progress'; // Adjust path
import { Upload, X, File, Check } from 'lucide-react';

interface UploadedDoc {
    id: string;
    name: string;
}

interface DocumentStepProps {
    documents: File[];
    uploadProgress: { [key: string]: number };
    uploadedDocuments: UploadedDoc[];
    isUsingDocuments: boolean;
    isProcessing: boolean;
    isOffline: boolean;
    fileInputRef: RefObject<HTMLInputElement>;
    onFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void;
    onRemoveDocument: (index: number) => void;
    onUploadDocuments: () => Promise<void>;
    onToggleDocumentMode: () => void;
}

const DocumentStep: React.FC<DocumentStepProps> = ({
    documents,
    uploadProgress,
    uploadedDocuments,
    isUsingDocuments,
    isProcessing,
    isOffline,
    fileInputRef,
    onFileSelect,
    onRemoveDocument,
    onUploadDocuments,
    onToggleDocumentMode,
}) => {
    if (isOffline && !isUsingDocuments) {
        // Optionally show a message if offline and not already using docs
        return <p className="text-center text-gray-500">Document upload unavailable while offline.</p>;
    }

    return (
        <div className="space-y-6 fadeIn">
            <div className="mb-4">
                <div className="flex items-center space-x-2 mb-2">
                    <Checkbox
                        id="useDocumentsCheckbox"
                        checked={isUsingDocuments}
                        onCheckedChange={onToggleDocumentMode}
                        disabled={isProcessing || isOffline}
                    />
                    <Label htmlFor="useDocumentsCheckbox" className="text-lg font-medium text-gray-800 dark:text-white">
                        Include documents in your analysis
                    </Label>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Upload files that provide context or information relevant to
                    your query (optional).
                </p>
            </div>

            {isUsingDocuments && (
                <div className="space-y-4">
                    <div
                        className={`border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-8 text-center transition-colors ${isOffline ? 'cursor-not-allowed opacity-50' : 'cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50'}`}
                        onClick={() => !isOffline && fileInputRef.current?.click()}
                    >
                        <Upload className={`h-10 w-10 mx-auto mb-3 ${isOffline ? 'text-gray-600' : 'text-gray-400 dark:text-gray-600'}`} />
                        <p className={`text-gray-600 dark:text-gray-400 ${isOffline ? 'text-gray-500' : ''}`}>
                            {isOffline ? 'File upload disabled offline' : 'Drag and drop files here, or click to select'}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                            Supports PDF, TXT, DOCX, and more (max 4MB per file)
                        </p>
                        <input
                            type="file"
                            ref={fileInputRef}
                            className="hidden"
                            multiple
                            onChange={onFileSelect}
                            disabled={isProcessing || isOffline}
                            aria-label="File Upload Input"
                        />
                    </div>

                    {/* Document List */}
                    {documents.length > 0 && (
                        <div className="mt-4">
                            <h3 className="font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Selected Documents ({documents.length})
                            </h3>
                            <div className="space-y-2">
                                {documents.map((doc, index) => (
                                    <div
                                        key={index}
                                        className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 p-3 rounded-md"
                                    >
                                        <div className="flex items-center space-x-3 overflow-hidden">
                                            <File className="h-5 w-5 text-blue-500 flex-shrink-0" />
                                            <div className="overflow-hidden">
                                                <p className="text-sm font-medium text-gray-800 dark:text-gray-200 truncate" title={doc.name}>
                                                    {doc.name}
                                                </p>
                                                <p className="text-xs text-gray-500 dark:text-gray-400">
                                                    {(doc.size / 1024).toFixed(1)} KB
                                                </p>
                                            </div>
                                        </div>

                                        <div className="flex items-center flex-shrink-0 ml-2">
                                            {uploadProgress[doc.name] !== undefined &&
                                                uploadProgress[doc.name] < 100 ? (
                                                <div className="w-16">
                                                    <Progress
                                                        value={uploadProgress[doc.name]}
                                                        className="h-1.5" // Make progress bar slimmer
                                                    />
                                                </div>
                                            ) : uploadProgress[doc.name] === 100 ? (
                                                <Check className="h-5 w-5 text-green-500" />
                                            ) : (
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    className="h-7 w-7 p-0 text-gray-500 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400"
                                                    onClick={() => onRemoveDocument(index)}
                                                    title="Remove file"
                                                    disabled={isProcessing}
                                                >
                                                    <X className="h-4 w-4" />
                                                </Button>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Uploaded Documents */}
                    {uploadedDocuments.length > 0 && (
                        <div className="mt-4">
                            <h3 className="font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Context Documents ({uploadedDocuments.length})
                            </h3>
                            <div className="space-y-2">
                                {uploadedDocuments.map((doc) => (
                                    <div
                                        key={doc.id}
                                        className="flex items-center justify-between bg-green-50 dark:bg-green-900/20 p-3 rounded-md"
                                    >
                                        <div className="flex items-center space-x-3 overflow-hidden">
                                            <File className="h-5 w-5 text-green-500 flex-shrink-0" />
                                            <p className="text-sm font-medium text-gray-800 dark:text-gray-200 truncate" title={doc.name}>
                                                {doc.name}
                                            </p>
                                        </div>
                                        {/* Optionally add a remove button for uploaded docs? */}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {documents.length > 0 && (
                        <div className="flex justify-center mt-4">
                            <Button
                                onClick={onUploadDocuments}
                                disabled={isProcessing || documents.length === 0 || isOffline}
                                className="bg-blue-600 hover:bg-blue-700 text-white"
                            >
                                Upload Selected Documents for Context
                            </Button>
                        </div>
                    )}
                </div>
            )}
            {/* Navigation buttons handled by parent */}
        </div>
    );
};

export default DocumentStep;