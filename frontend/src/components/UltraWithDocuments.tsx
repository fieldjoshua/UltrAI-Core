'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Checkbox } from './ui/checkbox';
import {
  Zap,
  Award,
  Brain,
  Feather,
  Shield,
  FileText,
  Users,
  Network,
  Clock,
  Lightbulb,
  RefreshCw,
  Upload,
  X,
  File,
  Check,
  History,
  Save,
  Trash2,
  Share2,
  Copy,
  Link,
  ExternalLink,
  DollarSign,
  FileCheck,
  EyeOff,
  Lock,
  SplitSquareVertical,
  FileType,
} from 'lucide-react';
import AnimatedLogoV3 from './AnimatedLogoV3';
import HistoryPanel from './panels/HistoryPanel';
import ShareDialog from './dialogs/ShareDialog';
import IntroStep from './steps/IntroStep';
import PromptStep from './steps/PromptStep';
import DocumentStep from './steps/DocumentStep';
import ModelSelectionStep from './steps/ModelSelectionStep';
import AnalysisTypeStep from './steps/AnalysisTypeStep';
import OptionsStep from './steps/OptionsStep';
import ProcessingStep from './steps/ProcessingStep';
import ResultsStep from './steps/ResultsStep';

// Import the API service functions
import { fetchAvailableModels, analyzePrompt, AnalysisPayload } from '../services/api';

// Import the layout components
import OfflineBanner from './layout/OfflineBanner';
import StepIndicator from './layout/StepIndicator';

// Import the custom hooks
import { useDocumentState } from '../hooks/useDocumentState';
import { useAnalysisConfig } from '../hooks/useAnalysisConfig';
import { useAnalysisExecution } from '../hooks/useAnalysisExecution';
import { useHistorySharing } from '../hooks/useHistorySharing';

// Step definitions
type Step =
  | 'INTRO'
  | 'PROMPT'
  | 'DOCUMENTS'
  | 'MODELS'
  | 'ANALYSIS_TYPE'
  | 'OPTIONS'
  | 'PROCESSING'
  | 'RESULTS';

// Step information with titles and descriptions
const stepInfo: Record<Step, { title: string; description: string }> = {
  INTRO: {
    title: 'Welcome to Ultra AI',
    description:
      'Experience AI intelligence multiplication through our multi-model analysis system.',
  },
  PROMPT: {
    title: 'Enter Your Prompt',
    description:
      'What would you like Ultra to analyze? Be specific for better results.',
  },
  DOCUMENTS: {
    title: 'Add Context',
    description:
      'Upload documents to provide additional context for your analysis.',
  },
  MODELS: {
    title: 'Select AI Models',
    description:
      'Choose which AI models to use for your analysis. Each model brings unique strengths.',
  },
  ANALYSIS_TYPE: {
    title: 'Analysis Method',
    description: 'Select how Ultra should approach your query.',
  },
  OPTIONS: {
    title: 'Select A La Carte Options',
    description: 'Choose additional options for your analysis.',
  },
  PROCESSING: {
    title: 'Processing',
    description: 'Ultra is analyzing your query across multiple models.',
  },
  RESULTS: {
    title: 'Results',
    description: 'Review your analysis from multiple AI perspectives.',
  },
};

// Define the model price mapping
const prices: { [key: string]: number } = {
  gpt4o: 0.0125,
  gpt4turbo: 0.04,
  gpto3mini: 0.0055,
  gpto1: 0.075,
  claude37: 0.018,
  claude3opus: 0.09,
  gemini15: 0.000375,
  llama3: 0,
};

// Define history and share interfaces (only needed for TypeScript if not imported)
interface HistoryItem {
  id: string;
  prompt: string;
  output: string;
  models: string[];
  ultraModel: string;
  timestamp: string;
  usingDocuments?: boolean;
  documents?: { id: string; name: string }[];
}

interface ShareItem extends HistoryItem {
  shareId: string;
  shareUrl: string;
  createdAt: string;
}

// Analysis pattern options
const analysisTypes = [
  {
    id: 'confidence',
    name: 'Confidence',
    description: 'Standard analysis with confidence scoring',
    icon: Shield,
  },
  {
    id: 'critique',
    name: 'Critique',
    description: 'Critical evaluation with pros and cons',
    icon: FileText,
  },
  {
    id: 'perspective',
    name: 'Perspective',
    description: 'Multiple viewpoints on the topic',
    icon: Users,
  },
  {
    id: 'fact_check',
    name: 'Fact Check',
    description: 'Verification of factual claims',
    icon: Check,
  },
  {
    id: 'scenario',
    name: 'Scenario',
    description: 'Future scenario exploration',
    icon: Network,
  },
];

// A la carte options
const alaCarteOptions = [
  {
    id: 'fact_check',
    name: 'Fact Check',
    description: 'Verify factual claims in the text',
    icon: FileCheck,
  },
  {
    id: 'avoid_ai_detection',
    name: 'Avoid AI Detection',
    description: 'Optimize output to avoid AI detection tools',
    icon: EyeOff,
  },
  {
    id: 'sourcing',
    name: 'Sourcing',
    description: 'Include sources to support the analysis',
    icon: Link,
  },
  {
    id: 'encrypted',
    name: 'Encrypted',
    description: 'Enhanced encryption for sensitive content',
    icon: Lock,
  },
  {
    id: 'no_data_sharing',
    name: 'No Data Sharing',
    description: 'Ensure data isn\'t shared or stored',
    icon: Shield,
  },
  {
    id: 'alternate_perspective',
    name: 'Alternate Perspective',
    description: 'Include alternative viewpoints',
    icon: SplitSquareVertical,
  },
];

// Output format options
const formatOptions = [
  {
    id: 'txt',
    name: 'Plain Text',
    description: 'Simple text format',
    icon: FileText,
  },
  {
    id: 'rtf',
    name: 'Rich Text Format',
    description: 'Formatted text with styling',
    icon: FileType,
  },
  {
    id: 'google_docs',
    name: 'Google Docs',
    description: 'Optimized for Google Docs',
    icon: File,
  },
  {
    id: 'word',
    name: 'Microsoft Word',
    description: 'Optimized for MS Word',
    icon: FileText,
  },
];

export default function UltraWithDocuments() {
  // Basic state
  const [prompt, setPrompt] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [selectedAlaCarteOptions, setSelectedAlaCarteOptions] = useState<string[]>([]);
  const [selectedOutputFormat, setSelectedOutputFormat] = useState<string>('txt');
  const [currentStep, setCurrentStep] = useState<Step>('INTRO');
  const [animating, setAnimating] = useState(false);
  const outputRef = React.useRef<HTMLDivElement>(null);
  const [isOffline, setIsOffline] = useState<boolean>(false);
  const [floatingPriceVisible, setFloatingPriceVisible] = useState<boolean>(true);
  const [floatingPricePosition, setFloatingPricePosition] = useState({ top: 0, right: 20 });
  const floatingPriceRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Use custom hooks
  const {
    documents,
    uploadProgress,
    uploadedDocuments,
    isUsingDocuments,
    fileInputRef,
    documentError,
    handleFileSelect,
    removeDocument,
    uploadDocuments,
    toggleDocumentMode,
    resetDocumentState
  } = useDocumentState();

  const {
    selectedLLMs,
    ultraLLM,
    availableModels,
    selectedAnalysisType,
    configError,
    handleLLMChange,
    handleUltraChange,
    handleAnalysisTypeChange,
    resetAnalysisConfig
  } = useAnalysisConfig(isOffline);

  const {
    isProcessing,
    isComplete,
    output: executionOutput,
    progress: executionProgress,
    progressMessage: executionProgressMessage,
    isCached,
    executeAnalysis,
    updateProgress,
    resetExecutionState,
    error: executionError
  } = useAnalysisExecution();

  const {
    history,
    showHistory,
    setShowHistory,
    sharedItems,
    showShareDialog,
    setShowShareDialog,
    shareDialogItem,
    shareUrl,
    copySuccess,
    saveToHistory,
    loadFromHistory,
    deleteHistoryItem,
    clearHistory,
    shareHistoryItem,
    copyToClipboard
  } = useHistorySharing();

  // Combine errors from different hooks
  useEffect(() => {
    const errors = [configError, documentError, executionError].filter(Boolean);
    setError(errors.length > 0 ? errors.join('\n') : null);
  }, [configError, documentError, executionError]);

  // Scroll to results when they're ready
  useEffect(() => {
    if (isComplete && outputRef.current) {
      outputRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [isComplete]);

  // Track scroll position to update floating price position
  useEffect(() => {
    const handleScroll = () => {
      if (containerRef.current && floatingPriceRef.current) {
        const containerRect = containerRef.current.getBoundingClientRect();
        const scrollY = window.scrollY;

        // Keep price visible when container is in view
        if (
          containerRect.top < window.innerHeight &&
          containerRect.bottom > 0
        ) {
          const newTop = Math.max(
            20, // Minimum top position
            Math.min(
              window.innerHeight - floatingPriceRef.current.offsetHeight - 20, // Maximum top position
              scrollY - containerRect.top + 100 // Dynamic position that follows scroll
            )
          );

          setFloatingPricePosition({
            top: newTop,
            right: 20,
          });
          setFloatingPriceVisible(true);
        } else {
          // Hide when container is not in view
          setFloatingPriceVisible(false);
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    // Initial positioning
    handleScroll();

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [currentStep]);

  // Calculate current progress percentage based on steps
  const calculateProgress = () => {
    const steps: Step[] = [
      'INTRO',
      'PROMPT',
      'DOCUMENTS',
      'MODELS',
      'ANALYSIS_TYPE',
      'OPTIONS',
      'PROCESSING',
      'RESULTS',
    ];
    const currentIndex = steps.indexOf(currentStep);
    return Math.round((currentIndex / (steps.length - 1)) * 100);
  };

  // Handle step navigation
  const goToNextStep = () => {
    const steps: Step[] = [
      'INTRO',
      'PROMPT',
      'DOCUMENTS',
      'MODELS',
      'ANALYSIS_TYPE',
      'OPTIONS',
      'PROCESSING',
      'RESULTS',
    ];
    const currentIndex = steps.indexOf(currentStep);
    if (currentIndex < steps.length - 1) {
      setCurrentStep(steps[currentIndex + 1]);
      updateProgress(calculateProgress(), 'Moving to next step...');
    }
  };

  const goToPreviousStep = () => {
    const steps: Step[] = [
      'INTRO',
      'PROMPT',
      'DOCUMENTS',
      'MODELS',
      'ANALYSIS_TYPE',
      'OPTIONS',
      'PROCESSING',
      'RESULTS',
    ];
    const currentIndex = steps.indexOf(currentStep);
    if (currentIndex > 0) {
      setCurrentStep(steps[currentIndex - 1]);
      updateProgress(calculateProgress(), 'Moving to previous step...');
    }
  };

  // Validate if user can proceed to the next step
  const validateCurrentStep = () => {
    switch (currentStep) {
      case 'INTRO':
        return true; // Can always proceed from intro
      case 'PROMPT':
        return prompt.trim().length > 0; // Need a prompt to continue
      case 'DOCUMENTS':
        return true; // Documents are optional
      case 'MODELS':
        return selectedLLMs.length > 0 && ultraLLM !== null; // Need models selected
      case 'ANALYSIS_TYPE':
        return true; // Default analysis type is pre-selected
      case 'OPTIONS':
        return true; // Options are optional
      case 'PROCESSING':
        return isComplete; // Wait until processing is done
      default:
        return true;
    }
  };

  // Handle analysis execution
  const handleAnalyzeClick = async () => {
    if (currentStep === 'ANALYSIS_TYPE' || currentStep === 'OPTIONS') {
      setCurrentStep('PROCESSING');
      setAnimating(true);
      setError(null);

      // Upload documents if needed
      if (isUsingDocuments && documents.length > 0) {
        updateProgress(10, 'Uploading documents...');
        try {
          await uploadDocuments();
        } catch (uploadError: any) {
          setError(`Document upload failed: ${uploadError.message}`);
          setAnimating(false);
          setCurrentStep('DOCUMENTS');
          return;
        }
      }

      const payload: AnalysisPayload = {
        prompt,
        selected_models: selectedLLMs,
        ultra_model: ultraLLM,
        pattern: selectedAnalysisType,
        options: {
          ...selectedAlaCarteOptions.reduce((acc, opt) => ({ ...acc, [opt]: true }), {})
        },
        output_format: selectedOutputFormat,
        userId: 'user-placeholder',
      };

      try {
        await executeAnalysis(payload);
        saveAnalysisToHistory();
        setCurrentStep('RESULTS');
      } catch (analysisError: any) {
        console.error("Analysis execution caught in component:", analysisError);
        saveAnalysisToHistory();
        setCurrentStep('RESULTS');
      } finally {
        setAnimating(false);
      }
    } else if (currentStep === 'PROCESSING' && isComplete) {
      setCurrentStep('RESULTS');
    }
  };

  // Start a new analysis
  const startNewAnalysis = () => {
    setCurrentStep('PROMPT');
    setPrompt('');
    setError(null);
    resetDocumentState();
    resetAnalysisConfig();
    resetExecutionState();
    setSelectedAlaCarteOptions([]);
    setSelectedOutputFormat('txt');
  };

  // Handle saving analysis to history
  const saveAnalysisToHistory = () => {
    if (!prompt || !executionOutput) return;

    const historyItem: HistoryItem = {
      id: Date.now().toString(),
      prompt,
      output: executionOutput,
      models: selectedLLMs,
      ultraModel: ultraLLM || '',
      timestamp: new Date().toISOString(),
      usingDocuments: isUsingDocuments,
      documents: isUsingDocuments ? uploadedDocuments : undefined,
    };

    saveToHistory(historyItem);
  };

  // Handle loading a history item
  const handleLoadFromHistory = (item: HistoryItem) => {
    const historyItem = loadFromHistory(item);

    setPrompt(historyItem.prompt);
    setCurrentStep('RESULTS');

    if (historyItem.models && historyItem.models.length > 0) {
      const availableItemModels = historyItem.models.filter((model) =>
        availableModels.includes(model)
      );

      if (availableItemModels.length > 0) {
        handleLLMChange(availableItemModels[0]);
      }
    }
  };

  // Handle a la carte option toggle
  const handleAlaCarteOptionToggle = (optionId: string) => {
    setSelectedAlaCarteOptions((prev) => {
      if (prev.includes(optionId)) {
        return prev.filter((id) => id !== optionId);
      } else {
        return [...prev, optionId];
      }
    });
  };

  // Handle output format change
  const handleOutputFormatChange = (formatId: string) => {
    setSelectedOutputFormat(formatId);
  };

  // Handle sharing analysis
  const shareAnalysis = () => {
    if (!prompt || !executionOutput) return;

    const currentItem: HistoryItem = {
      id: Date.now().toString(),
      prompt,
      output: executionOutput,
      models: selectedLLMs,
      ultraModel: ultraLLM || '',
      timestamp: new Date().toISOString(),
      usingDocuments: isUsingDocuments,
      documents: isUsingDocuments ? uploadedDocuments : undefined,
    };

    shareHistoryItem(currentItem);
  };

  // Render the floating price component
  const renderFloatingPrice = () => {
    if (!floatingPriceVisible || currentStep === 'INTRO' || currentStep === 'RESULTS') {
      return null;
    }

    // Calculate total price based on selected models
    const totalPrice = selectedLLMs.reduce((sum, model) => sum + (prices[model] || 0), 0);

    return (
      <div
        ref={floatingPriceRef}
        className="fixed bg-white dark:bg-gray-800 shadow-lg rounded-lg p-3 z-50 border border-gray-200 dark:border-gray-700 transition-all duration-300"
        style={{ top: `${floatingPricePosition.top}px`, right: `${floatingPricePosition.right}px` }}
      >
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Estimated Cost</span>
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 p-0"
            onClick={() => setFloatingPriceVisible(false)}
          >
            <X size={14} />
          </Button>
        </div>
        <div className="flex items-center">
          <DollarSign size={16} className="text-green-600 mr-1" />
          <span className="text-lg font-bold text-gray-900 dark:text-white">
            ${totalPrice.toFixed(4)}
          </span>
        </div>
      </div>
    );
  };

  // Render content based on current step
  const renderStepContent = () => {
    switch (currentStep) {
      case 'INTRO':
        return <IntroStep />;

      case 'PROMPT':
        return (
          <PromptStep
            prompt={prompt}
            setPrompt={setPrompt}
            isProcessing={isProcessing}
            isOffline={isOffline}
            error={error}
            goToNextStep={goToNextStep}
            goToPreviousStep={goToPreviousStep}
          />
        );

      case 'DOCUMENTS':
        return (
          <DocumentStep
            documents={documents}
            uploadProgress={uploadProgress}
            uploadedDocuments={uploadedDocuments}
            isUsingDocuments={isUsingDocuments}
            isProcessing={isProcessing}
            isOffline={isOffline}
            fileInputRef={fileInputRef}
            onFileSelect={handleFileSelect}
            onRemoveDocument={removeDocument}
            onUploadDocuments={uploadDocuments}
            onToggleDocumentMode={toggleDocumentMode}
          />
        );

      case 'MODELS':
        return (
          <ModelSelectionStep
            availableModels={availableModels}
            selectedLLMs={selectedLLMs}
            ultraLLM={ultraLLM}
            prices={prices}
            isProcessing={isProcessing}
            isOffline={isOffline}
            onLLMChange={handleLLMChange}
            onUltraChange={handleUltraChange}
          />
        );

      case 'ANALYSIS_TYPE':
        return (
          <AnalysisTypeStep
            analysisTypes={analysisTypes}
            selectedAnalysisType={selectedAnalysisType}
            onAnalysisTypeChange={handleAnalysisTypeChange}
          />
        );

      case 'OPTIONS':
        return (
          <OptionsStep
            alaCarteOptions={alaCarteOptions}
            formatOptions={formatOptions}
            selectedAlaCarteOptions={selectedAlaCarteOptions}
            selectedOutputFormat={selectedOutputFormat}
            onAlaCarteOptionToggle={handleAlaCarteOptionToggle}
            onOutputFormatChange={handleOutputFormatChange}
          />
        );

      case 'PROCESSING':
        return (
          <ProcessingStep
            progress={executionProgress}
            progressMessage={executionProgressMessage}
            error={error}
            onRetry={handleAnalyzeClick}
          />
        );

      case 'RESULTS':
        return (
          <ResultsStep
            prompt={prompt}
            output={executionOutput}
            isOffline={isOffline}
            outputRef={outputRef}
            onStartNewAnalysis={startNewAnalysis}
            onShowHistory={() => setShowHistory(true)}
            onShareAnalysis={shareAnalysis}
            onSaveToHistory={saveAnalysisToHistory}
          />
        );

      default:
        return null;
    }
  };

  // Render the component
  return (
    <div className="container mx-auto p-4 md:p-8 max-w-6xl" ref={containerRef}>
      {/* Step Indicator */}
      <StepIndicator currentStep={currentStep} />

      {/* Current Step Title and Description */}
      <div className="mb-8 text-center">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-2">
          {stepInfo[currentStep].title}
        </h2>
        <p className="text-gray-600 dark:text-gray-300">
          {stepInfo[currentStep].description}
        </p>
      </div>

      {/* Floating Price Component */}
      {renderFloatingPrice()}

      {/* Main Content Area */}
      <div className="bg-white dark:bg-gray-900 rounded-xl shadow-md p-6 mb-8 transition-all duration-500">
        {renderStepContent()}
      </div>

      {/* Navigation Buttons */}
      <div className="flex justify-between mt-8">
        <Button
          onClick={goToPreviousStep}
          disabled={currentStep === 'INTRO' || isProcessing}
          variant="outline"
          className="border-gray-300 dark:border-gray-700"
        >
          Previous
        </Button>

        {currentStep !== 'PROCESSING' && currentStep !== 'RESULTS' ? (
          <Button
            onClick={goToNextStep}
            disabled={!validateCurrentStep() || isProcessing || isOffline}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            {currentStep === 'ANALYSIS_TYPE' ? 'Start Analysis' : 'Next'}
          </Button>
        ) : currentStep === 'PROCESSING' ? (
          <Button
            onClick={handleAnalyzeClick}
            disabled={!isComplete || isOffline}
            className="bg-green-600 hover:bg-green-700 text-white"
          >
            View Results
          </Button>
        ) : null}
      </div>

      {/* History Panel */}
      <HistoryPanel
        showHistory={showHistory}
        history={history}
        sharedItems={sharedItems}
        onClose={() => setShowHistory(false)}
        onClearAll={clearHistory}
        onLoadItem={handleLoadFromHistory}
        onDeleteItem={deleteHistoryItem}
        onShareItem={shareHistoryItem}
      />

      {/* Share Dialog */}
      <ShareDialog
        showShareDialog={showShareDialog}
        shareDialogItem={shareDialogItem}
        shareUrl={shareUrl}
        copySuccess={copySuccess}
        onClose={() => setShowShareDialog(false)}
        onCopyToClipboard={copyToClipboard}
      />

      {/* Offline Banner */}
      <OfflineBanner isOffline={isOffline} />
    </div>
  );
}
