import React, { useState, useEffect } from 'react';
import {
  getOrchestratorModels,
  getOrchestratorPatterns,
  processWithFeatherOrchestration,
  processWithOrchestrator,
} from '../api/orchestrator';
import { AnalysisPatternSelector } from './AnalysisPatternSelector';
import { AnalysisProgress } from './atoms/AnalysisProgress';

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
  const [selectedPattern, setSelectedPattern] = useState('gut');
  const [useFeatherOrchestration, setUseFeatherOrchestration] = useState(true);

  // State for available models and patterns
  const [availableModels, setAvailableModels] = useState([]);
  const [availablePatterns, setAvailablePatterns] = useState([]);
  const [isLoadingModels, setIsLoadingModels] = useState(false);
  const [isLoadingPatterns, setIsLoadingPatterns] = useState(false);

  // State for results
  const [results, setResults] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  
  // State for 4-stage progress tracking
  const [progressStatus, setProgressStatus] = useState('idle');
  const [currentStage, setCurrentStage] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  
  // State for detailed breakdown visibility
  const [showDetailedBreakdown, setShowDetailedBreakdown] = useState(false);

  // Load available models and patterns on component mount
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

    const loadPatterns = async () => {
      setIsLoadingPatterns(true);
      try {
        const patterns = await getOrchestratorPatterns();
        setAvailablePatterns(patterns);
      } catch (err) {
        console.error('Pattern loading error:', err);
        // Use fallback patterns if API fails
        setAvailablePatterns([
          { name: 'gut', description: 'Gut-based intuitive analysis' },
          { name: 'confidence', description: 'Confidence scoring and agreement tracking' },
          { name: 'critique', description: 'Structured critique and revision process' },
          { name: 'fact_check', description: 'Rigorous fact-checking process' },
          { name: 'perspective', description: 'Multi-perspective analysis' },
          { name: 'scenario', description: 'Scenario-based analysis' }
        ]);
      } finally {
        setIsLoadingPatterns(false);
      }
    };

    loadModels();
    loadPatterns();
  }, []);

  // Handle model selection changes
  const handleModelToggle = (model) => {
    if (selectedModels.includes(model)) {
      // Remove from selection (unless it's the last one or the lead model)
      if (selectedModels.length > 1 && model !== leadModel) {
        setSelectedModels(selectedModels.filter((m) => m !== model));
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

  // Simulate 4-stage progress for Feather orchestration
  const simulateFeatherProgress = () => {
    const stages = [
      { stage: 1, message: 'Initial Analysis - Getting responses from all models...' },
      { stage: 2, message: 'Meta Analysis - Analyzing model responses...' },
      { stage: 3, message: 'Hyper Analysis - Synthesizing meta responses...' },
      { stage: 4, message: 'Ultra Analysis - Creating final synthesis...' }
    ];

    let stageIndex = 0;
    setProgressStatus('analyzing');
    setCurrentStage(1);
    setProgressMessage(stages[0].message);

    const progressInterval = setInterval(() => {
      stageIndex++;
      if (stageIndex < stages.length) {
        setCurrentStage(stages[stageIndex].stage);
        setProgressMessage(stages[stageIndex].message);
      } else {
        clearInterval(progressInterval);
        setProgressStatus('complete');
        setCurrentStage(4);
        setProgressMessage('4-stage Feather orchestration complete');
      }
    }, 2000); // Update every 2 seconds

    return progressInterval;
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
    setResults(null);

    try {
      let response;
      
      if (useFeatherOrchestration) {
        // Use sophisticated 4-stage Feather orchestration
        setProgressStatus('preparing');
        setProgressMessage('Preparing sophisticated 4-stage orchestration...');
        
        // Start progress simulation
        const progressInterval = simulateFeatherProgress();
        
        response = await processWithFeatherOrchestration({
          prompt,
          models: selectedModels,
          pattern: selectedPattern,
          ultraModel: leadModel || selectedModels[0],
          outputFormat: 'plain'
        });
        
        clearInterval(progressInterval);
        setProgressStatus('complete');
      } else {
        // Use legacy orchestration for backward compatibility
        setProgressStatus('analyzing');
        setProgressMessage('Processing with legacy orchestration...');
        
        response = await processWithOrchestrator({
          prompt,
          models: selectedModels,
          leadModel: leadModel || selectedModels[0],
          analysisType,
        });
        
        setProgressStatus('complete');
      }

      setResults(response);
    } catch (err) {
      setError(`Error processing request: ${err.message}`);
      setProgressStatus('error');
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
    <div className="max-w-6xl mx-auto p-4">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">UltrAI Sophisticated Orchestrator</h1>
        <p className="text-gray-600">Experience patent-protected 4-stage Feather analysis with advanced pattern selection</p>
      </div>

      {/* Orchestration Mode Toggle */}
      <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-blue-900">Orchestration Mode</h3>
            <p className="text-sm text-blue-700">
              {useFeatherOrchestration 
                ? "4-Stage Feather Analysis - Sophisticated patent-protected orchestration"
                : "Legacy Mode - Basic multi-model comparison"
              }
            </p>
          </div>
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={useFeatherOrchestration}
              onChange={(e) => setUseFeatherOrchestration(e.target.checked)}
              className="mr-2"
            />
            <span className="text-sm font-medium">Use Sophisticated Feather Orchestration</span>
          </label>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Progress display for sophisticated orchestration */}
      {isProcessing && useFeatherOrchestration && (
        <div className="mb-6">
          <AnalysisProgress
            status={progressStatus}
            currentStep={currentStage}
            totalSteps={4}
            statusMessage={progressMessage}
            error={error ? new Error(error) : undefined}
          />
        </div>
      )}

      {/* Input form */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Main form column */}
        <div className="lg:col-span-2">
          <form
            onSubmit={handleSubmit}
            className="bg-white rounded-lg shadow-md p-6"
          >
            {/* Prompt input */}
            <div className="mb-6">
              <label
                htmlFor="prompt"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Analysis Prompt
              </label>
              <textarea
                id="prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                rows={4}
                placeholder="Enter your prompt for sophisticated multi-LLM analysis..."
              ></textarea>
            </div>

            {/* Model selection */}
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-700 mb-3">
                Select AI Models ({selectedModels.length} selected)
              </h3>

              {isLoadingModels ? (
                <div className="flex items-center space-x-2 text-gray-500 p-4 border rounded-md">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  <span>Loading available models...</span>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {availableModels.map((model) => (
                    <div
                      key={model}
                      className={`border rounded-lg p-4 cursor-pointer transition-all ${
                        selectedModels.includes(model)
                          ? 'border-blue-500 bg-blue-50 shadow-sm'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => handleModelToggle(model)}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex items-start space-x-3">
                          <input
                            type="checkbox"
                            id={`model-${model}`}
                            checked={selectedModels.includes(model)}
                            onChange={() => handleModelToggle(model)}
                            className="mt-1"
                          />
                          <div>
                            <label htmlFor={`model-${model}`} className="font-medium text-sm cursor-pointer">
                              {formatModelName(model)}
                            </label>
                            {selectedModels.includes(model) && (
                              <div className="mt-2">
                                <label className="flex items-center text-xs text-gray-600">
                                  <input
                                    type="radio"
                                    id={`lead-${model}`}
                                    name="leadModel"
                                    checked={leadModel === model}
                                    onChange={() => handleLeadModelChange(model)}
                                    className="mr-1"
                                  />
                                  Ultra synthesis model
                                </label>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Legacy analysis type (only for non-Feather mode) */}
            {!useFeatherOrchestration && (
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-700 mb-3">
                  Legacy Analysis Type
                </h3>
                <div className="flex space-x-6">
                  <label className="flex items-center cursor-pointer">
                    <input
                      type="radio"
                      name="analysisType"
                      value="comparative"
                      checked={analysisType === 'comparative'}
                      onChange={() => setAnalysisType('comparative')}
                      className="mr-2"
                    />
                    <span>Comparative Analysis</span>
                  </label>
                  <label className="flex items-center cursor-pointer">
                    <input
                      type="radio"
                      name="analysisType"
                      value="factual"
                      checked={analysisType === 'factual'}
                      onChange={() => setAnalysisType('factual')}
                      className="mr-2"
                    />
                    <span>Factual Analysis</span>
                  </label>
                </div>
              </div>
            )}

            {/* Submit button */}
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={isProcessing}
                className={`px-6 py-3 rounded-lg font-medium transition-all ${
                  isProcessing
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : useFeatherOrchestration
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 shadow-lg'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {isProcessing 
                  ? (useFeatherOrchestration ? 'Running 4-Stage Analysis...' : 'Processing...')
                  : (useFeatherOrchestration ? 'Start Feather Orchestration' : 'Generate Response')
                }
              </button>
            </div>
          </form>
        </div>

        {/* Pattern selector sidebar */}
        <div className="lg:col-span-1">
          {useFeatherOrchestration && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold mb-4">Analysis Pattern</h3>
              {isLoadingPatterns ? (
                <div className="flex items-center space-x-2 text-gray-500 p-4">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Loading patterns...</span>
                </div>
              ) : (
                <AnalysisPatternSelector
                  patterns={availablePatterns.map(p => ({ id: p.name, name: p.name, description: p.description }))}
                  selectedPattern={selectedPattern}
                  onPatternChange={setSelectedPattern}
                  disabled={isProcessing}
                />
              )}
              
              <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                <p className="text-xs text-yellow-800">
                  <strong>Patent-Protected:</strong> Feather analysis patterns represent sophisticated intellectual property with 4-stage orchestration workflows.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Results */}
      {results && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-semibold">Analysis Results</h2>
            {results.processing_time && (
              <div className="text-sm text-gray-500">
                Processing time: {results.processing_time.toFixed(2)}s
              </div>
            )}
          </div>

          {/* Feather Orchestration Results */}
          {useFeatherOrchestration && results.status === 'success' && (
            <div className="space-y-6">
              {/* Ultra Synthesis™ - Primary Result (Prominent Display) */}
              {results.ultra_response && (
                <div className="mb-8">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                      Ultra Synthesis™
                    </h2>
                    <div className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                      Intelligence Multiplication Complete
                    </div>
                  </div>
                  
                  <div className="bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 p-8 rounded-xl border-2 border-gradient-to-r from-purple-200 to-blue-200 shadow-lg">
                    <div className="prose max-w-none">
                      <div 
                        data-testid="ultra-synthesis"
                        className="text-lg leading-relaxed text-gray-800 whitespace-pre-wrap font-medium"
                      >
                        {results.ultra_response}
                      </div>
                    </div>
                  </div>
                  
                  {/* Analysis Summary */}
                  <div className="mt-4 bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                    <div className="flex flex-wrap items-center justify-between text-sm text-gray-600">
                      <div className="flex items-center space-x-4">
                        <span className="font-medium">Pattern:</span>
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          {results.pattern_used || selectedPattern}
                        </span>
                      </div>
                      <div className="flex items-center space-x-4">
                        <span className="font-medium">Models Used:</span>
                        <span className="text-gray-700">
                          {results.models_used ? results.models_used.join(', ') : selectedModels.join(', ')}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Detailed Analysis Breakdown (Collapsible) */}
              <div className="border-t pt-6">
                <button
                  onClick={() => setShowDetailedBreakdown(!showDetailedBreakdown)}
                  className="flex items-center justify-between w-full text-left text-lg font-semibold text-gray-700 hover:text-gray-900 transition-colors"
                >
                  <span>Detailed Analysis Breakdown</span>
                  <svg 
                    className={`w-5 h-5 transform transition-transform ${showDetailedBreakdown ? 'rotate-180' : ''}`}
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                
                {showDetailedBreakdown && (
                  <div className="mt-6 space-y-6">
                    {/* Stage 1: Initial Responses */}
                    {results.initial_responses && Object.keys(results.initial_responses).length > 0 && (
                      <div>
                        <h3 className="text-lg font-semibold mb-3 flex items-center">
                          <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-sm mr-2">1</span>
                          Initial Analysis Responses
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {Object.entries(results.initial_responses).map(([model, response]) => (
                            <div key={model} className="bg-gray-50 p-4 rounded-lg border">
                              <h4 className="font-medium mb-2 flex items-center">
                                {formatModelName(model)}
                                {leadModel && leadModel.includes(model) && (
                                  <span className="ml-2 text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">
                                    Ultra Model
                                  </span>
                                )}
                              </h4>
                              <p className="text-sm whitespace-pre-wrap text-gray-700">{response}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Stage 2: Meta Analysis */}
                    {results.meta_responses && Object.keys(results.meta_responses).length > 0 && (
                      <div>
                        <h3 className="text-lg font-semibold mb-3 flex items-center">
                          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm mr-2">2</span>
                          Meta Analysis
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {Object.entries(results.meta_responses).map(([model, response]) => (
                            <div key={model} className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                              <h4 className="font-medium mb-2">{formatModelName(model)}</h4>
                              <p className="text-sm whitespace-pre-wrap text-gray-700">{response}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Stage 3: Hyper Analysis */}
                    {results.hyper_responses && Object.keys(results.hyper_responses).length > 0 && (
                      <div>
                        <h3 className="text-lg font-semibold mb-3 flex items-center">
                          <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-sm mr-2">3</span>
                          Hyper Synthesis
                        </h3>
                        <div className="space-y-4">
                          {Object.entries(results.hyper_responses).map(([model, response]) => (
                            <div key={model} className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                              <h4 className="font-medium mb-2">{formatModelName(model)}</h4>
                              <p className="text-sm whitespace-pre-wrap text-gray-700">{response}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Legacy Results Display */}
          {!useFeatherOrchestration && (
            <div className="space-y-6">
              {/* Initial responses */}
              {results.initial_responses && results.initial_responses.length > 0 && (
                <div>
                  <h3 className="text-lg font-medium mb-3">Model Responses</h3>
                  <div className="space-y-4">
                    {results.initial_responses.map((response, index) => (
                      <div key={index} className="bg-gray-50 p-4 rounded border">
                        <h4 className="font-medium mb-2">
                          {response.model} ({response.provider})
                          {leadModel === response.model && (
                            <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                              Primary
                            </span>
                          )}
                        </h4>
                        <p className="whitespace-pre-wrap text-sm">{response.response}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Synthesis */}
              {results.synthesis && (
                <div>
                  <h3 className="text-lg font-medium mb-3">Synthesized Response</h3>
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

          {/* Error handling */}
          {results.status === 'error' && (
            <div className="bg-red-50 p-4 rounded-lg border border-red-200">
              <h3 className="text-lg font-semibold text-red-800 mb-2">Error</h3>
              <p className="text-red-700">{results.error || 'An unknown error occurred'}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default OrchestratorInterface;
