import React, { useState, useEffect } from 'react';
import { 
  getOrchestratorModels, 
  processWithOrchestrator 
} from '../../api/api';

/**
 * OrchestratorInterface component provides a user interface for 
 * interacting with the modular LLM orchestration system.
 */
const OrchestratorInterface = () => {
  // State for form inputs
  const [prompt, setPrompt] = useState('');
  const [selectedModels, setSelectedModels] = useState([]);
  const [leadModel, setLeadModel] = useState('');
  const [analysisType, setAnalysisType] = useState('comparative');
  
  // State for available models
  const [availableModels, setAvailableModels] = useState([]);
  const [isLoadingModels, setIsLoadingModels] = useState(false);
  
  // State for results
  const [results, setResults] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);

  // Load available models on component mount
  useEffect(() => {
    const loadModels = async () => {
      setIsLoadingModels(true);
      try {
        const models = await getOrchestratorModels();
        setAvailableModels(models);
        
        // Set default selections if models are available
        if (models.length > 0) {
          setSelectedModels([models[0]]);
          setLeadModel(models[0]);
        }
      } catch (err) {
        setError('Failed to load available models');
        console.error('Model loading error:', err);
      } finally {
        setIsLoadingModels(false);
      }
    };
    
    loadModels();
  }, []);
  
  // Handle model selection changes
  const handleModelToggle = (model) => {
    if (selectedModels.includes(model)) {
      // Remove from selection (unless it's the last one or the lead model)
      if (selectedModels.length > 1 && model !== leadModel) {
        setSelectedModels(selectedModels.filter(m => m !== model));
      }
    } else {
      // Add to selection
      setSelectedModels([...selectedModels, model]);
    }
  };
  
  // Handle lead model change
  const handleLeadModelChange = (model) => {
    setLeadModel(model);
    
    // Ensure the lead model is selected
    if (!selectedModels.includes(model)) {
      setSelectedModels([...selectedModels, model]);
    }
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate inputs
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }
    
    if (selectedModels.length === 0) {
      setError('Please select at least one model');
      return;
    }
    
    setIsProcessing(true);
    setError(null);
    
    try {
      // Process with orchestrator
      const response = await processWithOrchestrator({
        prompt,
        models: selectedModels,
        leadModel: leadModel || selectedModels[0],
        analysisType,
      });
      
      setResults(response);
    } catch (err) {
      setError(`Error processing request: ${err.message}`);
      console.error('Processing error:', err);
    } finally {
      setIsProcessing(false);
    }
  };
  
  // Format model display name
  const formatModelName = (model) => {
    const parts = model.split('-');
    if (parts.length > 1) {
      return `${parts[0].charAt(0).toUpperCase() + parts[0].slice(1)} ${parts[1].toUpperCase()}`;
    }
    return model;
  };
  
  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">UltrAI Orchestrator</h1>
      
      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}
      
      {/* Input form */}
      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 mb-6">
        {/* Prompt input */}
        <div className="mb-4">
          <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-1">
            Prompt
          </label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"
            rows={4}
            placeholder="What would you like to analyze?"
          ></textarea>
        </div>
        
        {/* Model selection */}
        <div className="mb-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Select Models</h3>
          
          {isLoadingModels ? (
            <div className="flex items-center space-x-2 text-gray-500">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Loading available models...</span>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
              {availableModels.map((model) => (
                <div
                  key={model}
                  className={`border rounded-md p-3 cursor-pointer ${
                    selectedModels.includes(model) ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                  }`}
                  onClick={() => handleModelToggle(model)}
                >
                  <div className="flex justify-between items-center">
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id={`model-${model}`}
                        checked={selectedModels.includes(model)}
                        onChange={() => handleModelToggle(model)}
                        className="mr-2"
                      />
                      <label htmlFor={`model-${model}`} className="text-sm">
                        {formatModelName(model)}
                      </label>
                    </div>
                    
                    {selectedModels.includes(model) && (
                      <div className="flex items-center">
                        <input
                          type="radio"
                          id={`lead-${model}`}
                          name="leadModel"
                          checked={leadModel === model}
                          onChange={() => handleLeadModelChange(model)}
                          className="mr-1"
                        />
                        <label htmlFor={`lead-${model}`} className="text-xs text-gray-500">
                          Primary
                        </label>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* Analysis type selection */}
        <div className="mb-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Analysis Type</h3>
          <div className="flex space-x-4">
            <label className="flex items-center">
              <input
                type="radio"
                name="analysisType"
                value="comparative"
                checked={analysisType === 'comparative'}
                onChange={() => setAnalysisType('comparative')}
                className="mr-2"
              />
              <span>Comparative</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="analysisType"
                value="factual"
                checked={analysisType === 'factual'}
                onChange={() => setAnalysisType('factual')}
                className="mr-2"
              />
              <span>Factual</span>
            </label>
          </div>
        </div>
        
        {/* Submit button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isProcessing}
            className={`px-4 py-2 rounded-md ${
              isProcessing
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {isProcessing ? 'Processing...' : 'Generate Response'}
          </button>
        </div>
      </form>
      
      {/* Results */}
      {results && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Results</h2>
          
          {/* Initial responses */}
          {results.initial_responses && results.initial_responses.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-medium mb-2">Initial Responses</h3>
              <div className="space-y-4">
                {results.initial_responses.map((response, index) => (
                  <div key={index} className="bg-gray-50 p-4 rounded border border-gray-200">
                    <h4 className="font-medium mb-2">
                      {response.model} ({response.provider})
                      {leadModel === response.model && (
                        <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                          Primary
                        </span>
                      )}
                    </h4>
                    <p className="whitespace-pre-wrap">{response.response}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Analysis results */}
          {results.analysis_results && (
            <div className="mb-6">
              <h3 className="text-lg font-medium mb-2">
                Analysis Results ({results.analysis_results.type})
              </h3>
              {results.analysis_results.combined_summary && (
                <div className="bg-blue-50 p-4 rounded border border-blue-200">
                  <p className="whitespace-pre-wrap">{results.analysis_results.combined_summary}</p>
                </div>
              )}
            </div>
          )}
          
          {/* Synthesis */}
          {results.synthesis && (
            <div className="mb-4">
              <h3 className="text-lg font-medium mb-2">Synthesized Response</h3>
              <div className="bg-green-50 p-4 rounded border border-green-200">
                <h4 className="font-medium mb-2">
                  Synthesized by {results.synthesis.model} ({results.synthesis.provider})
                </h4>
                <p className="whitespace-pre-wrap">{results.synthesis.response}</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default OrchestratorInterface;