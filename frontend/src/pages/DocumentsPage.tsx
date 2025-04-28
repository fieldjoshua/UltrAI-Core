import React from 'react';
import DocumentList from '../features/documents/components/DocumentList';
import DocumentUpload from '../features/documents/components/DocumentUpload';

const DocumentsPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        Document Management
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-2">
          <DocumentList />
        </div>
        <div>
          <DocumentUpload />
        </div>
      </div>
    </div>
  );
};

export default DocumentsPage;
