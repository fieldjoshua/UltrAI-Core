import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { analyzePrompt, fetchAvailableModels } from '../services/api';
import { CheckCircle, ChevronRight, ChevronLeft, Loader2 } from 'lucide-react';

type Step = 'intro' | 'prompt' | 'models' | 'pattern' | 'results';

// Analysis pattern interface
interface AnalysisPattern {
  key: string;
  name: string;
  description: string;
}

// Add interface for model responses
interface ModelResponse {
  model: string;
  response: string;
}

const SimpleAnalysis: React.FC = () => {
  // Basic state
  const [prompt, setPrompt] = useState('');
  const [output, setOutput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<Step>('intro');

  // Models state
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [selectedModels, setSelectedModels] = useState<string[]>(['gpt4o']);
  const [primaryModel, setPrimaryModel] = useState<string>('gpt4o');

  // Analysis patterns from documentation
  const [patterns, setPatterns] = useState<AnalysisPattern[]>([
    {
      key: 'gut',
      name: 'Gut Check Analysis',
      description: 'Rapid evaluation of different perspectives to identify the most likely correct answer'
    },
    {
      key: 'confidence',
      name: 'Confidence Analysis',
      description: 'Evaluates the strength of each model response with confidence scoring'
    },
    {
      key: 'critique',
      name: 'Critique Analysis',
      description: 'Models critically evaluate each other\'s reasoning and answers'
    },
    {
      key: 'fact_check',
      name: 'Fact Check Analysis',
      description: 'Verifies factual accuracy and cites sources for claims'
    },
    {
      key: 'perspective',
      name: 'Perspective Analysis',
      description: 'Examines a question from multiple analytical perspectives'
    },
    {
      key: 'scenario',
      name: 'Scenario Analysis',
      description: 'Explores potential future outcomes and alternative possibilities'
    },
    {
      key: 'stakeholder',
      name: 'Stakeholder Vision',
      description: 'Analyzes from multiple stakeholder perspectives to reveal diverse interests and needs'
    },
    {
      key: 'systems',
      name: 'Systems Mapper',
      description: 'Maps complex system dynamics with feedback loops and leverage points'
    },
    {
      key: 'time',
      name: 'Time Horizon',
      description: 'Analyzes across multiple time frames to balance short and long-term considerations'
    },
    {
      key: 'innovation',
      name: 'Innovation Bridge',
      description: 'Uses cross-domain analogies to discover non-obvious patterns and solutions'
    }
  ]);

  const [selectedPattern, setSelectedPattern] = useState<string>('gut');
  const [modelsLoading, setModelsLoading] = useState(false);

  // Add state for individual model responses
  const [modelResponses, setModelResponses] = useState<ModelResponse[]>([]);

  // Fetch available models
  useEffect(() => {
    const getModels = async () => {
      setModelsLoading(true);
      try {
        const models = await fetchAvailableModels();
        setAvailableModels(models);

        // Set default selections if available in the fetched models
        if (models.includes('gpt4o')) {
          setSelectedModels(['gpt4o']);
          setPrimaryModel('gpt4o');
        } else if (models.length > 0) {
          setSelectedModels([models[0]]);
          setPrimaryModel(models[0]);
        }
      } catch (err) {
        console.error('Failed to fetch models:', err);
        // Fallback to some default models
        setAvailableModels(['gpt4o', 'claude37', 'gemini15', 'llama3']);
      } finally {
        setModelsLoading(false);
      }
    };

    getModels();
  }, []);

  // Handle model selection toggle
  const toggleModel = (model: string) => {
    if (selectedModels.includes(model)) {
      // Don't allow deselecting the last model
      if (selectedModels.length > 1) {
        setSelectedModels(selectedModels.filter(m => m !== model));

        // If removing the primary model, set a new one
        if (primaryModel === model) {
          setPrimaryModel(selectedModels.filter(m => m !== model)[0]);
        }
      }
    } else {
      setSelectedModels([...selectedModels, model]);
    }
  };

  // Set primary model
  const handlePrimaryModelChange = (model: string) => {
    // Add to selected models if not already selected
    if (!selectedModels.includes(model)) {
      setSelectedModels([...selectedModels, model]);
    }
    setPrimaryModel(model);
  };

  // Handle pattern selection
  const handlePatternChange = (pattern: string) => {
    setSelectedPattern(pattern);
  };

  // Handle form submission
  const handleSubmit = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    if (selectedModels.length === 0) {
      setError('Please select at least one model');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Prepare analysis payload
      const payload = {
        prompt,
        selected_models: selectedModels,
        ultra_model: primaryModel,
        pattern: selectedPattern,
        options: {},
        output_format: 'txt',
        userId: 'user-placeholder',
      };

      console.log('Sending analysis request:', payload);
      const result = await analyzePrompt(payload);
      setOutput(result.ultra_response);

      // Handle individual model responses
      const individualResponses: ModelResponse[] = [];

      // If the API returns individual model responses, use those
      if (result.model_responses) {
        for (const model in result.model_responses) {
          individualResponses.push({
            model,
            response: result.model_responses[model]
          });
        }
      } else {
        // Mock responses for demonstration
        for (const model of selectedModels) {
          individualResponses.push({
            model,
            response: result.ultra_response
              ? `${model}'s response (simulated): ${result.ultra_response.substring(0, 100)}...`
              : `No response from ${model}`
          });
        }
      }

      setModelResponses(individualResponses);
      setCurrentStep('results');
    } catch (err: any) {
      setError(err.message || 'An error occurred during analysis');
      console.error('Analysis error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle navigation between steps
  const goToNextStep = () => {
    if (currentStep === 'intro') setCurrentStep('prompt');
    else if (currentStep === 'prompt') setCurrentStep('models');
    else if (currentStep === 'models') setCurrentStep('pattern');
    else if (currentStep === 'pattern') {
      // Run the analysis when going to results
      handleSubmit();
    }
  };

  const goToPreviousStep = () => {
    if (currentStep === 'pattern') setCurrentStep('models');
    else if (currentStep === 'models') setCurrentStep('prompt');
    else if (currentStep === 'prompt') setCurrentStep('intro');
    else if (currentStep === 'results') setCurrentStep('pattern');
  };

  // Validate if we can proceed to the next step
  const canProceed = () => {
    if (currentStep === 'prompt' && !prompt.trim()) return false;
    if (currentStep === 'models' && selectedModels.length === 0) return false;
    return true;
  };

  // Render current step content
  const renderStepContent = () => {
    switch (currentStep) {
      case 'intro':
        return (
          <div className="text-center p-6">
            <h2 className="text-2xl font-bold mb-4">Welcome to UltrAI Analysis</h2>
            <p className="mb-6 text-gray-600">
              This tool helps you analyze text using multiple AI models working together.
              Follow the steps to create your analysis.
            </p>
            <div className="flex justify-center">
              <button
                onClick={goToNextStep}
                className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md flex items-center"
              >
                Get Started
                <ChevronRight className="ml-2" size={16} />
              </button>
            </div>
          </div>
        );

      case 'prompt':
        return (
          <div className="p-4">
            <h2 className="text-xl font-semibold mb-4">Step 1: Enter Your Prompt</h2>
            <p className="mb-4 text-gray-600">
              Write what you'd like to analyze. Be as specific as possible for best results.
            </p>
            <div className="mb-4">
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                rows={5}
                placeholder="What would you like to analyze?"
              />
            </div>
          </div>
        );

      case 'models':
        return (
          <div className="p-4">
            <h2 className="text-xl font-semibold mb-4">Step 2: Select AI Models</h2>
            <p className="mb-4 text-gray-600">
              Choose which AI models to use for your analysis. Each model brings unique strengths.
            </p>

            {modelsLoading ? (
              <div className="flex justify-center items-center py-8">
                <Loader2 className="animate-spin mr-2" />
                <span>Loading available models...</span>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {availableModels.map(model => (
                    <div
                      key={model}
                      className={`border p-3 rounded-md cursor-pointer ${
                        selectedModels.includes(model) ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                      }`}
                      onClick={() => toggleModel(model)}
                    >
                      <div className="flex justify-between items-center">
                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            checked={selectedModels.includes(model)}
                            onChange={() => toggleModel(model)}
                            className="mr-2"
                            aria-label={`Select ${model}`}
                            title={`Select ${model}`}
                          />
                          <span>{model}</span>
                        </div>
                        {selectedModels.includes(model) && (
                          <div className="flex items-center">
                            <input
                              type="radio"
                              name="primaryModel"
                              checked={primaryModel === model}
                              onChange={() => handlePrimaryModelChange(model)}
                              className="mr-1"
                              aria-label={`Set ${model} as primary`}
                              title={`Set ${model} as primary`}
                            />
                            <label className="text-sm text-gray-600">Primary</label>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                <div className="bg-yellow-50 border border-yellow-200 p-3 rounded-md">
                  <p className="text-sm text-yellow-800">
                    <strong>Selected Models:</strong> {selectedModels.join(', ')}
                  </p>
                  <p className="text-sm text-yellow-800">
                    <strong>Primary Model:</strong> {primaryModel}
                  </p>
                </div>
              </div>
            )}
          </div>
        );

      case 'pattern':
        return (
          <div className="p-4">
            <h2 className="text-xl font-semibold mb-4">Step 3: Select Analysis Pattern</h2>
            <p className="mb-4 text-gray-600">
              Choose how the models should collaborate on your analysis. Each pattern represents a different approach to intelligence multiplication.
            </p>

            <div className="space-y-3">
              {patterns.map(pattern => (
                <div
                  key={pattern.key}
                  className={`border p-3 rounded-md cursor-pointer ${
                    selectedPattern === pattern.key ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                  }`}
                  onClick={() => handlePatternChange(pattern.key)}
                >
                  <div className="flex items-center">
                    <input
                      type="radio"
                      name="pattern"
                      checked={selectedPattern === pattern.key}
                      onChange={() => handlePatternChange(pattern.key)}
                      className="mr-2"
                      aria-label={`Select ${pattern.name} pattern`}
                      title={`Select ${pattern.name} pattern`}
                    />
                    <div>
                      <span className="font-medium">{pattern.name}</span>
                      <p className="text-sm text-gray-600">
                        {pattern.description}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      case 'results':
        return (
          <div className="p-4">
            <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>
            <div className="flex items-center mb-4">
              <span className="text-sm bg-gray-200 rounded px-2 py-1 mr-2">Prompt</span>
              <p className="text-gray-700">{prompt}</p>
            </div>

            {/* Combined response */}
            <div className="mb-6">
              <h3 className="text-lg font-medium mb-2">Ultra Combined Response</h3>
              <div className="bg-gray-50 p-4 rounded border border-gray-200 whitespace-pre-wrap">
                {output}
              </div>
            </div>

            {/* Individual model responses */}
            <div className="mb-6">
              <h3 className="text-lg font-medium mb-2">Individual Model Responses</h3>
              <div className="space-y-4">
                {modelResponses.map((response, index) => (
                  <div key={index} className="border rounded-md overflow-hidden">
                    <div className="bg-gray-100 px-4 py-2 font-medium flex justify-between items-center">
                      <span>{response.model}</span>
                      {response.model === primaryModel && (
                        <span className="text-xs bg-blue-100 text-blue-700 rounded px-2 py-1">Primary</span>
                      )}
                    </div>
                    <div className="p-4 whitespace-pre-wrap">
                      {response.response}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-4 flex justify-between">
              <button
                onClick={() => setCurrentStep('prompt')}
                className="bg-gray-200 hover:bg-gray-300 text-gray-700 py-2 px-4 rounded-md"
              >
                New Analysis
              </button>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">UltrAI Analysis</h1>

      {/* Step progress */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          {['intro', 'prompt', 'models', 'pattern', 'results'].map((step, index) => (
            <div key={step} className="flex items-center">
              <div className={`
                flex items-center justify-center w-8 h-8 rounded-full
                ${currentStep === step ? 'bg-blue-600 text-white' :
                  (currentStep === 'results' ||
                   (index < ['intro', 'prompt', 'models', 'pattern', 'results'].indexOf(currentStep))
                  ) ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-600'}
              `}>
                {(currentStep === 'results' ||
                  (index < ['intro', 'prompt', 'models', 'pattern', 'results'].indexOf(currentStep))
                ) ? <CheckCircle size={16} /> : index + 1}
              </div>
              {index < 4 && (
                <div className={`h-1 w-10 ${
                  index < ['intro', 'prompt', 'models', 'pattern'].indexOf(currentStep)
                    ? 'bg-green-500' : 'bg-gray-200'
                }`} />
              )}
            </div>
          ))}
        </div>
        <div className="flex justify-between text-xs text-gray-600">
          <span>Start</span>
          <span>Prompt</span>
          <span>Models</span>
          <span>Pattern</span>
          <span>Results</span>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-md border border-red-200">
          {error}
        </div>
      )}

      {/* Main content */}
      <div className="bg-white shadow-md rounded-lg p-6 mb-8">
        {renderStepContent()}
      </div>

      {/* Navigation buttons */}
      {currentStep !== 'intro' && currentStep !== 'results' && (
        <div className="flex justify-between mt-4">
          <button
            onClick={goToPreviousStep}
            className="bg-gray-200 hover:bg-gray-300 text-gray-700 py-2 px-4 rounded-md flex items-center"
          >
            <ChevronLeft className="mr-2" size={16} />
            Back
          </button>

          <button
            onClick={goToNextStep}
            disabled={!canProceed() || isLoading}
            className={`py-2 px-4 rounded-md flex items-center ${
              !canProceed() || isLoading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {isLoading ? (
              <>
                <Loader2 className="animate-spin mr-2" size={16} />
                Processing...
              </>
            ) : (
              <>
                {currentStep === 'pattern' ? 'Run Analysis' : 'Next'}
                <ChevronRight className="ml-2" size={16} />
              </>
            )}
          </button>
        </div>
      )}

      {currentStep === 'intro' && (
        <div className="mt-8 text-center text-gray-600">
          <p>For document management, visit the{' '}
            <Link to="/documents" className="text-blue-600 underline">Documents page</Link>.
          </p>
        </div>
      )}
    </div>
  );
};

export default SimpleAnalysis;
