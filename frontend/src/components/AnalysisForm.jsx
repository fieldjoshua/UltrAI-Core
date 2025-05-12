import React, { useState, useEffect } from 'react';
import { Loader2, ChevronRight, AlertCircle, CheckCircle } from 'lucide-react';
import { fetchAvailableModels, analyzePrompt } from '../services/api';

/**
 * Analysis form component for submitting text analysis requests
 * 
 * This component handles:
 * - Prompt input
 * - Model selection
 * - Analysis pattern selection
 * - Submission and results display
 */
const AnalysisForm = () => {
  // Form state
  const [prompt, setPrompt] = useState('');
  const [selectedModels, setSelectedModels] = useState([]);
  const [primaryModel, setPrimaryModel] = useState('');
  const [pattern, setPattern] = useState('gut');
  
  // UI state
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [modelLoadError, setModelLoadError] = useState(null);
  const [results, setResults] = useState(null);
  
  // Models state
  const [availableModels, setAvailableModels] = useState([]);
  
  // Analysis patterns
  const patterns = [
    { id: 'gut', name: 'Gut Check', description: 'Rapid evaluation of different perspectives' },
    { id: 'confidence', name: 'Confidence Analysis', description: 'Evaluates the strength of each model response' },
    { id: 'critique', name: 'Critique Analysis', description: 'Models critically evaluate each other\'s reasoning' },
    { id: 'perspective', name: 'Perspective Analysis', description: 'Examines a question from multiple analytical perspectives' },
  ];
  
  // Load available models on component mount
  useEffect(() => {
    const loadModels = async () => {
      try {
        setIsLoading(true);
        const models = await fetchAvailableModels();
        setAvailableModels(models);
        
        // Set default selections if models are available
        if (models.length > 0) {
          setSelectedModels([models[0]]);
          setPrimaryModel(models[0]);
        }
        
        setModelLoadError(null);
      } catch (err) {
        console.error('Failed to load models:', err);
        setModelLoadError(err.message || 'Failed to load models');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadModels();
  }, []);
  
  // Handle model selection
  const handleModelSelect = (model) => {
    // If already selected, remove it (unless it's the last one)
    if (selectedModels.includes(model)) {
      if (selectedModels.length > 1) {
        setSelectedModels(selectedModels.filter(m => m !== model));
        
        // If removing the primary model, set a new one
        if (primaryModel === model) {
          setPrimaryModel(selectedModels.filter(m => m !== model)[0]);
        }
      }
    } else {
      // Add to selection
      setSelectedModels([...selectedModels, model]);
    }
  };
  
  // Set primary model
  const handlePrimaryModelChange = (model) => {
    // Ensure model is selected
    if (!selectedModels.includes(model)) {
      setSelectedModels([...selectedModels, model]);
    }
    setPrimaryModel(model);
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }
    
    if (selectedModels.length === 0) {
      setError('Please select at least one model');
      return;
    }
    
    if (!primaryModel) {
      setError('Please select a primary model');
      return;
    }
    
    try {
      setIsLoading(true);
      setError(null);
      
      // Prepare payload
      const payload = {
        prompt,
        selected_models: selectedModels,
        ultra_model: primaryModel,
        pattern,
        options: {}
      };
      
      // Submit analysis request
      const response = await analyzePrompt(payload);
      
      // Handle success
      setResults(response.results);
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.message || 'An error occurred during analysis');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Format model name for display
  const formatModelName = (model) => {
    // Convert model IDs to readable names
    const modelMap = {
      'gpt4o': 'GPT-4o',
      'gpt4turbo': 'GPT-4 Turbo',
      'claude37': 'Claude 3.7',
      'claude3opus': 'Claude 3 Opus',
      'gemini15': 'Gemini 1.5 Pro',
      'llama3': 'Llama 3',
    };
    
    return modelMap[model] || model;
  };
  
  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">AI Analysis</h2>
      
      {/* Model load error */}
      {modelLoadError && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
          <div className="flex items-start">
            <AlertCircle className="text-red-500 mt-1 mr-2" size={18} />
            <div>
              <p className="text-red-700">{modelLoadError}</p>
              <p className="text-red-600 text-sm mt-1">
                Using default models instead
              </p>
            </div>
          </div>
        </div>
      )}
      
      {/* Analysis form */}
      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 mb-6">
        {/* Prompt input */}
        <div className="mb-4">
          <label 
            htmlFor="prompt" 
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Prompt
          </label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            rows={4}
            placeholder="What would you like to analyze?"
            aria-label="Prompt"
          />
        </div>
        
        {/* Model selection */}
        <div className="mb-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Select AI Models</h3>
          
          {isLoading && availableModels.length === 0 ? (
            <div className="flex items-center space-x-2 text-gray-500">
              <Loader2 className="animate-spin" size={16} />
              <span>Loading available models...</span>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
              {availableModels.map((model) => (
                <div 
                  key={model}
                  className={`border rounded-md p-3 cursor-pointer ${
                    selectedModels.includes(model) 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200'
                  }`}
                  onClick={() => handleModelSelect(model)}
                >
                  <div className="flex justify-between items-center">
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id={`model-${model}`}
                        checked={selectedModels.includes(model)}
                        onChange={() => handleModelSelect(model)}
                        className="mr-2"
                        aria-label={model}
                      />
                      <label 
                        htmlFor={`model-${model}`}
                        className="text-sm"
                      >
                        {formatModelName(model)}
                      </label>
                    </div>
                    
                    {selectedModels.includes(model) && (
                      <div className="flex items-center">
                        <input
                          type="radio"
                          id={`primary-${model}`}
                          name="primaryModel"
                          checked={primaryModel === model}
                          onChange={() => handlePrimaryModelChange(model)}
                          className="mr-1"
                          aria-label={`Set ${model} as primary`}
                        />
                        <label 
                          htmlFor={`primary-${model}`}
                          className="text-xs text-gray-500"
                        >
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
        
        {/* Pattern selection */}
        <div className="mb-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Analysis Pattern</h3>
          
          <div className="space-y-2">
            {patterns.map((p) => (
              <div 
                key={p.id}
                className={`border rounded-md p-3 cursor-pointer ${
                  pattern === p.id 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200'
                }`}
                onClick={() => setPattern(p.id)}
              >
                <div className="flex items-center">
                  <input
                    type="radio"
                    id={`pattern-${p.id}`}
                    name="pattern"
                    value={p.id}
                    checked={pattern === p.id}
                    onChange={() => setPattern(p.id)}
                    className="mr-2"
                    aria-label={p.name}
                  />
                  <label htmlFor={`pattern-${p.id}`}>
                    <div className="font-medium text-sm">{p.name}</div>
                    <div className="text-xs text-gray-500">{p.description}</div>
                  </label>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
            <div className="flex items-start">
              <AlertCircle className="text-red-500 mt-1 mr-2" size={18} />
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        )}
        
        {/* Submit button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isLoading}
            className={`flex items-center px-4 py-2 rounded-md ${
              isLoading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {isLoading ? (
              <>
                <Loader2 data-testid="loading-indicator" className="animate-spin mr-2" size={16} />
                Analyzing...
              </>
            ) : (
              <>
                Run Analysis
                <ChevronRight className="ml-1" size={16} />
              </>
            )}
          </button>
        </div>
      </form>
      
      {/* Results */}
      {results && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold mb-4">Analysis Results</h3>
          
          <div className="mb-6">
            <h4 className="text-lg font-medium mb-2">Your Prompt</h4>
            <div className="bg-gray-50 p-4 rounded border border-gray-200">
              <p>{prompt}</p>
            </div>
          </div>
          
          {/* Performance metrics */}
          {results.performance && (
            <div className="mb-6">
              <h4 className="text-lg font-medium mb-2">Performance</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gray-50 p-3 rounded border border-gray-200">
                  <p className="text-xs text-gray-500">Total Time</p>
                  <p className="font-medium">{results.performance.total_time_seconds.toFixed(1)}s</p>
                </div>
                <div className="bg-gray-50 p-3 rounded border border-gray-200">
                  <p className="text-xs text-gray-500">Models Used</p>
                  <p className="font-medium">{Object.keys(results.model_responses || {}).length}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded border border-gray-200">
                  <p className="text-xs text-gray-500">Total Tokens</p>
                  <p className="font-medium">
                    {results.performance.token_counts && 
                      results.performance.token_counts[primaryModel]?.total_tokens}
                  </p>
                </div>
                <div className="bg-gray-50 p-3 rounded border border-gray-200">
                  <p className="text-xs text-gray-500">Primary Model</p>
                  <p className="font-medium">{formatModelName(primaryModel)}</p>
                </div>
              </div>
            </div>
          )}
          
          {/* Ultra response */}
          <div className="mb-6">
            <h4 className="text-lg font-medium mb-2">Ultra Analysis</h4>
            <div className="bg-blue-50 p-4 rounded border border-blue-200">
              <p className="whitespace-pre-wrap text-gray-900">{results.ultra_response}</p>
            </div>
          </div>
          
          {/* Individual model responses */}
          {results.model_responses && (
            <div className="mb-4">
              <h4 className="text-lg font-medium mb-2">Individual Model Responses</h4>
              <div className="space-y-4">
                {Object.entries(results.model_responses).map(([model, response]) => (
                  <div key={model} className="bg-white rounded border border-gray-200">
                    <div className="bg-gray-50 px-4 py-2 border-b border-gray-200 font-medium">
                      {formatModelName(model)}
                      {model === primaryModel && (
                        <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                          Primary
                        </span>
                      )}
                    </div>
                    <div className="p-4">
                      <p className="whitespace-pre-wrap text-gray-900">{response}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Success message */}
          <div className="mt-4 bg-green-50 border border-green-200 rounded-md p-4">
            <div className="flex items-start">
              <CheckCircle className="text-green-500 mt-1 mr-2" size={18} />
              <p className="text-green-700">Analysis completed successfully</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisForm;