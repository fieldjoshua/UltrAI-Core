import React, { useState, useEffect } from 'react';
import EnhancedPromptInput from './atoms/EnhancedPromptInput';
import ModelSelector from './atoms/ModelSelector';
import EnhancedPatternSelector from './atoms/EnhancedPatternSelector';
import ResultsDisplay from './atoms/ResultsDisplay';
import AnalysisProgress from './atoms/AnalysisProgress';
import { Card } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertTitle, AlertDescription } from './ui/alert';
import { AlertCircle } from 'lucide-react';

// Types from components
import type { AnalysisOptions } from './atoms/EnhancedPromptInput';
import type { Model } from './atoms/ModelSelector';
import type { AnalysisPattern } from './atoms/EnhancedPatternSelector';
import type { AnalysisResult } from './atoms/ResultsDisplay';

// Mock API functions - replace with actual API calls
const fetchModels = async (): Promise<Model[]> => {
  // Simulated API delay
  await new Promise((resolve) => setTimeout(resolve, 1000));

  return [
    {
      id: 'gpt4o',
      name: 'GPT-4o',
      provider: 'OpenAI',
      description: 'Most capable language model from OpenAI',
      capabilities: ['Text generation', 'Reasoning', 'Creative writing'],
      isAvailable: true,
    },
    {
      id: 'gpt4',
      name: 'GPT-4',
      provider: 'OpenAI',
      description: 'Powerful language model with strong reasoning',
      capabilities: ['Text generation', 'Reasoning'],
      isAvailable: true,
    },
    {
      id: 'claude3opus',
      name: 'Claude 3 Opus',
      provider: 'Anthropic',
      description: "Anthropic's most powerful model",
      capabilities: ['Text generation', 'Reasoning', 'Long context'],
      isAvailable: true,
    },
    {
      id: 'claude3sonnet',
      name: 'Claude 3 Sonnet',
      provider: 'Anthropic',
      description: 'Balanced model for everyday tasks',
      capabilities: ['Text generation', 'Reasoning'],
      isAvailable: true,
    },
    {
      id: 'gemini-pro',
      name: 'Gemini Pro',
      provider: 'Google',
      description: "Google's large multimodal model",
      capabilities: ['Text generation', 'Code generation'],
      isAvailable: true,
    },
    {
      id: 'llama3',
      name: 'Llama 3',
      provider: 'Meta',
      description: 'Open weights model with strong capabilities',
      capabilities: ['Text generation'],
      isAvailable: true,
    },
  ];
};

const fetchPatterns = async (): Promise<AnalysisPattern[]> => {
  // Simulated API delay
  await new Promise((resolve) => setTimeout(resolve, 800));

  return [
    {
      id: 'gut',
      name: 'Gut Check Analysis',
      description:
        'Rapid evaluation of different perspectives to identify the most likely correct answer',
      useCases: [
        'Fact-based queries',
        'Questions with objective answers',
        'Time-sensitive analysis',
      ],
    },
    {
      id: 'confidence',
      name: 'Confidence Analysis',
      description:
        'Evaluates the strength of each model response with confidence scoring',
      useCases: [
        'Uncertain queries',
        'Risk assessment',
        'Multiple possible interpretations',
      ],
    },
    {
      id: 'critique',
      name: 'Critique Analysis',
      description:
        "Models critically evaluate each other's reasoning and answers",
      useCases: [
        'Complex reasoning tasks',
        'Checks for logical flaws',
        'Rigorous evaluation',
      ],
    },
    {
      id: 'fact_check',
      name: 'Fact Check Analysis',
      description: 'Verifies factual accuracy and cites sources for claims',
      useCases: [
        'Research topics',
        'Checking controversial claims',
        'Educational content',
      ],
    },
    {
      id: 'perspective',
      name: 'Perspective Analysis',
      description: 'Examines a question from multiple analytical perspectives',
      useCases: ['Complex problems', 'Multifaceted issues', 'Decision making'],
    },
  ];
};

const submitAnalysis = async (
  prompt: string,
  selectedModels: string[],
  selectedPattern: string,
  options: AnalysisOptions
): Promise<{
  status: string;
  results: AnalysisResult[];
}> => {
  // Simulate a multi-step analysis process with updates
  await new Promise((resolve) => setTimeout(resolve, 2000));

  return {
    status: 'complete',
    results: selectedModels.map((modelId) => ({
      modelId,
      modelName:
        modelId === 'gpt4o'
          ? 'GPT-4o'
          : modelId === 'claude3opus'
            ? 'Claude 3 Opus'
            : modelId === 'gemini-pro'
              ? 'Gemini Pro'
              : modelId,
      content: `This is a simulated analysis response from ${modelId} using the ${selectedPattern} pattern.\n\nThe prompt was: "${prompt}"\n\nIn a real implementation, this would contain the actual model response. It would include detailed analysis based on the selected pattern.\n\n## Key Points\n\n- First important point from analysis\n- Second important consideration\n- Additional context or clarification\n\n## Conclusion\n\nThis is the conclusion based on the analysis.`,
      timestamp: new Date().toISOString(),
      processingTimeMs: Math.floor(Math.random() * 3000) + 1000,
      sections: [
        {
          id: 'analysis',
          title: 'Analysis',
          content: `This is the main analysis section for the prompt: "${prompt}"`,
        },
        {
          id: 'key-points',
          title: 'Key Points',
          content:
            '- Important point 1\n- Important point 2\n- Important point 3',
        },
        {
          id: 'conclusion',
          title: 'Conclusion',
          content: 'This is the conclusion based on the analysis.',
        },
      ],
      metadata: {
        modelVersion: '1.0',
        tokenCount: Math.floor(Math.random() * 1000) + 500,
        pattern: selectedPattern,
        options,
      },
    })),
  };
};

export const AnalysisInterface: React.FC = () => {
  // State
  const [activeTab, setActiveTab] = useState('prompt');
  const [prompt, setPrompt] = useState<string>('');
  const [selectedModels, setSelectedModels] = useState<string[]>(['gpt4o']);
  const [selectedPattern, setSelectedPattern] = useState<string>('gut');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [results, setResults] = useState<AnalysisResult[] | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [analysisStatus, setAnalysisStatus] = useState<
    'idle' | 'preparing' | 'analyzing' | 'complete' | 'error'
  >('idle');

  // Loading states
  const [isLoadingModels, setIsLoadingModels] = useState<boolean>(false);
  const [isLoadingPatterns, setIsLoadingPatterns] = useState<boolean>(false);
  const [models, setModels] = useState<Model[]>([]);
  const [patterns, setPatterns] = useState<AnalysisPattern[]>([]);
  const [analysisStep, setAnalysisStep] = useState<number>(0);
  const [estimatedTimeRemaining, setEstimatedTimeRemaining] =
    useState<number>(0);

  // Load data on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        setIsLoadingModels(true);
        setIsLoadingPatterns(true);

        const [modelsData, patternsData] = await Promise.all([
          fetchModels(),
          fetchPatterns(),
        ]);

        setModels(modelsData);
        setPatterns(patternsData);
      } catch (err) {
        setError(
          err instanceof Error ? err : new Error('Failed to load initial data')
        );
      } finally {
        setIsLoadingModels(false);
        setIsLoadingPatterns(false);
      }
    };

    loadData();
  }, []);

  // Handle form submission
  const handleSubmit = async (
    submittedPrompt: string,
    options: AnalysisOptions
  ) => {
    try {
      if (selectedModels.length === 0) {
        throw new Error('Please select at least one model');
      }

      setPrompt(submittedPrompt);
      setIsSubmitting(true);
      setAnalysisStatus('preparing');
      setAnalysisStep(1);
      setEstimatedTimeRemaining(10);
      setError(null);

      // Simulate step progress
      const progressInterval = setInterval(() => {
        setAnalysisStep((step) => {
          if (step < 3) return step + 1;
          return step;
        });
        setEstimatedTimeRemaining((time) => Math.max(0, time - 3));
      }, 3000);

      setTimeout(() => {
        setAnalysisStatus('analyzing');
      }, 2000);

      // Submit analysis
      const response = await submitAnalysis(
        submittedPrompt,
        selectedModels,
        selectedPattern,
        options
      );

      clearInterval(progressInterval);

      // Update state with results
      setResults(response.results);
      setAnalysisStatus('complete');
      setActiveTab('results'); // Switch to results tab
    } catch (err) {
      setError(
        err instanceof Error
          ? err
          : new Error('An error occurred during analysis')
      );
      setAnalysisStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Cancel analysis
  const handleCancel = () => {
    setIsSubmitting(false);
    setAnalysisStatus('idle');
    setError(new Error('Analysis cancelled by user'));
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Ultra Analysis Interface</h1>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error.message}</AlertDescription>
        </Alert>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid grid-cols-3 mb-8">
          <TabsTrigger value="prompt">Prompt</TabsTrigger>
          <TabsTrigger value="models">Models & Pattern</TabsTrigger>
          <TabsTrigger value="results" disabled={!results}>
            Results
          </TabsTrigger>
        </TabsList>

        <TabsContent value="prompt">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Enter Your Prompt</h2>
            <p className="text-gray-600 mb-6">
              Provide your query or task for the AI models to analyze. Be
              specific and include relevant details for best results.
            </p>

            <EnhancedPromptInput
              onSubmit={(newPrompt, options) => {
                handleSubmit(newPrompt, options);
                setActiveTab('models');
              }}
              isLoading={isSubmitting}
              maxLength={4000}
              placeholder="Enter your prompt here..."
              initialValue={prompt}
            />
          </Card>
        </TabsContent>

        <TabsContent value="models">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6">
              <ModelSelector
                availableModels={models}
                selectedModels={selectedModels}
                onSelectionChange={setSelectedModels}
                isLoading={isLoadingModels}
                maxSelections={5}
              />
            </Card>

            <Card className="p-6">
              <EnhancedPatternSelector
                availablePatterns={patterns}
                selectedPattern={selectedPattern}
                onPatternChange={setSelectedPattern}
                isLoading={isLoadingPatterns}
              />
            </Card>
          </div>

          {(analysisStatus === 'preparing' ||
            analysisStatus === 'analyzing' ||
            analysisStatus === 'complete' ||
            analysisStatus === 'error') && (
            <div className="mt-6">
              <AnalysisProgress
                status={analysisStatus}
                currentStep={analysisStep}
                totalSteps={3}
                estimatedTimeRemaining={estimatedTimeRemaining}
                error={error || undefined}
                onCancel={handleCancel}
              />
            </div>
          )}
        </TabsContent>

        <TabsContent value="results">
          {results ? (
            <Card className="p-6">
              <ResultsDisplay
                results={results}
                isLoading={isSubmitting}
                error={error || undefined}
                comparisonMode={results.length > 1}
              />
            </Card>
          ) : (
            <Card className="p-6 text-center text-gray-500">
              No results to display. Submit a prompt for analysis.
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AnalysisInterface;
