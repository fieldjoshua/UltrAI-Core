import React, { useState, useEffect } from 'react';
import { analyzePrompt, fetchAvailableModels } from '../services/api';
import { 
  Brain, 
  Loader2, 
  CheckCircle, 
  AlertCircle, 
  Copy, 
  RefreshCw,
  Zap,
  Users,
  Eye
} from 'lucide-react';

interface ModelResponse {
  model: string;
  response: string;
  status: string;
}

interface AnalysisResults {
  status: string;
  message: string;
  model_responses: Record<string, ModelResponse>;
  combined_response: string;
  timestamp: string;
  processing_time?: number;
}

const MultimodalAnalysis: React.FC = () => {
  const [query, setQuery] = useState('');
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [selectedModels, setSelectedModels] = useState<string[]>(['gpt-4', 'claude-3-sonnet', 'gemini-pro']);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResults | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'individual' | 'combined'>('individual');

  // Fetch available models on component mount
  useEffect(() => {
    const loadModels = async () => {
      try {
        const models = await fetchAvailableModels();
        setAvailableModels(models);
        console.log('Loaded models:', models);
      } catch (error) {
        console.error('Failed to load models:', error);
        // Use fallback models
        setAvailableModels(['gpt-4', 'gpt-4-turbo', 'claude-3-sonnet', 'claude-3-haiku', 'gemini-pro']);
      }
    };
    loadModels();
  }, []);

  const handleModelToggle = (modelName: string) => {
    setSelectedModels(prev => {
      if (prev.includes(modelName)) {
        return prev.filter(m => m !== modelName);
      } else {
        return [...prev, modelName];
      }
    });
  };

  const runAnalysis = async () => {
    if (!query.trim()) {
      setError('Please enter a query to analyze');
      return;
    }

    if (selectedModels.length === 0) {
      setError('Please select at least one model');
      return;
    }

    setIsLoading(true);
    setError(null);
    setAnalysisResults(null);

    try {
      const payload = {
        prompt: query,
        selected_models: selectedModels,
        pattern: 'comprehensive',
        ultra_model: selectedModels[0],
        output_format: 'txt',
        options: {}
      };

      console.log('Starting multimodal analysis with models:', selectedModels);
      
      const results = await analyzePrompt(payload);
      setAnalysisResults(results);
      
      console.log('Analysis completed:', results);
    } catch (error: any) {
      console.error('Analysis failed:', error);
      setError(error.message || 'Analysis failed');
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // You could add a toast notification here
  };

  const getProviderIcon = (modelName: string) => {
    if (modelName.includes('gpt')) return '🧠';
    if (modelName.includes('claude')) return '🤖';
    if (modelName.includes('gemini')) return '💎';
    return '🔬';
  };

  const getProviderColor = (modelName: string) => {
    if (modelName.includes('gpt')) return 'border-green-500 bg-green-50';
    if (modelName.includes('claude')) return 'border-blue-500 bg-blue-50';
    if (modelName.includes('gemini')) return 'border-purple-500 bg-purple-50';
    return 'border-gray-500 bg-gray-50';
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center justify-center gap-2">
          <Brain className="w-8 h-8 text-blue-600" />
          Multimodal AI Analysis
        </h1>
        <p className="text-gray-600">
          Compare responses from multiple AI models simultaneously
        </p>
      </div>

      {/* Query Input */}
      <div className="bg-white rounded-lg shadow-sm border p-6 space-y-4">
        <label className="block text-sm font-medium text-gray-700">
          Enter your query or question:
        </label>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="What would you like to analyze? (e.g., 'Explain quantum computing', 'Analyze this business proposal', 'Compare renewable energy sources')"
          className="w-full h-32 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
        />
        
        {/* Model Selection */}
        <div className="space-y-3">
          <label className="block text-sm font-medium text-gray-700">
            Select Models ({selectedModels.length} selected):
          </label>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
            {availableModels.map((model) => (
              <button
                key={model}
                onClick={() => handleModelToggle(model)}
                className={`p-3 rounded-lg border-2 transition-all duration-200 text-sm font-medium ${
                  selectedModels.includes(model)
                    ? `${getProviderColor(model)} border-opacity-100`
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{getProviderIcon(model)}</span>
                  <span className="truncate">{model}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Analysis Button */}
        <button
          onClick={runAnalysis}
          disabled={isLoading || !query.trim() || selectedModels.length === 0}
          className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700 transition-colors duration-200 flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Analyzing with {selectedModels.length} models...
            </>
          ) : (
            <>
              <Zap className="w-5 h-5" />
              Run Multimodal Analysis
            </>
          )}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <span className="text-red-800">{error}</span>
        </div>
      )}

      {/* Results Display */}
      {analysisResults && (
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          {/* Results Header */}
          <div className="bg-green-50 border-b p-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="font-medium text-green-800">
                Analysis Complete
              </span>
              {analysisResults.processing_time && (
                <span className="text-sm text-green-600">
                  ({analysisResults.processing_time.toFixed(2)}s)
                </span>
              )}
            </div>
            <div className="text-sm text-green-600">
              {Object.keys(analysisResults.model_responses).length} models responded
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="border-b">
            <nav className="flex">
              <button
                onClick={() => setActiveTab('individual')}
                className={`px-6 py-3 text-sm font-medium border-b-2 ${
                  activeTab === 'individual'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Users className="w-4 h-4 inline mr-2" />
                Individual Responses
              </button>
              <button
                onClick={() => setActiveTab('combined')}
                className={`px-6 py-3 text-sm font-medium border-b-2 ${
                  activeTab === 'combined'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Eye className="w-4 h-4 inline mr-2" />
                Combined Analysis
              </button>
            </nav>
          </div>

          {/* Results Content */}
          <div className="p-6">
            {activeTab === 'individual' && (
              <div className="space-y-6">
                {Object.entries(analysisResults.model_responses).map(([modelName, response]) => (
                  <div key={modelName} className={`border rounded-lg p-4 ${getProviderColor(modelName)}`}>
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{getProviderIcon(modelName)}</span>
                        <span className="font-medium text-gray-900">{modelName}</span>
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          response.status === 'success' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {response.status}
                        </span>
                      </div>
                      <button
                        onClick={() => copyToClipboard(response.response)}
                        className="p-1 hover:bg-white rounded"
                        title="Copy response"
                      >
                        <Copy className="w-4 h-4 text-gray-600" />
                      </button>
                    </div>
                    <div className="bg-white rounded p-3 text-sm text-gray-800 whitespace-pre-wrap">
                      {response.response}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'combined' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium text-gray-900">
                    Combined Analysis Results
                  </h3>
                  <button
                    onClick={() => copyToClipboard(analysisResults.combined_response)}
                    className="flex items-center gap-2 px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
                  >
                    <Copy className="w-4 h-4" />
                    Copy All
                  </button>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-800 whitespace-pre-wrap max-h-96 overflow-y-auto">
                  {analysisResults.combined_response}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Info Footer */}
      <div className="text-center text-sm text-gray-500">
        Powered by UltraAI Core • Real-time multimodal analysis with GPT-4, Claude, and Gemini
      </div>
    </div>
  );
};

export default MultimodalAnalysis;