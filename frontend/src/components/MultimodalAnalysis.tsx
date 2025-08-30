import React, { useState, useEffect } from 'react';
import { analyzePrompt, fetchAvailableModels } from '../services/api';
import {
  Loader2,
  CheckCircle,
  AlertCircle,
  Copy,
  RefreshCw,
  Zap,
  Users,
  Eye
} from 'lucide-react';
import CyberpunkCity from './CyberpunkCity';
import FullCyberCity from './FullCyberCity';

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
  const [selectedModels, setSelectedModels] = useState<string[]>(['gpt-4', 'claude-3-sonnet', 'meta-llama/Meta-Llama-3-8B-Instruct']);
  const [analysisResults, setAnalysisResults] = useState<any>(null);
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
    if (modelName.includes('llama')) return '🦙';
    if (modelName.includes('mistral')) return '🌪️';
    if (modelName.includes('qwen')) return '🏮';
    if (modelName.includes('/')) return '🤗'; // HuggingFace models
    return '🔬';
  };

  const getProviderColor = (modelName: string) => {
    if (modelName.includes('gpt')) return 'border-green-500 bg-green-50';
    if (modelName.includes('claude')) return 'border-blue-500 bg-blue-50';
    if (modelName.includes('gemini')) return 'border-purple-500 bg-purple-50';
    if (modelName.includes('llama')) return 'border-orange-500 bg-orange-50';
    if (modelName.includes('mistral')) return 'border-indigo-500 bg-indigo-50';
    if (modelName.includes('qwen')) return 'border-red-500 bg-red-50';
    if (modelName.includes('/')) return 'border-yellow-500 bg-yellow-50'; // HuggingFace models
    return 'border-gray-500 bg-gray-50';
  };

  return (
    <div className="site-background min-h-screen">
      <CyberpunkCity />
      {/* Full PNG preview */}
      <FullCyberCity height={260} maxWidth={1100} />
      <div className="max-w-6xl mx-auto p-6 flex flex-row gap-8">
        {/* Left Panel: Inputs and Controls */}
        <div className="w-full max-w-xs bg-black/70 rounded-xl p-6 flex flex-col gap-6 neon-panel border border-cyan-400 shadow-xl">
          <div>
            <label className="block text-cyan-200 font-semibold mb-2">Query</label>
            <textarea
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="What would you like to analyze? (e.g. Compare AI models on this prompt...)"
              className="w-full h-28 p-2 rounded bg-gray-900 text-cyan-100 border border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-400 resize-none"
            />
          </div>
          <div>
            <label className="block text-cyan-200 font-semibold mb-2">Select Models</label>
            <div className="flex flex-col gap-2 max-h-40 overflow-y-auto">
              {availableModels.map(model => (
                <label key={model} className="flex items-center gap-2 text-cyan-100 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedModels.includes(model)}
                    onChange={() => handleModelToggle(model)}
                    className="accent-cyan-400"
                  />
                  <span className="text-sm">{getProviderIcon(model)} {model}</span>
                </label>
              ))}
            </div>
          </div>
          <button
            onClick={runAnalysis}
            disabled={isLoading}
            className="neon-generate-btn mt-2 py-3 rounded-lg font-bold text-lg bg-cyan-500 text-black shadow-lg hover:bg-cyan-400 transition disabled:opacity-60"
          >
            {isLoading ? (
              <span className="flex items-center gap-2"><Loader2 className="animate-spin w-5 h-5" /> Generating...</span>
            ) : (
              <span className="flex items-center gap-2"><Zap className="w-5 h-5" /> Generate</span>
            )}
          </button>
        </div>
        {/* Main Content: Results and Info */}
        <div className="flex-1 space-y-6">
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
                      ({typeof analysisResults.processing_time === 'number' 
                        ? analysisResults.processing_time.toFixed(2) 
                        : typeof analysisResults.processing_time === 'string'
                          ? analysisResults.processing_time
                          : JSON.stringify(analysisResults.processing_time)}s)
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
                    {Object.entries(analysisResults.model_responses as any).map(([modelName, response]: any[]) => (
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
                          {typeof response.response === 'string' 
                            ? response.response 
                            : typeof response.response === 'object' && response.response !== null
                              ? JSON.stringify(response.response, null, 2)
                              : String(response.response || 'No response available')}
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
                      {typeof analysisResults.combined_response === 'string' 
                        ? analysisResults.combined_response 
                        : typeof analysisResults.combined_response === 'object' && analysisResults.combined_response !== null
                          ? JSON.stringify(analysisResults.combined_response, null, 2)
                          : String(analysisResults.combined_response || 'No combined response available')}
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
      </div>
    </div>
  );
};

export default MultimodalAnalysis;