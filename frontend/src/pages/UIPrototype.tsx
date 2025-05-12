import React from 'react';
import AnalysisInterface from '../components/AnalysisInterface';

const UIPrototype: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">UI Prototype</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            This prototype demonstrates the core functionality of the Ultra analysis system.
          </p>
        </div>
        
        <AnalysisInterface />
      </div>
    </div>
  );
};

export default UIPrototype;