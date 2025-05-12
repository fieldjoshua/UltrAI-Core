import React from 'react';
import OrchestratorInterface from '../components/OrchestratorInterface';

/**
 * Page for the orchestrator interface
 */
const OrchestratorPage: React.FC = () => {
  return (
    <div className="container mx-auto py-6 px-4">
      <h1 className="text-3xl font-bold mb-8">UltrAI Orchestrator</h1>
      <OrchestratorInterface />
    </div>
  );
};

export default OrchestratorPage;