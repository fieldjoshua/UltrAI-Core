'use client'

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Checkbox } from './ui/checkbox';
import { Progress } from './ui/progress';
import { Zap, Award, Brain, Feather, Shield, FileText, Users, Network, Clock, Lightbulb, RefreshCw, Upload, X, File, Check, History, Save, Trash2, WifiOff, Share2, Copy, Link, ExternalLink } from 'lucide-react';

// Simplified API URL
const API_URL = import.meta.env.VITE_API_URL || 'https://ultra-api.vercel.app';

// Step definitions - add INTRO as the first step
type Step = 'INTRO' | 'PROMPT' | 'MODELS' | 'PROCESSING' | 'RESULTS';

// Define the model price mapping
const prices: { [key: string]: number } = {
  'gpt4o': 0.0125,
  'gpt4turbo': 0.04,
  'gpto3mini': 0.00550,
  'gpto1': 0.075,
  'claude37': 0.018,
  'claude3opus': 0.09,
  'gemini15': 0.000375,
  'llama3': 0
};

// Configuration for API calls
const API_CONFIG = {
  baseURL: API_URL,
  maxRetries: 3,
  retryDelay: 1000, // 1 second initial delay
  retryStatusCodes: [408, 429, 500, 502, 503, 504] // Status codes to retry on
};

// Axios instance with retry capability
const axiosWithRetry = axios.create({ baseURL: API_CONFIG.baseURL });

// Add response interceptor for handling retries
axiosWithRetry.interceptors.response.use(undefined, async (error) => {
  const { config, response = {} } = error;

  // Skip retry for specific error status codes or if we've already retried the maximum times
  if (
    !config ||
    !API_CONFIG.retryStatusCodes.includes(response.status) ||
    config.__retryCount >= API_CONFIG.maxRetries
  ) {
    return Promise.reject(error);
  }

  // Set retry count
  config.__retryCount = config.__retryCount || 0;
  config.__retryCount++;

  // Exponential backoff delay
  const delay = API_CONFIG.retryDelay * Math.pow(2, config.__retryCount - 1);

  // Wait for the delay
  await new Promise(resolve => setTimeout(resolve, delay));

  // Retry the request
  return axiosWithRetry(config);
});

// Define the history item interface
interface HistoryItem {
  id: string;
  prompt: string;
  output: string;
  models: string[];
  ultraModel: string;
  timestamp: string;
  usingDocuments?: boolean;
  documents?: { id: string, name: string }[];
}

// Define the share interface
interface ShareItem extends HistoryItem {
  shareId: string;
  shareUrl: string;
  createdAt: string;
}

export default function UltraWithDocuments() {
  // Basic state
  const [prompt, setPrompt] = useState('');
  const [output, setOutput] = useState('');
  const [selectedLLMs, setSelectedLLMs] = useState<string[]>([]);
  const [ultraLLM, setUltraLLM] = useState<string | null>(null);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Processing state
  const [isProcessing, setIsProcessing] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [isCached, setIsCached] = useState(false);

  // Document state
  const [documents, setDocuments] = useState<File[]>([]);
  const [uploadProgress, setUploadProgress] = useState<{ [key: string]: number }>({});
  const [uploadedDocuments, setUploadedDocuments] = useState<{ id: string, name: string }[]>([]);
  const [isUsingDocuments, setIsUsingDocuments] = useState(false);

  // File input ref
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Step flow state
  const [currentStep, setCurrentStep] = useState<Step>('INTRO');
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('Initializing analysis...');

  // Animation state
  const [animating, setAnimating] = useState(false);

  // Create a ref for the output container to implement scroll to results
  const outputRef = React.useRef<HTMLDivElement>(null);

  // History state
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  // Offline state
  const [isOffline, setIsOffline] = useState<boolean>(false);

  // Sharing state
  const [shareUrl, setShareUrl] = useState<string>('');
  const [showShareDialog, setShowShareDialog] = useState(false);
  const [shareDialogItem, setShareDialogItem] = useState<HistoryItem | null>(null);
  const [sharedItems, setSharedItems] = useState<ShareItem[]>([]);
  const [copySuccess, setCopySuccess] = useState(false);

  // Check online status on component mount and add event listeners
  useEffect(() => {
    // Check initial online status
    setIsOffline(!navigator.onLine);

    // Event listeners for online/offline status
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);

    // Add event listeners
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Clean up event listeners on component unmount
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Check for available models on component mount
  useEffect(() => {
    const fetchAvailableModels = async () => {
      // Skip the API call if offline
      if (isOffline) {
        setError('You are currently offline. You can view your saved interactions, but cannot make new requests.');
        return;
      }

      try {
        setError(null);
        const response = await axiosWithRetry.get(`/api/available-models`);
        if (response.data && response.data.available_models) {
          setAvailableModels(response.data.available_models);
        } else {
          setError('Could not retrieve available models');
        }
      } catch (err: any) {
        setError(`Could not connect to the backend API: ${err.message}`);
      }
    };

    fetchAvailableModels();
  }, [isOffline]);

  // Scroll to results when they're ready
  useEffect(() => {
    if (isComplete && outputRef.current) {
      outputRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [isComplete]);

  // Load history from local storage on component mount
  useEffect(() => {
    const loadHistory = () => {
      try {
        const savedHistory = localStorage.getItem('ultraAiHistory');
        if (savedHistory) {
          setHistory(JSON.parse(savedHistory));
        }
      } catch (err) {
        console.error('Failed to load history:', err);
        // If loading fails, reset history storage
        localStorage.removeItem('ultraAiHistory');
      }
    };

    loadHistory();
  }, []);

  // Load shared items from local storage on component mount
  useEffect(() => {
    const loadSharedItems = () => {
      try {
        const savedSharedItems = localStorage.getItem('ultraAiSharedItems');
        if (savedSharedItems) {
          setSharedItems(JSON.parse(savedSharedItems));
        }
      } catch (err) {
        console.error('Failed to load shared items:', err);
        // If loading fails, reset shared items storage
        localStorage.removeItem('ultraAiSharedItems');
      }
    };

    loadSharedItems();
  }, []);

  // Toggle a model selection
  const toggleModelSelection = (modelId: string) => {
    if (selectedLLMs.includes(modelId)) {
      setSelectedLLMs(selectedLLMs.filter(id => id !== modelId));
    } else {
      setSelectedLLMs([...selectedLLMs, modelId]);
    }
  };

  // Handle LLM selection with toggleModelSelection
  const handleLLMChange = (id: string) => {
    toggleModelSelection(id);

    // Reset the ultra model if it's no longer selected as an LLM
    if (ultraLLM === id && !selectedLLMs.includes(id)) {
      setUltraLLM(null);
    }
  };

  // Set a model as the Ultra model
  const handleUltraChange = (id: string) => {
    // If not already selected as an LLM, select it
    if (!selectedLLMs.includes(id)) {
      setSelectedLLMs([...selectedLLMs, id]);
    }
    setUltraLLM(id);
  };

  // Update progress with a message
  const updateProgress = (percent: number, message: string) => {
    setProgress(percent);
    setProgressMessage(message);
  };

  // Handle file selection
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = e.target.files;
    if (fileList) {
      const newFiles = Array.from(fileList);
      setDocuments(prev => [...prev, ...newFiles]);
    }

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Remove a document from the list
  const removeDocument = (indexToRemove: number) => {
    setDocuments(docs => docs.filter((_, index) => index !== indexToRemove));
  };

  // Upload documents to server
  const uploadDocuments = async () => {
    if (documents.length === 0) return;

    setError(null);

    for (let i = 0; i < documents.length; i++) {
      const file = documents[i];
      const formData = new FormData();
      formData.append('file', file);

      try {
        // Track upload progress
        setUploadProgress(prev => ({ ...prev, [file.name]: 0 }));

        const response = await axiosWithRetry.post('/api/upload-document', formData, {
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              setUploadProgress(prev => ({ ...prev, [file.name]: percentCompleted }));
            }
          }
        });

        if (response.data && response.data.id) {
          setUploadedDocuments(prev => [...prev, { id: response.data.id, name: file.name }]);
        }
      } catch (err: any) {
        setError(`Failed to upload ${file.name}: ${err.message}`);
        // Continue with other files even if one fails
      }
    }

    // Clear documents list after upload attempts
    setDocuments([]);
  };

  // Toggle document mode
  const toggleDocumentMode = () => {
    setIsUsingDocuments(prev => !prev);
  };

  // Handle saving current interaction to history
  const saveToHistory = () => {
    if (!prompt || !output) return;

    const historyItem: HistoryItem = {
      id: Date.now().toString(),
      prompt,
      output,
      models: selectedLLMs,
      ultraModel: ultraLLM || '',
      timestamp: new Date().toISOString(),
      usingDocuments: isUsingDocuments,
      documents: isUsingDocuments ? uploadedDocuments : undefined
    };

    // Add to history
    const updatedHistory = [historyItem, ...history].slice(0, 50); // Keep only the most recent 50 entries
    setHistory(updatedHistory);

    // Save to localStorage
    try {
      localStorage.setItem('ultraAiHistory', JSON.stringify(updatedHistory));
    } catch (err) {
      console.error('Failed to save history:', err);
    }
  };

  // Load a history item
  const loadFromHistory = (item: HistoryItem) => {
    setPrompt(item.prompt);
    setOutput(item.output);

    // Set models if they're available
    if (item.models && item.models.length > 0) {
      const availableItemModels = item.models.filter(model =>
        availableModels.includes(model)
      );

      if (availableItemModels.length > 0) {
        setSelectedLLMs(availableItemModels);
      }
    }

    // Set ultra model if it's available
    if (item.ultraModel && availableModels.includes(item.ultraModel)) {
      setUltraLLM(item.ultraModel);
    }

    // Set document mode and documents if applicable
    if (item.usingDocuments && item.documents) {
      setIsUsingDocuments(true);
      setUploadedDocuments(item.documents);
    } else {
      setIsUsingDocuments(false);
      setUploadedDocuments([]);
    }

    // Set component state
    setIsComplete(true);
    setCurrentStep('RESULTS');
    setShowHistory(false);
  };

  // Delete a history item
  const deleteHistoryItem = (id: string) => {
    const updatedHistory = history.filter(item => item.id !== id);
    setHistory(updatedHistory);

    // Save updated history to localStorage
    try {
      localStorage.setItem('ultraAiHistory', JSON.stringify(updatedHistory));
    } catch (err) {
      console.error('Failed to save updated history:', err);
    }
  };

  // Clear all history
  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem('ultraAiHistory');
    setShowHistory(false);
  };

  // Generate a shareable link for a history item
  const shareHistoryItem = (item: HistoryItem) => {
    setShareDialogItem(item);

    // Check if this item has already been shared
    const existingShare = sharedItems.find(shared => shared.id === item.id);

    if (existingShare) {
      // Use the existing share URL
      setShareUrl(existingShare.shareUrl);
    } else {
      // Generate new share ID and URL
      const shareId = generateShareId();
      const newShareUrl = `${window.location.origin}/share/${shareId}`;
      setShareUrl(newShareUrl);

      // Create new shared item
      const sharedItem: ShareItem = {
        ...item,
        shareId,
        shareUrl: newShareUrl,
        createdAt: new Date().toISOString()
      };

      // Add to shared items
      const updatedSharedItems = [...sharedItems, sharedItem];
      setSharedItems(updatedSharedItems);

      // Save to localStorage
      try {
        localStorage.setItem('ultraAiSharedItems', JSON.stringify(updatedSharedItems));
      } catch (err) {
        console.error('Failed to save shared items:', err);
      }
    }

    // Show share dialog
    setShowShareDialog(true);
  };

  // Generate a unique share ID
  const generateShareId = (): string => {
    return Math.random().toString(36).substring(2, 15) +
      Math.random().toString(36).substring(2, 15);
  };

  // Copy share URL to clipboard
  const copyToClipboard = () => {
    navigator.clipboard.writeText(shareUrl)
      .then(() => {
        setCopySuccess(true);
        setTimeout(() => setCopySuccess(false), 2000);
      })
      .catch(err => {
        console.error('Failed to copy:', err);
      });
  };

  // Main function to analyze the prompt
  const handleAnalyze = async () => {
    // Don't allow analysis when offline
    if (isOffline) {
      setError('You cannot analyze prompts while offline. Please reconnect to the internet.');
      return;
    }

    try {
      // Validate inputs
      if (!prompt.trim()) {
        setError('Please enter a prompt');
        return;
      }

      if (selectedLLMs.length < 2) {
        setError('Please select at least two AI models');
        return;
      }

      if (!ultraLLM) {
        setError('Please select a synthesizer model');
        return;
      }

      setIsProcessing(true);
      setCurrentStep('PROCESSING');
      setIsComplete(false);
      setError(null);
      setOutput('');
      setIsCached(false);

      // Reset and start progress
      updateProgress(10, 'Initializing models...');

      // Filter out unavailable models
      const availableSelectedModels = selectedLLMs.filter(modelId =>
        availableModels.includes(modelId)
      );

      // If no selected models are available, show error
      if (availableSelectedModels.length === 0) {
        throw new Error("None of the selected models are available. Please select available models.");
      }

      // If ultra model isn't available, use the first available model
      let safeUltraModel = ultraLLM;
      if (ultraLLM && !availableModels.includes(ultraLLM)) {
        safeUltraModel = availableSelectedModels[0];
      }

      // Update progress
      updateProgress(30, 'Requesting analysis from models...');

      // Create request data with or without document IDs
      const requestData = {
        prompt,
        llms: availableSelectedModels,
        ultraLLM: safeUltraModel,
        pattern: "Confidence Analysis", // Default pattern
        documentIds: isUsingDocuments && uploadedDocuments.length > 0
          ? uploadedDocuments.map(doc => doc.id)
          : undefined
      };

      // Make API request with retry capability
      const response = await axiosWithRetry.post(`/api/analyze`, requestData);

      updateProgress(90, 'Processing results...');

      // Check if the response was from cache
      if (response.data && response.data.cached) {
        setIsCached(true);
        updateProgress(100, 'Retrieved from cache');
      } else {
        updateProgress(100, 'Analysis complete');
      }

      // Handle response
      if (response.data && (response.data.ultra_response || response.data.status === 'success')) {
        const resultText = response.data.ultra_response || response.data.results?.ultra;
        setOutput(resultText || 'No response received from AI models.');
        setIsComplete(true);
        setCurrentStep('RESULTS');

        // Save this successful interaction to history
        setTimeout(() => {
          saveToHistory();
        }, 500);
      } else {
        setError('Received invalid response from server');
      }
    } catch (err: any) {
      let errorMessage = `An error occurred: ${err.message || err}`;

      // Enhanced error handling for different error types
      if (err.response) {
        // Backend returned an error response
        const status = err.response.status;
        const errorData = err.response.data;

        if (status === 400) {
          errorMessage = `Error: ${errorData.message || 'Invalid request parameters'}`;
        } else if (status === 402) {
          errorMessage = `Error: ${errorData.message || 'Insufficient account balance for this request'}`;
        } else if (status === 429) {
          errorMessage = 'Error: Rate limit exceeded. Please try again later.';
        } else if (status >= 500) {
          errorMessage = `Server error: ${errorData.message || 'The server encountered an error'}`;
        }
      } else if (err.request) {
        // Request was made but no response received
        errorMessage = 'Error: No response received from server. Please check your internet connection.';
      }

      setError(errorMessage);
      updateProgress(100, 'Error occurred');
    } finally {
      setIsProcessing(false);
    }
  };

  // Render the offline banner
  const renderOfflineBanner = () => {
    if (!isOffline) return null;

    return (
      <div className="bg-yellow-900/30 border border-yellow-700 rounded-lg p-3 mb-6 flex items-center">
        <WifiOff className="h-5 w-5 text-yellow-500 mr-2 flex-shrink-0" />
        <div>
          <p className="text-yellow-300 font-medium">You are currently offline</p>
          <p className="text-yellow-400/80 text-sm">You can view your saved interactions, but cannot make new requests until you reconnect.</p>
        </div>
      </div>
    );
  };

  // Handle step navigation with animation
  const goToNextStep = () => {
    // If offline and not in history viewing mode, don't allow progress
    if (isOffline && currentStep !== 'RESULTS') {
      setError('You cannot create new analyses while offline. Please reconnect to the internet.');
      return;
    }

    setAnimating(true);

    setTimeout(() => {
      if (currentStep === 'INTRO') {
        setCurrentStep('PROMPT');
      } else if (currentStep === 'PROMPT') {
        if (!prompt.trim()) {
          setError('Please enter a prompt');
          setAnimating(false);
          return;
        }
        setError(null);
        setCurrentStep('MODELS');
      } else if (currentStep === 'MODELS') {
        handleAnalyze();
      }
      setAnimating(false);
    }, 400); // Match this timing with the CSS transition
  };

  const goToPreviousStep = () => {
    setAnimating(true);

    setTimeout(() => {
      if (currentStep === 'PROMPT') {
        setCurrentStep('INTRO');
      } else if (currentStep === 'MODELS') {
        setCurrentStep('PROMPT');
      } else if (currentStep === 'RESULTS') {
        setCurrentStep('MODELS');
      }
      setAnimating(false);
    }, 400); // Match this timing with the CSS transition
  };

  // Reset everything and start over
  const handleReset = () => {
    setPrompt('');
    setOutput('');
    setSelectedLLMs([]);
    setUltraLLM(null);
    setIsComplete(false);
    setError(null);
    setCurrentStep('INTRO');
    setProgress(0);
  };

  // Human-readable model names
  const getModelDisplayName = (modelId: string) => {
    const modelNames: { [key: string]: string } = {
      'gpt4o': 'GPT-4o',
      'gpt4turbo': 'GPT-4 Turbo',
      'gpto3mini': 'GPT-3.5',
      'gpto1': 'GPT-o1',
      'claude37': 'Claude 3.5',
      'claude3opus': 'Claude 3 Opus',
      'gemini15': 'Gemini 1.5',
      'llama3': 'Llama 3'
    };

    return modelNames[modelId] || modelId;
  };

  // Calculate total price based on selected models
  const calculatePrice = () => {
    return selectedLLMs.reduce((total, model) => total + (prices[model] || 0), 0);
  };

  // Render model selection cards
  const renderModelOptions = () => {
    return availableModels.map((model) => (
      <div
        key={model}
        className={`border rounded-lg p-3 cursor-pointer transition-all ${selectedLLMs.includes(model)
          ? 'border-cyan-400 bg-cyan-900/30'
          : 'border-gray-700 bg-gray-800/40 hover:bg-gray-800/70'
          }`}
        onClick={() => handleLLMChange(model)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Checkbox
              checked={selectedLLMs.includes(model)}
              onCheckedChange={() => handleLLMChange(model)}
              className="data-[state=checked]:bg-cyan-500 data-[state=checked]:text-white"
            />
            <span className="font-medium text-cyan-100">{getModelDisplayName(model)}</span>
          </div>

          {/* Ultra model selection */}
          {selectedLLMs.includes(model) && (
            <Button
              variant={ultraLLM === model ? "default" : "outline"}
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                handleUltraChange(model);
              }}
              className={ultraLLM === model ? "bg-amber-500 hover:bg-amber-600" : ""}
            >
              {ultraLLM === model ? "Synthesizer ✓" : "Set as Synthesizer"}
            </Button>
          )}
        </div>
        <div className="text-xs text-gray-400 mt-1">
          ${model !== 'llama3' ? (prices[model] || 0).toFixed(5) : '0.00000'}/1K tokens
        </div>
      </div>
    ));
  };

  // Render the step indicator
  const renderStepIndicator = () => {
    // Only show step indicator after the intro step
    if (currentStep === 'INTRO') return null;

    return (
      <div className="mb-8">
        <div className="flex justify-between w-full mb-2">
          <div className={`text-sm font-medium ${currentStep === 'PROMPT' ? 'text-cyan-400' : 'text-gray-500'}`}>
            1. Enter Prompt
          </div>
          <div className={`text-sm font-medium ${currentStep === 'MODELS' ? 'text-cyan-400' : 'text-gray-500'}`}>
            2. Select Models
          </div>
          <div className={`text-sm font-medium ${['PROCESSING', 'RESULTS'].includes(currentStep) ? 'text-cyan-400' : 'text-gray-500'}`}>
            3. Get Results
          </div>
        </div>
        <div className="relative w-full bg-gray-800 h-2 rounded-full overflow-hidden">
          <div
            className="absolute top-0 left-0 h-full bg-gradient-to-r from-cyan-500 to-cyan-400 transition-all duration-300"
            style={{
              width: currentStep === 'PROMPT' ? '33%' :
                currentStep === 'MODELS' ? '66%' : '100%'
            }}
          />
        </div>
      </div>
    );
  };

  // Pricing display component
  const PricingDisplay = () => {
    const totalPrice = calculatePrice();

    return (
      <div className="bg-gradient-to-r from-purple-900 via-cyan-800 to-pink-900 p-3 rounded-lg border border-cyan-500 relative overflow-hidden">
        <div className="relative z-10">
          <h2 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-400 via-cyan-300 to-purple-400 mb-2 flex items-center">
            <Award className="w-5 h-5 mr-2 text-amber-400" />
            Price Estimate
          </h2>

          <div className="bg-black/50 rounded-lg p-3 backdrop-blur-sm">
            <div className="flex justify-center items-center">
              <span className="text-2xl font-bold text-cyan-300">${totalPrice.toFixed(4)}</span>
              <span className="text-sm text-gray-400 ml-2">/ 1000 tokens</span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Render the step content for the PROCESSING step
  const renderProcessingStep = () => {
    return (
      <div className="space-y-6 py-8 px-4 md:px-8 fadeIn">
        <div className="flex flex-col items-center">
          <h2 className="text-xl font-semibold mb-6 text-cyan-200">Processing Your Request</h2>

          <div className="w-full mb-8">
            <Progress value={progress} className="h-2 bg-gray-800" />
            <p className="text-sm text-gray-400 mt-2">{progressMessage}</p>

            {/* Render retry button if there's an error */}
            {error && (
              <div className="mt-4 flex justify-center">
                <Button
                  variant="outline"
                  size="sm"
                  className="flex items-center space-x-2 text-amber-400 border-amber-600 hover:bg-amber-900/30"
                  onClick={handleAnalyze}
                >
                  <RefreshCw className="h-4 w-4 mr-1" />
                  Retry Request
                </Button>
              </div>
            )}
          </div>

          {/* Animated processing indicator */}
          <div className="relative h-32 w-32 mb-6">
            <div className="absolute inset-0 opacity-30 rounded-full border-4 border-cyan-500"></div>
            <div className="absolute inset-0 rounded-full border-t-4 border-cyan-300 animate-spin"></div>
            <div className="absolute inset-2 rounded-full border-b-4 border-pink-500 animate-spin animate-delay-500"></div>
            <div className="absolute inset-4 rounded-full border-r-4 border-green-400 animate-spin animate-delay-1000"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <Brain className="h-12 w-12 text-cyan-400 opacity-80" />
            </div>
          </div>

          <div className="text-center max-w-md">
            <h3 className="text-lg font-medium text-white mb-2">AI Models Working Together</h3>
            <p className="text-gray-400 text-sm">
              Multiple AI models are analyzing your prompt and synthesizing results.
              This typically takes 15-30 seconds depending on complexity.
            </p>
          </div>
        </div>
      </div>
    );
  };

  // Render document upload UI
  const renderDocumentUpload = () => {
    return (
      <div className="mt-6 p-4 border border-cyan-800 rounded-lg bg-black/40">
        <div className="flex items-center mb-4">
          <FileText className="text-cyan-400 mr-2 h-5 w-5" />
          <h3 className="text-lg font-medium text-cyan-300">Document Processing</h3>
          <div className="ml-auto">
            <Checkbox
              checked={isUsingDocuments}
              onCheckedChange={() => toggleDocumentMode()}
              className="data-[state=checked]:bg-cyan-500"
            />
            <span className="ml-2 text-sm text-cyan-200">
              {isUsingDocuments ? 'Using documents' : 'Not using documents'}
            </span>
          </div>
        </div>

        {isUsingDocuments && (
          <>
            <div className="mb-4">
              <p className="text-sm text-gray-400 mb-2">
                Upload documents to analyze alongside your prompt. The AI will reference these documents when generating its response.
              </p>

              {/* Document upload button */}
              <div className="flex items-center">
                <input
                  type="file"
                  onChange={handleFileSelect}
                  className="hidden"
                  ref={fileInputRef}
                  multiple
                  accept=".pdf,.doc,.docx,.txt,.md"
                />
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  variant="outline"
                  size="sm"
                  className="text-cyan-400 border-cyan-700 hover:bg-cyan-900/30 mr-2"
                >
                  <Upload className="h-4 w-4 mr-1" />
                  Select Files
                </Button>

                {documents.length > 0 && (
                  <Button
                    onClick={uploadDocuments}
                    size="sm"
                    className="bg-cyan-700 hover:bg-cyan-600"
                  >
                    Upload {documents.length} Files
                  </Button>
                )}
              </div>
            </div>

            {/* Selected files list */}
            {documents.length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-cyan-300 mb-2">Selected Files:</h4>
                <div className="space-y-2 max-h-40 overflow-y-auto pr-2">
                  {documents.map((file, index) => (
                    <div key={index} className="flex items-center justify-between bg-black/60 p-2 rounded-md">
                      <div className="flex items-center">
                        <File className="h-4 w-4 text-cyan-500 mr-2" />
                        <span className="text-sm text-gray-300 truncate max-w-[200px]">{file.name}</span>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0 text-gray-500 hover:text-red-400"
                        onClick={() => removeDocument(index)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Uploaded files list */}
            {uploadedDocuments.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-cyan-300 mb-2">Uploaded Documents:</h4>
                <div className="space-y-2 max-h-40 overflow-y-auto pr-2">
                  {uploadedDocuments.map((doc, index) => (
                    <div key={index} className="flex items-center justify-between bg-black/60 p-2 rounded-md border border-green-900/30">
                      <div className="flex items-center">
                        <Check className="h-4 w-4 text-green-500 mr-2" />
                        <span className="text-sm text-gray-300 truncate max-w-[250px]">{doc.name}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    );
  };

  // Render content based on current step
  const renderStepContent = () => {
    switch (currentStep) {
      case 'INTRO':
        return (
          <div className="space-y-6 py-6 fadeIn">
            <div className="text-center">
              <h1 className="text-4xl md:text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-pink-500 via-cyan-500 to-green-500 mb-4">
                UltrAI
              </h1>
              <div className="w-16 h-1 bg-gradient-to-r from-pink-500 via-cyan-500 to-green-500 mx-auto mb-6"></div>
            </div>

            <div className="border-2 border-cyan-700 rounded-lg p-6 bg-black/50 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-900/20 to-purple-900/20"></div>
              <div className="relative z-10">
                <div className="flex items-center mb-4">
                  <div className="w-8 h-8 rounded-full bg-cyan-700 flex items-center justify-center mr-3 text-white font-bold">1</div>
                  <h2 className="text-2xl font-bold text-cyan-400">Welcome to UltrAI</h2>
                </div>
                <p className="text-lg text-cyan-100 mb-4">
                  UltrAI is more powerful than other AI modules because it uses multiple premium AI Programs to provide you with a product that is formed from the best of multiple models.
                </p>
                <p className="text-lg text-cyan-100 mb-6">
                  We are here to make it easy for everyone to use AI to make their WorkLife/SchoolLife/LifeLife more efficient and happy.
                </p>
                <p className="text-xl text-cyan-300 font-medium mb-4">
                  So what do you want to analyze or know more about?
                </p>
                <div className="pt-4">
                  <Button
                    onClick={goToNextStep}
                    size="lg"
                    className="font-medium text-lg bg-gradient-to-r from-cyan-600 to-cyan-700 hover:from-cyan-500 hover:to-cyan-600 w-full"
                  >
                    <Zap className="mr-2 h-5 w-5" />
                    Get Started
                  </Button>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
              <div className="bg-black/40 border border-cyan-900 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <Brain className="w-5 h-5 text-pink-400 mr-2" />
                  <h3 className="text-lg font-semibold text-cyan-300">Multiple Models</h3>
                </div>
                <p className="text-gray-300 text-sm">
                  Get insights from multiple AI models at once for better perspectives.
                </p>
              </div>
              <div className="bg-black/40 border border-cyan-900 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <Feather className="w-5 h-5 text-yellow-400 mr-2" />
                  <h3 className="text-lg font-semibold text-cyan-300">Expert Synthesis</h3>
                </div>
                <p className="text-gray-300 text-sm">
                  One model combines all perspectives into a unified response.
                </p>
              </div>
              <div className="bg-black/40 border border-cyan-900 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <Shield className="w-5 h-5 text-green-400 mr-2" />
                  <h3 className="text-lg font-semibold text-cyan-300">More Accurate</h3>
                </div>
                <p className="text-gray-300 text-sm">
                  Multiple models reduce errors and provide well-rounded answers.
                </p>
              </div>
            </div>
          </div>
        );

      case 'PROMPT':
        return (
          <div className={`space-y-4 ${animating ? 'fadeOut' : 'fadeIn'}`}>
            <div className="border-2 border-cyan-700 rounded-lg p-6 bg-black/50 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-900/20 to-purple-900/20"></div>
              <div className="relative z-10">
                <div className="flex items-center mb-4">
                  <div className="w-8 h-8 rounded-full bg-cyan-700 flex items-center justify-center mr-3 text-white font-bold">1</div>
                  <h2 className="text-2xl font-bold text-cyan-400">What would you like analyzed?</h2>
                </div>
                <div className="space-y-2">
                  <Label className="text-lg text-cyan-200">Enter your prompt or question</Label>
                  <Textarea
                    placeholder="Describe what you want multiple AI models to analyze. Try things like 'Explain quantum computing', 'Is AI dangerous?', or 'What are the ethical implications of genetic engineering?'"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    className="min-h-[200px] text-lg p-4 leading-relaxed bg-gray-900 border-gray-700 text-cyan-50"
                  />
                </div>
              </div>
            </div>
            <div className="pt-4 flex justify-between">
              <Button
                onClick={goToPreviousStep}
                variant="outline"
                size="lg"
                className="border-cyan-700 text-cyan-400 hover:bg-cyan-950"
              >
                Back
              </Button>
              <Button
                onClick={goToNextStep}
                size="lg"
                className="font-medium text-lg bg-gradient-to-r from-cyan-600 to-cyan-700 hover:from-cyan-500 hover:to-cyan-600"
              >
                Next: Select AI Models
              </Button>
            </div>
          </div>
        );

      case 'MODELS':
        return (
          <div className={`space-y-4 ${animating ? 'fadeOut' : 'fadeIn'}`}>
            <div className="border-2 border-cyan-700 rounded-lg p-6 bg-black/50 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-900/20 to-purple-900/20"></div>
              <div className="relative z-10">
                <div className="flex items-center mb-4">
                  <div className="w-8 h-8 rounded-full bg-cyan-700 flex items-center justify-center mr-3 text-white font-bold">2</div>
                  <h2 className="text-2xl font-bold text-cyan-400">Select AI models</h2>
                </div>
                <p className="text-cyan-100 mb-4">
                  Choose at least 2 AI models to analyze your prompt. Then select one model to be the "Synthesizer"
                  that will combine all the insights.
                </p>

                <div className="space-y-2">
                  <Label className="text-lg text-cyan-200">Available AI Models</Label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2">
                    {renderModelOptions()}
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-4">
              <PricingDisplay />
            </div>

            <div className="pt-4 flex justify-between">
              <Button
                onClick={goToPreviousStep}
                variant="outline"
                size="lg"
                className="border-cyan-700 text-cyan-400 hover:bg-cyan-950"
              >
                Back
              </Button>
              <Button
                onClick={goToNextStep}
                size="lg"
                className="font-medium text-lg bg-gradient-to-r from-cyan-600 to-cyan-700 hover:from-cyan-500 hover:to-cyan-600"
                disabled={selectedLLMs.length < 2 || !ultraLLM}
              >
                Analyze Now
              </Button>
            </div>
          </div>
        );

      case 'PROCESSING':
        return renderProcessingStep();

      case 'RESULTS':
        return (
          <div className="space-y-4 fadeIn">
            <div className="border-2 border-cyan-700 rounded-lg p-6 bg-black/50 relative overflow-hidden" ref={outputRef}>
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-900/20 to-purple-900/20"></div>
              <div className="relative z-10">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <div className="w-8 h-8 rounded-full bg-cyan-700 flex items-center justify-center mr-3 text-white font-bold">3</div>
                    <h2 className="text-2xl font-bold text-cyan-400">Analysis Results</h2>
                  </div>

                  {/* Share button */}
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-purple-400 border-purple-800 hover:bg-purple-900/30"
                    onClick={() => {
                      const currentItem: HistoryItem = {
                        id: Date.now().toString(),
                        prompt,
                        output,
                        models: selectedLLMs,
                        ultraModel: ultraLLM || '',
                        timestamp: new Date().toISOString(),
                        usingDocuments: isUsingDocuments,
                        documents: isUsingDocuments ? uploadedDocuments : undefined
                      };
                      shareHistoryItem(currentItem);
                    }}
                  >
                    <Share2 className="h-4 w-4 mr-1" />
                    Share
                  </Button>
                </div>

                {isCached && (
                  <div className="mb-4 bg-blue-900/20 border border-blue-800 rounded-lg p-3 text-blue-300 flex items-center">
                    <Clock className="h-5 w-5 mr-2" />
                    <span>Results retrieved from cache for faster response.</span>
                  </div>
                )}

                <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 mt-4">
                  <div className="prose prose-invert max-w-none">
                    <div className="whitespace-pre-line text-lg leading-relaxed text-cyan-50">
                      {output}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="pt-6 flex justify-between">
              <Button
                onClick={handleReset}
                variant="outline"
                size="lg"
                className="border-cyan-700 text-cyan-400 hover:bg-cyan-950"
              >
                Start New Analysis
              </Button>
            </div>
          </div>
        );
    }
  };

  // Render history panel
  const renderHistoryPanel = () => {
    if (!showHistory) return null;

    return (
      <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
        <div className="bg-gray-900 border-2 border-cyan-700 rounded-lg max-w-3xl w-full max-h-[90vh] flex flex-col">
          <div className="p-4 border-b border-cyan-800 flex justify-between items-center">
            <h2 className="text-xl font-bold text-cyan-400 flex items-center">
              <History className="mr-2 h-5 w-5" />
              Interaction History
            </h2>
            <div className="flex items-center">
              {history.length > 0 && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={clearHistory}
                  className="mr-2 text-red-400 border-red-800 hover:bg-red-900/30"
                >
                  <Trash2 className="h-4 w-4 mr-1" />
                  Clear All
                </Button>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowHistory(false)}
                className="text-gray-400"
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            {history.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No saved interactions yet.</p>
                <p className="text-sm mt-2">Complete an analysis to save it here.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {history.map((item) => (
                  <div
                    key={item.id}
                    className="border border-gray-800 rounded-lg p-3 bg-black/40 hover:bg-gray-900/60 transition-colors"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-medium text-cyan-300 truncate max-w-[70%]">
                        {item.prompt.substring(0, 60)}{item.prompt.length > 60 ? '...' : ''}
                      </h3>
                      <div className="flex items-center">
                        <span className="text-xs text-gray-500 mr-2">
                          {new Date(item.timestamp).toLocaleString()}
                        </span>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 w-7 p-0 text-blue-400 hover:text-blue-300 hover:bg-blue-950/30"
                          onClick={() => shareHistoryItem(item)}
                          title="Share"
                        >
                          <Share2 className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 w-7 p-0 text-cyan-400 hover:text-cyan-300 hover:bg-cyan-950/30"
                          onClick={() => loadFromHistory(item)}
                        >
                          <FileText className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 w-7 p-0 text-red-400 hover:text-red-300 hover:bg-red-950/30"
                          onClick={() => deleteHistoryItem(item.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>

                    <div className="text-sm text-gray-400 mb-2 truncate">
                      {item.output.substring(0, 80)}{item.output.length > 80 ? '...' : ''}
                    </div>

                    <div className="flex flex-wrap items-center mt-2 text-xs">
                      <span className="bg-cyan-900/40 text-cyan-300 px-2 py-1 rounded-full mr-2 mb-1">
                        {(item.models || []).length} models
                      </span>
                      {item.usingDocuments && (
                        <span className="bg-blue-900/40 text-blue-300 px-2 py-1 rounded-full mr-2 mb-1">
                          {(item.documents || []).length} documents
                        </span>
                      )}
                      {/* Show indicator if this item has been shared */}
                      {sharedItems.some(shared => shared.id === item.id) && (
                        <span className="bg-purple-900/40 text-purple-300 px-2 py-1 rounded-full mr-2 mb-1 flex items-center">
                          <Share2 className="h-3 w-3 mr-1" /> Shared
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Render share dialog
  const renderShareDialog = () => {
    if (!showShareDialog || !shareDialogItem) return null;

    return (
      <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
        <div className="bg-gray-900 border-2 border-cyan-700 rounded-lg max-w-md w-full p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-cyan-400 flex items-center">
              <Share2 className="mr-2 h-5 w-5" />
              Share Analysis
            </h2>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowShareDialog(false)}
              className="text-gray-400"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>

          <div className="space-y-4">
            <p className="text-gray-300">
              Share this analysis with others using the link below:
            </p>

            <div className="flex items-center">
              <div className="bg-black/60 border border-gray-700 rounded-lg p-3 flex-1 overflow-hidden">
                <p className="text-cyan-300 truncate">{shareUrl}</p>
              </div>
              <Button
                variant="outline"
                size="sm"
                className={`ml-2 ${copySuccess ? 'text-green-400 border-green-700' : 'text-cyan-400 border-cyan-700'}`}
                onClick={copyToClipboard}
              >
                {copySuccess ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              </Button>
            </div>

            <div className="pt-2">
              <p className="text-sm text-gray-400">
                Anyone with this link can view this analysis without needing an account.
              </p>
            </div>

            <div className="bg-gray-800/60 border border-gray-700 rounded-lg p-3 mt-4">
              <div className="flex items-center mb-2">
                <Link className="text-cyan-400 mr-2 h-4 w-4" />
                <h3 className="text-cyan-300 font-medium">Shared Analysis</h3>
              </div>
              <p className="text-gray-400 text-sm mb-1 truncate">
                <span className="text-gray-500">Prompt: </span>
                {shareDialogItem.prompt.substring(0, 100)}{shareDialogItem.prompt.length > 100 ? '...' : ''}
              </p>
              <p className="text-gray-400 text-xs">
                <span className="text-gray-500">Using models: </span>
                {shareDialogItem.models.map(model => model).join(', ')}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white p-4 md:p-6">
      <div className="max-w-4xl mx-auto bg-black border-4 border-cyan-700 rounded-lg shadow-2xl shadow-cyan-500/20 p-6 md:p-8 relative overflow-hidden">
        {/* Offline banner */}
        {renderOfflineBanner()}

        {/* Step indicator */}
        {renderStepIndicator()}

        {/* History button - shown in all steps */}
        <div className="absolute top-4 right-4 flex space-x-2">
          <Button
            variant="outline"
            size="sm"
            className="text-cyan-400 border-cyan-800 hover:bg-cyan-900/30"
            onClick={() => setShowHistory(true)}
          >
            <History className="h-4 w-4 mr-1" />
            History{history.length > 0 ? ` (${history.length})` : ''}
          </Button>

          {/* Save button - only shown in RESULTS step */}
          {currentStep === 'RESULTS' && (
            <Button
              variant="outline"
              size="sm"
              className="text-green-400 border-green-800 hover:bg-green-900/30"
              onClick={saveToHistory}
            >
              <Save className="h-4 w-4 mr-1" />
              Save
            </Button>
          )}
        </div>

        {/* Error display */}
        {error && (
          <div className="mb-6 bg-red-900/20 border border-red-800 rounded-lg p-4 text-red-400">
            {error}
          </div>
        )}

        {/* Step content */}
        {renderStepContent()}

        {/* Document upload UI - shown in PROMPT step when online */}
        {currentStep === 'PROMPT' && !isOffline && renderDocumentUpload()}

        {/* Footer note */}
        <div className="mt-6 text-center text-sm text-gray-500">
          Ultra AI combines multiple AI models to provide more balanced and thorough analysis.
          {isOffline && " (Offline mode available for viewing saved analyses)"}
        </div>
      </div>

      {/* History panel */}
      {renderHistoryPanel()}

      {/* Share dialog */}
      {renderShareDialog()}

      {/* Add styles for animations */}
      <style dangerouslySetInnerHTML={{
        __html: `
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }

        @keyframes fadeOut {
          from { opacity: 1; transform: translateY(0); }
          to { opacity: 0; transform: translateY(-20px); }
        }

        .fadeIn {
          animation: fadeIn 0.5s ease-out forwards;
        }

        .fadeOut {
          animation: fadeOut 0.4s ease-in forwards;
        }
      ` }} />
    </div>
  );
}