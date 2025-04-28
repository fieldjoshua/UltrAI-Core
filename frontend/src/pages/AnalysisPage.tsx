import React, { useState, useEffect } from 'react';
import { PromptInput } from '../components/PromptInput';
import { LLMSelector } from '../components/LLMSelector';
import { AnalysisPatternSelector } from '../components/AnalysisPatternSelector';
import { AnalysisResults } from '../components/AnalysisResults';
import { ExportButton } from '../components/ExportButton';
import { AnalysisHistory } from '../components/AnalysisHistory';
import { HelpModal } from '../components/HelpModal';
import { Tooltip } from '../components/ui/tooltip';
import { analysisService } from '../services/analysisService';
import { historyService } from '../services/historyService';
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts';
import {
  AnalysisRequest,
  AnalysisResponse,
  AnalysisProgress,
} from '../types/analysis';

// Mock data for demonstration
const availableModels = [
  {
    id: 'gpt-4',
    name: 'GPT-4',
    description: "OpenAI's most advanced model",
  },
  {
    id: 'claude-3',
    name: 'Claude 3',
    description: "Anthropic's latest model",
  },
  {
    id: 'llama-2',
    name: 'Llama 2',
    description: "Meta's open-source model",
  },
];

const analysisPatterns = [
  {
    id: 'basic',
    name: 'Basic Analysis',
    description: 'Standard analysis of the prompt',
  },
  {
    id: 'detailed',
    name: 'Detailed Analysis',
    description: 'In-depth analysis with additional insights',
  },
  {
    id: 'comparative',
    name: 'Comparative Analysis',
    description: 'Compare responses across models',
  },
];

export const AnalysisPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [selectedPattern, setSelectedPattern] = useState('basic');
  const [results, setResults] = useState<AnalysisResponse['results'] | null>(
    null
  );
  const [currentAnalysisId, setCurrentAnalysisId] = useState<string | null>(
    null
  );
  const [progress, setProgress] = useState<AnalysisProgress | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [showHistory, setShowHistory] = useState(false);
  const [showHelp, setShowHelp] = useState(false);

  const shortcuts = [
    {
      key: 'h',
      ctrlKey: true,
      description: 'Toggle help modal',
      handler: () => setShowHelp(!showHelp),
    },
    {
      key: 't',
      ctrlKey: true,
      description: 'Toggle history view',
      handler: () => setShowHistory(!showHistory),
    },
    {
      key: 'Escape',
      description: 'Close modal or clear selection',
      handler: () => {
        setShowHelp(false);
        setShowHistory(false);
      },
    },
  ];

  useKeyboardShortcuts(shortcuts);

  useEffect(() => {
    let progressInterval: NodeJS.Timeout;

    const checkProgress = async () => {
      if (!currentAnalysisId) return;

      try {
        const progressResponse =
          await analysisService.getAnalysisProgress(currentAnalysisId);
        setProgress(progressResponse.progress);

        if (progressResponse.progress.status === 'completed') {
          const resultsResponse =
            await analysisService.getAnalysisResults(currentAnalysisId);
          setResults(resultsResponse.results);
          setIsLoading(false);
          clearInterval(progressInterval);

          // Save to history
          historyService.addToHistory({
            prompt: currentPrompt,
            selectedModels,
            pattern: selectedPattern,
            results: resultsResponse.results,
          });
        } else if (progressResponse.progress.status === 'failed') {
          setError(progressResponse.progress.message || 'Analysis failed');
          setIsLoading(false);
          clearInterval(progressInterval);
        }
      } catch (error) {
        console.error('Progress check error:', error);
        if (retryCount < 3) {
          setRetryCount(prev => prev + 1);
        } else {
          setError('Failed to check analysis progress');
          setIsLoading(false);
          clearInterval(progressInterval);
        }
      }
    };

    if (currentAnalysisId && isLoading) {
      progressInterval = setInterval(checkProgress, 2000);
    }

    return () => {
      if (progressInterval) {
        clearInterval(progressInterval);
      }
    };
  }, [
    currentAnalysisId,
    isLoading,
    retryCount,
    selectedModels,
    selectedPattern,
  ]);

  const [currentPrompt, setCurrentPrompt] = useState('');

  const handleSubmit = async (prompt: string) => {
    if (selectedModels.length === 0) {
      setError('Please select at least one LLM for analysis');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResults(null);
    setProgress(null);
    setRetryCount(0);
    setCurrentPrompt(prompt);

    try {
      const request: AnalysisRequest = {
        prompt,
        selected_models: selectedModels,
        ultra_model: 'ultra-default',
        pattern: selectedPattern,
      };

      const response = await analysisService.analyzePrompt(request);
      setCurrentAnalysisId(response.analysis_id);
    } catch (error) {
      console.error('Analysis error:', error);
      setError(
        error instanceof Error ? error.message : 'Failed to analyze prompt'
      );
      setIsLoading(false);
    }
  };

  const handleSelectHistory = (entry: {
    prompt: string;
    selectedModels: string[];
    pattern: string;
    results: AnalysisResponse['results'];
  }) => {
    setCurrentPrompt(entry.prompt);
    setSelectedModels(entry.selectedModels);
    setSelectedPattern(entry.pattern);
    setResults(entry.results);
    setShowHistory(false);
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">LLM Analysis Interface</h1>
        <div className="flex items-center space-x-4">
          <Tooltip content="View keyboard shortcuts and help">
            <HelpModal shortcuts={shortcuts} />
          </Tooltip>
          <Tooltip content="View analysis history">
            <Button
              variant="outline"
              onClick={() => setShowHistory(!showHistory)}
            >
              {showHistory ? 'Hide History' : 'Show History'}
            </Button>
          </Tooltip>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="space-y-6">
        {showHistory ? (
          <AnalysisHistory onSelectHistory={handleSelectHistory} />
        ) : (
          <>
            <Tooltip content="Enter your prompt and press Enter to analyze">
              <PromptInput onSubmit={handleSubmit} isLoading={isLoading} />
            </Tooltip>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Tooltip content="Select one or more LLMs to analyze your prompt">
                <LLMSelector
                  options={availableModels}
                  selectedModels={selectedModels}
                  onSelectionChange={setSelectedModels}
                  disabled={isLoading}
                />
              </Tooltip>

              <Tooltip content="Choose an analysis pattern to guide the LLM responses">
                <AnalysisPatternSelector
                  patterns={analysisPatterns}
                  selectedPattern={selectedPattern}
                  onPatternChange={setSelectedPattern}
                  disabled={isLoading}
                />
              </Tooltip>
            </div>

            {progress && (
              <div className="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded">
                <p className="font-medium">
                  Analysis Progress: {progress.stage}
                </p>
                <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
                  <div
                    className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                    style={{ width: `${progress.progress}%` }}
                  ></div>
                </div>
                {progress.message && (
                  <p className="mt-2 text-sm">{progress.message}</p>
                )}
              </div>
            )}

            {results && (
              <>
                <div className="flex justify-end mb-4">
                  <Tooltip content="Export results in various formats">
                    <ExportButton results={results} disabled={isLoading} />
                  </Tooltip>
                </div>
                <AnalysisResults
                  results={results.model_responses}
                  isLoading={isLoading}
                />
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
};
