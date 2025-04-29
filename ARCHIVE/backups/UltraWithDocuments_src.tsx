'use client'

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Checkbox } from './ui/checkbox';
import { Progress } from './ui/progress';
import { Zap, Award, Brain, Feather, Shield, FileText, Users, Network, Clock, Lightbulb, RefreshCw, Upload, X, File, Check, History, Save, Trash2, WifiOff, Share2, Copy, Link, ExternalLink, DollarSign } from 'lucide-react';
import AnimatedLogoV3 from './AnimatedLogoV3';

// Simplified API URL
const API_URL = import.meta.env.VITE_API_URL || 'https://ultra-api.vercel.app';

// Step definitions - expanded to include 7 distinct steps with clear progression
type Step = 'INTRO' | 'PROMPT' | 'DOCUMENTS' | 'MODELS' | 'ANALYSIS_TYPE' | 'PROCESSING' | 'RESULTS';

// Step information with titles and descriptions
const stepInfo: Record<Step, { title: string, description: string }> = {
  'INTRO': {
    title: 'Welcome to Ultra AI',
    description: 'Experience AI intelligence multiplication through our multi-model analysis system.'
  },
  'PROMPT': {
    title: 'Enter Your Prompt',
    description: 'What would you like Ultra to analyze? Be specific for better results.'
  },
  'DOCUMENTS': {
    title: 'Add Context',
    description: 'Upload documents to provide additional context for your analysis.'
  },
  'MODELS': {
    title: 'Select AI Models',
    description: 'Choose which AI models to use for your analysis. Each model brings unique strengths.'
  },
  'ANALYSIS_TYPE': {
    title: 'Analysis Method',
    description: 'Select how Ultra should approach your query.'
  },
  'PROCESSING': {
    title: 'Processing',
    description: 'Ultra is analyzing your query across multiple models.'
  },
  'RESULTS': {
    title: 'Results',
    description: 'Review your analysis from multiple AI perspectives.'
  }
};

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

// Analysis pattern options
const analysisTypes = [
  { id: 'confidence', name: 'Confidence', description: 'Standard analysis with confidence scoring', icon: Shield },
  { id: 'critique', name: 'Critique', description: 'Critical evaluation with pros and cons', icon: FileText },
  { id: 'perspective', name: 'Perspective', description: 'Multiple viewpoints on the topic', icon: Users },
  { id: 'fact_check', name: 'Fact Check', description: 'Verification of factual claims', icon: Check },
  { id: 'scenario', name: 'Scenario', description: 'Future scenario exploration', icon: Network }
];

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

  // Add state for floating price component
  const [floatingPriceVisible, setFloatingPriceVisible] = useState<boolean>(true);
  const [selectedAnalysisType, setSelectedAnalysisType] = useState<string>('confidence');
  const [floatingPricePosition, setFloatingPricePosition] = useState({ top: 0, right: 20 });
  const floatingPriceRef = useRef<HTMLDivElement>(null);

  // Add a ref for the main container
  const containerRef = useRef<HTMLDivElement>(null);

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
        // Use mock data instead of API call
        const mockModels = ['gpt4o', 'gpt4turbo', 'gpto3mini', 'gpto1', 'claude37', 'claude3opus', 'gemini15', 'llama3'];
        setAvailableModels(mockModels);

        // Previous API call code:
        // const response = await axiosWithRetry.get(`/api/available-models`);
        // if (response.data && response.data.available_models) {
        //   setAvailableModels(response.data.available_models);
        // } else {
        //   setError('Could not retrieve available models');
        // }
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

  // Handle file selection with size validation
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = e.target.files;
    if (fileList) {
      // Check if any file exceeds the size limit (4MB for cloud environment)
      const MAX_FILE_SIZE = 4 * 1024 * 1024; // 4MB in bytes
      const validFiles: File[] = [];
      let hasOversize = false;

      Array.from(fileList).forEach(file => {
        if (file.size > MAX_FILE_SIZE) {
          hasOversize = true;
        } else {
          validFiles.push(file);
        }
      });

      if (hasOversize) {
        setError(`Some files exceed the 4MB size limit. Only files smaller than 4MB will be uploaded.`);
      }

      if (validFiles.length > 0) {
        setDocuments(prev => [...prev, ...validFiles]);
      }
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

  // Upload documents to server with chunking for large files
  const uploadDocuments = async () => {
    if (documents.length === 0) return;

    setError(null);

    // Simulate document uploads with mock data
    for (let i = 0; i < documents.length; i++) {
      const file = documents[i];

      try {
        // Track upload progress
        setUploadProgress(prev => ({ ...prev, [file.name]: 0 }));

        // Simulate progress updates
        for (let progress = 0; progress <= 100; progress += 10) {
          setUploadProgress(prev => ({ ...prev, [file.name]: progress }));
          await new Promise(r => setTimeout(r, 100)); // Delay for visual effect
        }

        // Add mock document ID
        const mockDocId = `doc-${Math.random().toString(36).substring(2, 9)}`;
        setUploadedDocuments(prev => [...prev, { id: mockDocId, name: file.name }]);

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

  // Track scroll position to update floating price position
  useEffect(() => {
    const handleScroll = () => {
      if (containerRef.current && floatingPriceRef.current) {
        const containerRect = containerRef.current.getBoundingClientRect();
        const scrollY = window.scrollY;

        // Keep price visible when container is in view
        if (containerRect.top < window.innerHeight && containerRect.bottom > 0) {
          const newTop = Math.max(
            20, // Minimum top position
            Math.min(
              window.innerHeight - floatingPriceRef.current.offsetHeight - 20, // Maximum top position
              scrollY - containerRect.top + 100 // Dynamic position that follows scroll
            )
          );

          setFloatingPricePosition({
            top: newTop,
            right: 20
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
    const steps: Step[] = ['INTRO', 'PROMPT', 'DOCUMENTS', 'MODELS', 'ANALYSIS_TYPE', 'PROCESSING', 'RESULTS'];
    const currentIndex = steps.indexOf(currentStep);
    return Math.round((currentIndex / (steps.length - 1)) * 100);
  };

  // Handle analysis type selection
  const handleAnalysisTypeChange = (type: string) => {
    setSelectedAnalysisType(type);
  };

  // Handle step navigation
  const goToNextStep = () => {
    const steps: Step[] = ['INTRO', 'PROMPT', 'DOCUMENTS', 'MODELS', 'ANALYSIS_TYPE', 'PROCESSING', 'RESULTS'];
    const currentIndex = steps.indexOf(currentStep);
    if (currentIndex < steps.length - 1) {
      setCurrentStep(steps[currentIndex + 1]);
      setProgress(calculateProgress());
    }
  };

  const goToPreviousStep = () => {
    const steps: Step[] = ['INTRO', 'PROMPT', 'DOCUMENTS', 'MODELS', 'ANALYSIS_TYPE', 'PROCESSING', 'RESULTS'];
    const currentIndex = steps.indexOf(currentStep);
    if (currentIndex > 0) {
      setCurrentStep(steps[currentIndex - 1]);
      setProgress(calculateProgress());
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
      case 'PROCESSING':
        return isComplete; // Wait until processing is done
      default:
        return true;
    }
  };

  // Modify the analyze function to use the updated step flow
  const handleAnalyzeClick = async () => {
    if (currentStep === 'ANALYSIS_TYPE') {
      setCurrentStep('PROCESSING');
      setProgress(calculateProgress());
      await handleAnalyze();
    } else if (currentStep === 'PROCESSING' && isComplete) {
      setCurrentStep('RESULTS');
      setProgress(calculateProgress());
    }
  };

  // Main function to analyze the prompt
  const handleAnalyze = async () => {
    // Skip if offline
    if (isOffline) {
      setError('You are offline. Please connect to the internet to use Ultra AI.');
      return;
    }

    try {
      setError(null);
      setIsProcessing(true);
      setIsComplete(false);
      setIsCached(false);
      setOutput('');
      setAnimating(true);

      // Upload any documents if we're using document context
      if (isUsingDocuments && documents.length > 0) {
        updateProgress(10, 'Uploading documents...');
        await uploadDocuments();
      }

      // Set up request payload
      const payload = {
        prompt,
        models: selectedLLMs,
        ultra_model: ultraLLM || selectedLLMs[0],
        analysis_type: selectedAnalysisType,
        documents: isUsingDocuments ? uploadedDocuments.map(doc => doc.id) : []
      };

      // Simulate progress updates
      updateProgress(20, 'Analyzing prompt...');
      await new Promise(r => setTimeout(r, 500));
      updateProgress(40, 'Processing with models...');
      await new Promise(r => setTimeout(r, 800));
      updateProgress(60, 'Generating insights...');
      await new Promise(r => setTimeout(r, 700));
      updateProgress(80, 'Comparing results...');
      await new Promise(r => setTimeout(r, 500));
      updateProgress(100, 'Finalizing output...');
      await new Promise(r => setTimeout(r, 300));

      // Generate mock response instead of API call
      const mockResponse = {
        output: `# Ultra AI Analysis

## Summary
Your prompt "${prompt}" has been analyzed by ${selectedLLMs.length} models.

## Key Insights
* This is a simulated response since the backend API is not available
* The models used were: ${selectedLLMs.join(', ')}
* Ultra model: ${ultraLLM || selectedLLMs[0]}
* Analysis type: ${selectedAnalysisType}
${isUsingDocuments ? `* Documents used: ${uploadedDocuments.map(doc => doc.name).join(', ')}` : ''}

## Detailed Analysis
This is a mock response created when deploying to Vercel. In a production environment, this would contain the actual analysis from the selected AI models.

## Confidence Score
High: The answer is accurate based on the available information and general knowledge.

## Sources
- Mock data for demonstration purposes
- Models: ${selectedLLMs.join(', ')}`,
        cached: false
      };

      // Set output and finalize
      setOutput(mockResponse.output);
      setIsCached(mockResponse.cached || false);
      setIsProcessing(false);
      setIsComplete(true);

      // Save to history
      saveToHistory();

      // Transition to results step
      setCurrentStep('RESULTS');
      setAnimating(false);

    } catch (err: any) {
      setError(`Analysis failed: ${err.message}`);
      setIsProcessing(false);
      setAnimating(false);
    }
  };

  // Function to share an analysis
  const shareAnalysis = async () => {
    if (isOffline) {
      setError('Cannot share while offline. Please reconnect to the internet.');
      return;
    }

    try {
      // Create a shareable item from current analysis
      const shareItem: HistoryItem = {
        id: `share-${Date.now()}`,
        prompt,
        output,
        models: selectedLLMs,
        ultraModel: ultraLLM || '',
        timestamp: new Date().toISOString(),
        usingDocuments: isUsingDocuments,
        documents: uploadedDocuments
      };

      // Generate a share ID
      const shareId = `s-${Math.random().toString(36).substring(2, 9)}`;

      // Create share URL
      const baseUrl = window.location.origin;
      const shareUrl = `${baseUrl}/share/${shareId}`;

      // Save to API if available
      try {
        await axiosWithRetry.post('/api/share', {
          shareId,
          content: shareItem
        });
      } catch (err) {
        console.error('Error saving share to API:', err);
        // Continue with local storage fallback
      }

      // Save locally too as backup
      const newShareItem: ShareItem = {
        ...shareItem,
        shareId,
        shareUrl,
        createdAt: new Date().toISOString()
      };

      const updatedSharedItems = [...sharedItems, newShareItem];
      setSharedItems(updatedSharedItems);
      localStorage.setItem('ultraAiSharedItems', JSON.stringify(updatedSharedItems));

      // Set share URL and dialog
      setShareUrl(shareUrl);
      setShareDialogItem(shareItem);
      setShowShareDialog(true);
    } catch (err) {
      console.error('Error creating share:', err);
      setError('Failed to create shareable link. Please try again.');
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
          <div className={`text-sm font-medium ${currentStep === 'DOCUMENTS' ? 'text-cyan-400' : 'text-gray-500'}`}>
            2. Add Context
          </div>
          <div className={`text-sm font-medium ${currentStep === 'MODELS' ? 'text-cyan-400' : 'text-gray-500'}`}>
            3. Select AI Models
          </div>
          <div className={`text-sm font-medium ${currentStep === 'ANALYSIS_TYPE' ? 'text-cyan-400' : 'text-gray-500'}`}>
            4. Analysis Method
          </div>
          <div className={`text-sm font-medium ${['PROCESSING', 'RESULTS'].includes(currentStep) ? 'text-cyan-400' : 'text-gray-500'}`}>
            5. Get Results
          </div>
        </div>
        <div className="relative w-full bg-gray-800 h-2 rounded-full overflow-hidden">
          <div
            className="absolute top-0 left-0 h-full bg-gradient-to-r from-cyan-500 to-cyan-400 transition-all duration-300"
            style={{
              width: currentStep === 'PROMPT' ? '33%' :
                currentStep === 'DOCUMENTS' ? '66%' :
                  currentStep === 'MODELS' ? '100%' : '100%'
            }}
          />
        </div>
      </div>
    );
  };

  // Pricing display component
  const PricingDisplay = () => {
    const totalPrice = selectedLLMs.reduce((total, model) => total + (prices[model] || 0), 0);

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
    if (isOffline) return null;

    return (
      <div className="mt-6">
        <div className="flex items-center space-x-2 mb-2">
          <Checkbox
            id="useDocuments"
            checked={isUsingDocuments}
            onCheckedChange={(checked) => setIsUsingDocuments(checked as boolean)}
            disabled={isProcessing}
          />
          <Label htmlFor="useDocuments" className="text-cyan-300">
            Include documents in your analysis
          </Label>
        </div>

        {isUsingDocuments && (
          <div className="space-y-4 mt-3">
            <div
              className="border-2 border-dashed border-cyan-700 rounded-lg p-6 text-center cursor-pointer hover:bg-cyan-900/10 transition-colors"
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload className="h-10 w-10 text-cyan-700 mx-auto mb-3" />
              <p className="text-cyan-100">
                Drag and drop files here, or click to select
              </p>
              <p className="text-xs text-cyan-500 mt-1">
                Supports PDF, TXT, DOCX, and more (max 4MB per file)
              </p>
              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                multiple
                onChange={handleFileSelect}
                disabled={isProcessing}
              />
            </div>

            {/* Document List */}
            {documents.length > 0 && (
              <div className="mt-4">
                <h3 className="font-medium text-cyan-300 mb-2">
                  Selected Documents ({documents.length})
                </h3>
                <div className="space-y-2">
                  {documents.map((doc, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between bg-cyan-900/20 p-3 rounded-md"
                    >
                      <div className="flex items-center space-x-3">
                        <File className="h-5 w-5 text-cyan-400" />
                        <div>
                          <p className="text-sm font-medium text-cyan-100">{doc.name}</p>
                          <p className="text-xs text-cyan-500">
                            {(doc.size / 1024).toFixed(1)} KB
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center">
                        {uploadProgress[doc.name] !== undefined && uploadProgress[doc.name] < 100 ? (
                          <div className="w-16">
                            <Progress value={uploadProgress[doc.name]} size="sm" />
                          </div>
                        ) : uploadProgress[doc.name] === 100 ? (
                          <Check className="h-5 w-5 text-green-500" />
                        ) : (
                          <button
                            onClick={() => removeDocument(index)}
                            className="text-cyan-500 hover:text-red-500"
                          >
                            <X className="h-5 w-5" />
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Uploaded Documents */}
            {uploadedDocuments.length > 0 && (
              <div className="mt-4">
                <h3 className="font-medium text-cyan-300 mb-2">
                  Uploaded Documents ({uploadedDocuments.length})
                </h3>
                <div className="space-y-2">
                  {uploadedDocuments.map((doc) => (
                    <div
                      key={doc.id}
                      className="flex items-center justify-between bg-green-900/20 p-3 rounded-md"
                    >
                      <div className="flex items-center space-x-3">
                        <File className="h-5 w-5 text-green-500" />
                        <p className="text-sm font-medium text-cyan-100">{doc.name}</p>
                      </div>
                      <Check className="h-5 w-5 text-green-500" />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {documents.length > 0 && (
              <div className="flex justify-center mt-4">
                <Button
                  onClick={uploadDocuments}
                  disabled={isProcessing || documents.length === 0}
                  className="bg-cyan-700 hover:bg-cyan-600 text-white"
                >
                  Upload Selected Documents
                </Button>
              </div>
            )}
          </div>
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
                  Ultra multiplies intelligence by analyzing your prompt with multiple AI models simultaneously,
                  then synthesizing the insights into a comprehensive response.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                  <div className="bg-blue-50 dark:bg-blue-900/30 p-4 rounded-lg">
                    <Brain className="w-8 h-8 text-blue-500 mb-2 mx-auto" />
                    <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-1">Multiple Models</h3>
                  </div>

                  <div className="bg-purple-50 dark:bg-purple-900/30 p-4 rounded-lg">
                    <Lightbulb className="w-8 h-8 text-purple-500 mb-2 mx-auto" />
                    <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-1">Enhanced Analysis</h3>
                  </div>

                  <div className="bg-green-50 dark:bg-green-900/30 p-4 rounded-lg">
                    <FileText className="w-8 h-8 text-green-500 mb-2 mx-auto" />
                    <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-1">Document Context</h3>
                  </div>
                </div>
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
                  <h2 className="text-2xl font-bold text-cyan-400">What would you like Ultra to analyze?</h2>
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

      case 'DOCUMENTS':
        return renderDocumentUpload();

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
                    {availableModels.map((model) => {
                      const isSelected = selectedLLMs.includes(model);
                      const isUltra = ultraLLM === model;

                      return (
                        <div
                          key={model}
                          className={`
                            border rounded-lg p-4 cursor-pointer transition-all
                            ${isSelected
                              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                              : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'}
                            ${isUltra ? 'ring-2 ring-purple-500' : ''}
                          `}
                          onClick={() => handleLLMChange(model)}
                        >
                          <div className="flex justify-between items-center">
                            <div className="flex items-center gap-2">
                              <Checkbox
                                checked={isSelected}
                                onCheckedChange={() => handleLLMChange(model)}
                                disabled={isProcessing || isOffline}
                                className="data-[state=checked]:bg-blue-600"
                              />
                              <span className="font-medium text-gray-800 dark:text-gray-200">
                                {model.charAt(0).toUpperCase() + model.slice(1)}
                              </span>
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              ${prices[model]?.toFixed(4)} / 1K tokens
                            </div>
                          </div>

                          <div className="mt-4 flex justify-between items-center">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleUltraChange(model);
                              }}
                              disabled={!isSelected || isProcessing || isOffline}
                              className={`
                                text-xs font-medium px-3 py-1 rounded-full
                                ${isUltra
                                  ? 'bg-purple-600 text-white'
                                  : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-purple-200'}
                                ${!isSelected ? 'opacity-50 cursor-not-allowed' : ''}
                              `}
                            >
                              {isUltra ? 'Ultra Model ✓' : 'Set as Ultra Model'}
                            </button>
                          </div>
                        </div>
                      );
                    })}
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

      case 'ANALYSIS_TYPE':
        return (
          <div className="space-y-6">
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-800 dark:text-white mb-2">
                Select Analysis Method
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Choose how Ultra should approach your query.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {analysisTypes.map((type) => {
                  const isSelected = selectedAnalysisType === type.id;
                  const Icon = type.icon;

                  return (
                    <div
                      key={type.id}
                      className={`
                        border rounded-lg p-4 cursor-pointer transition-all
                        ${isSelected
                          ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'}
                      `}
                      onClick={() => handleAnalysisTypeChange(type.id)}
                    >
                      <div className="flex flex-col items-center text-center">
                        <div className={`p-3 rounded-full mb-3 ${isSelected ? 'bg-purple-100 dark:bg-purple-900/30' : 'bg-gray-100 dark:bg-gray-800'}`}>
                          <Icon className={`h-6 w-6 ${isSelected ? 'text-purple-600' : 'text-gray-500 dark:text-gray-400'}`} />
                        </div>
                        <h4 className="font-medium text-gray-800 dark:text-gray-200 mb-1">
                          {type.name}
                        </h4>
                        <p className="text-xs text-gray-600 dark:text-gray-400">
                          {type.description}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        );

      case 'PROCESSING':
        return renderProcessingStep();

      case 'RESULTS':
        return (
          <div className="space-y-6" ref={outputRef}>
            <div className="mb-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-medium text-gray-800 dark:text-white">
                  Ultra Analysis Results
                </h3>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => saveToHistory()}
                    disabled={isOffline}
                    className="text-sm text-blue-600 dark:text-blue-400 flex items-center gap-1 hover:underline"
                  >
                    <Save className="h-4 w-4" />
                    Save
                  </button>
                  <button
                    onClick={() => shareAnalysis()}
                    disabled={isOffline}
                    className="text-sm text-purple-600 dark:text-purple-400 flex items-center gap-1 hover:underline"
                  >
                    <Share2 className="h-4 w-4" />
                    Share
                  </button>
                </div>
              </div>

              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-4">
                <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-2">Your Prompt</h4>
                <p className="text-gray-800 dark:text-gray-200">{prompt}</p>
              </div>

              <div className="prose prose-lg dark:prose-invert max-w-none">
                {output && (
                  <div className="whitespace-pre-wrap rounded-lg border border-gray-200 dark:border-gray-700 p-4">
                    {output}
                  </div>
                )}
              </div>
            </div>

            <div className="flex flex-col md:flex-row gap-4 mt-8">
              <Button
                onClick={() => {
                  setCurrentStep('PROMPT');
                  setPrompt('');
                  setSelectedLLMs([]);
                  setUltraLLM(null);
                  setDocuments([]);
                  setUploadedDocuments([]);
                  setOutput('');
                  setIsComplete(false);
                  setProgress(0);
                  setIsUsingDocuments(false);
                }}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Start New Analysis
              </Button>

              <Button
                onClick={() => setShowHistory(true)}
                variant="outline"
                className="border-gray-300 dark:border-gray-700"
              >
                <History className="h-4 w-4 mr-2" />
                View History
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

  // Render floating price component
  const renderFloatingPrice = () => {
    if (!floatingPriceVisible) return null;

    return (
      <div
        ref={floatingPriceRef}
        className="fixed shadow-lg rounded-lg bg-white dark:bg-gray-800 p-4 z-50 border border-gray-200 dark:border-gray-700 transition-all duration-300"
        style={{
          top: `${floatingPricePosition.top}px`,
          right: `${floatingPricePosition.right}px`,
          opacity: isOffline ? 0.5 : 1
        }}
      >
        <div className="flex flex-col gap-2">
          <h3 className="font-medium text-sm text-gray-700 dark:text-gray-300">Estimated Cost</h3>
          <div className="flex items-center gap-2">
            <DollarSign className="w-4 h-4 text-cyan-500" />
            <span className="text-lg font-medium text-cyan-500">
              {(selectedLLMs.reduce((total, model) => total + (prices[model] || 0), 0)).toFixed(4)}
            </span>
          </div>

          {/* Step completion indicator */}
          <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            Step {Object.keys(stepInfo).indexOf(currentStep) + 1} of {Object.keys(stepInfo).length}
          </div>
        </div>
      </div>
    );
  };

  // Render the main component
  return (
    <div className="container mx-auto p-4 md:p-8 max-w-6xl" ref={containerRef}>
      {/* Step Progress Bar */}
      <div className="mb-8">
        <Progress
          value={progress}
          animated={true}
          labels={Object.values(stepInfo).map(step => step.title)}
          showLabels={true}
          activeStep={Object.keys(stepInfo).indexOf(currentStep)}
        />
      </div>

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

      {/* Main Content Area - Different for each step */}
      <div className="bg-white dark:bg-gray-900 rounded-xl shadow-md p-6 mb-8 transition-all duration-500">
        {/* Step 1: Introduction */}
        {currentStep === 'INTRO' && (
          <div className="space-y-6">
            <div className="flex justify-center mb-8">
              <AnimatedLogoV3 size="large" />
            </div>

            <div className="text-center max-w-2xl mx-auto">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                Welcome to Ultra AI
              </h1>
              <p className="text-gray-700 dark:text-gray-300 mb-6">
                Ultra multiplies intelligence by analyzing your prompt with multiple AI models simultaneously,
                then synthesizing the insights into a comprehensive response.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <div className="bg-blue-50 dark:bg-blue-900/30 p-4 rounded-lg">
                  <Brain className="w-8 h-8 text-blue-500 mb-2 mx-auto" />
                  <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-1">Multiple Models</h3>
                </div>

                <div className="bg-purple-50 dark:bg-purple-900/30 p-4 rounded-lg">
                  <Lightbulb className="w-8 h-8 text-purple-500 mb-2 mx-auto" />
                  <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-1">Enhanced Analysis</h3>
                </div>

                <div className="bg-green-50 dark:bg-green-900/30 p-4 rounded-lg">
                  <FileText className="w-8 h-8 text-green-500 mb-2 mx-auto" />
                  <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-1">Document Context</h3>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Prompt Input */}
        {currentStep === 'PROMPT' && (
          <div className="space-y-6">
            <div className="mb-6">
              <Label htmlFor="prompt" className="text-lg font-medium mb-2 block">
                What would you like Ultra to analyze?
              </Label>
              <div className="relative">
                <Textarea
                  id="prompt"
                  placeholder="Enter your question or request here..."
                  className="w-full min-h-32 p-3 text-md"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  disabled={isProcessing || isOffline}
                />
                {prompt.length > 0 && (
                  <div className="absolute bottom-2 right-2 text-xs text-gray-500">
                    {prompt.length} characters
                  </div>
                )}
              </div>

              <div className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                <p>Tips for great prompts:</p>
                <ul className="list-disc pl-5 mt-1 space-y-1">
                  <li>Be specific about what you're looking for</li>
                  <li>Provide context when relevant</li>
                  <li>Ask for analysis, comparisons, or evaluations</li>
                </ul>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-300 p-3 rounded-md mb-4">
                {error}
              </div>
            )}
          </div>
        )}

        {/* Step 3: Documents Upload */}
        {currentStep === 'DOCUMENTS' && (
          <div className="space-y-6">
            <div className="mb-4">
              <div className="flex items-center space-x-2 mb-2">
                <Checkbox
                  id="useDocuments"
                  checked={isUsingDocuments}
                  onCheckedChange={(checked) => setIsUsingDocuments(checked as boolean)}
                  disabled={isProcessing || isOffline}
                />
                <Label htmlFor="useDocuments" className="text-lg font-medium">
                  Include documents in your analysis
                </Label>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Upload files that provide context or information relevant to your query.
              </p>
            </div>

            {isUsingDocuments && (
              <div className="space-y-4">
                <div
                  className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-8 text-center cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload className="h-10 w-10 text-gray-400 dark:text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-600 dark:text-gray-400">
                    Drag and drop files here, or click to select
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                    Supports PDF, TXT, DOCX, and more (max 4MB per file)
                  </p>
                  <input
                    type="file"
                    ref={fileInputRef}
                    className="hidden"
                    multiple
                    onChange={handleFileSelect}
                    disabled={isProcessing || isOffline}
                  />
                </div>

                {/* Document List */}
                {documents.length > 0 && (
                  <div className="mt-4">
                    <h3 className="font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Selected Documents ({documents.length})
                    </h3>
                    <div className="space-y-2">
                      {documents.map((doc, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 p-3 rounded-md"
                        >
                          <div className="flex items-center space-x-3">
                            <File className="h-5 w-5 text-blue-500" />
                            <div>
                              <p className="text-sm font-medium text-gray-800 dark:text-gray-200">{doc.name}</p>
                            </div>
                          </div>

                          <div className="flex items-center">
                            {uploadProgress[doc.name] !== undefined && uploadProgress[doc.name] < 100 ? (
                              <div className="w-16">
                                <Progress value={uploadProgress[doc.name]} size="sm" />
                              </div>
                            ) : uploadProgress[doc.name] === 100 ? (
                              <Check className="h-5 w-5 text-green-500" />
                            ) : (
                              <button
                                onClick={() => removeDocument(index)}
                                className="text-gray-500 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400"
                              >
                                <X className="h-5 w-5" />
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Uploaded Documents */}
                {uploadedDocuments.length > 0 && (
                  <div className="mt-4">
                    <h3 className="font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Uploaded Documents ({uploadedDocuments.length})
                    </h3>
                    <div className="space-y-2">
                      {uploadedDocuments.map((doc) => (
                        <div
                          key={doc.id}
                          className="flex items-center justify-between bg-green-50 dark:bg-green-900/20 p-3 rounded-md"
                        >
                          <div className="flex items-center space-x-3">
                            <File className="h-5 w-5 text-green-500" />
                            <p className="text-sm font-medium text-gray-800 dark:text-gray-200">{doc.name}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {documents.length > 0 && (
                  <div className="flex justify-center mt-4">
                    <Button
                      onClick={uploadDocuments}
                      disabled={isProcessing || documents.length === 0 || isOffline}
                      className="bg-blue-600 hover:bg-blue-700 text-white"
                    >
                      Upload Selected Documents
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Step 4: Model Selection */}
        {currentStep === 'MODELS' && (
          <div className={`space-y-4 ${animating ? 'fadeOut' : 'fadeIn'}`}>
            <div className="border-2 border-cyan-700 rounded-lg p-6 bg-black/50 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-900/20 to-purple-900/20"></div>
              <div className="relative z-10">
                <div className="flex items-center mb-4">
                  <div className="w-8 h-8 rounded-full bg-cyan-700 flex items-center justify-center mr-3 text-white font-bold">2</div>
                  <h2 className="text-2xl font-bold text-cyan-400">Select AI models</h2>
                </div>
                <p className="text-cyan-100 mb-4">
                  Choose which AI models will analyze your query. Each model brings unique strengths and perspectives.
                </p>

                <div className="space-y-2">
                  <Label className="text-lg text-cyan-200">Available AI Models</Label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2">
                    {availableModels.map((model) => {
                      const isSelected = selectedLLMs.includes(model);
                      const isUltra = ultraLLM === model;

                      return (
                        <div
                          key={model}
                          className={`
                            border rounded-lg p-4 cursor-pointer transition-all
                            ${isSelected
                              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                              : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'}
                            ${isUltra ? 'ring-2 ring-purple-500' : ''}
                          `}
                          onClick={() => handleLLMChange(model)}
                        >
                          <div className="flex justify-between items-center">
                            <div className="flex items-center gap-2">
                              <Checkbox
                                checked={isSelected}
                                onCheckedChange={() => handleLLMChange(model)}
                                disabled={isProcessing || isOffline}
                                className="data-[state=checked]:bg-blue-600"
                              />
                              <span className="font-medium text-gray-800 dark:text-gray-200">
                                {model.charAt(0).toUpperCase() + model.slice(1)}
                              </span>
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              ${prices[model]?.toFixed(4)} / 1K tokens
                            </div>
                          </div>

                          <div className="mt-4 flex justify-between items-center">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleUltraChange(model);
                              }}
                              disabled={!isSelected || isProcessing || isOffline}
                              className={`
                                text-xs font-medium px-3 py-1 rounded-full
                                ${isUltra
                                  ? 'bg-purple-600 text-white'
                                  : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-purple-200'}
                                ${!isSelected ? 'opacity-50 cursor-not-allowed' : ''}
                              `}
                            >
                              {isUltra ? 'Ultra Model ✓' : 'Set as Ultra Model'}
                            </button>
                          </div>
                        </div>
                      );
                    })}
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
        )}

        {/* Step 5: Analysis Type Selection */}
        {currentStep === 'ANALYSIS_TYPE' && (
          <div className="space-y-6">
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-800 dark:text-white mb-2">
                Select Analysis Method
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Choose how Ultra should approach your query.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {analysisTypes.map((type) => {
                  const isSelected = selectedAnalysisType === type.id;
                  const Icon = type.icon;

                  return (
                    <div
                      key={type.id}
                      className={`
                        border rounded-lg p-4 cursor-pointer transition-all
                        ${isSelected
                          ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'}
                      `}
                      onClick={() => handleAnalysisTypeChange(type.id)}
                    >
                      <div className="flex flex-col items-center text-center">
                        <div className={`p-3 rounded-full mb-3 ${isSelected ? 'bg-purple-100 dark:bg-purple-900/30' : 'bg-gray-100 dark:bg-gray-800'}`}>
                          <Icon className={`h-6 w-6 ${isSelected ? 'text-purple-600' : 'text-gray-500 dark:text-gray-400'}`} />
                        </div>
                        <h4 className="font-medium text-gray-800 dark:text-gray-200 mb-1">
                          {type.name}
                        </h4>
                        <p className="text-xs text-gray-600 dark:text-gray-400">
                          {type.description}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Step 6: Processing */}
        {currentStep === 'PROCESSING' && (
          <div className="space-y-6 text-center">
            <div className="flex justify-center mb-8">
              <div className="relative">
                <AnimatedLogoV3 size="large" />
              </div>
            </div>

            <h3 className="text-xl font-medium text-gray-800 dark:text-white mb-2">
              {isComplete ? 'Analysis Complete!' : 'Processing Your Analysis'}
            </h3>

            <div className="max-w-md mx-auto mb-6">
              <Progress value={isComplete ? 100 : progress} animated={!isComplete} />
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                {progressMessage}
              </p>
            </div>

            {isComplete && (
              <div className="text-center">
                <p className="text-green-600 dark:text-green-400 font-medium mb-4">
                  {isCached ? 'Results retrieved from cache' : 'Analysis completed successfully'}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Step 7: Results */}
        {currentStep === 'RESULTS' && (
          <div className="space-y-6" ref={outputRef}>
            <div className="mb-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-medium text-gray-800 dark:text-white">
                  Ultra Analysis Results
                </h3>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => saveToHistory()}
                    disabled={isOffline}
                    className="text-sm text-blue-600 dark:text-blue-400 flex items-center gap-1 hover:underline"
                  >
                    <Save className="h-4 w-4" />
                    Save
                  </button>
                  <button
                    onClick={() => shareAnalysis()}
                    disabled={isOffline}
                    className="text-sm text-purple-600 dark:text-purple-400 flex items-center gap-1 hover:underline"
                  >
                    <Share2 className="h-4 w-4" />
                    Share
                  </button>
                </div>
              </div>

              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-4">
                <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-2">Your Prompt</h4>
                <p className="text-gray-800 dark:text-gray-200">{prompt}</p>
              </div>

              <div className="prose prose-lg dark:prose-invert max-w-none">
                {output && (
                  <div className="whitespace-pre-wrap rounded-lg border border-gray-200 dark:border-gray-700 p-4">
                    {output}
                  </div>
                )}
              </div>
            </div>

            <div className="flex flex-col md:flex-row gap-4 mt-8">
              <Button
                onClick={() => {
                  setCurrentStep('PROMPT');
                  setPrompt('');
                  setSelectedLLMs([]);
                  setUltraLLM(null);
                  setDocuments([]);
                  setUploadedDocuments([]);
                  setOutput('');
                  setIsComplete(false);
                  setProgress(0);
                  setIsUsingDocuments(false);
                }}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Start New Analysis
              </Button>

              <Button
                onClick={() => setShowHistory(true)}
                variant="outline"
                className="border-gray-300 dark:border-gray-700"
              >
                <History className="h-4 w-4 mr-2" />
                View History
              </Button>
            </div>
          </div>
        )}
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

      {/* History Dialog */}
      {renderHistoryPanel()}

      {/* Share Dialog */}
      {renderShareDialog()}

      {/* Offline Mode Banner */}
      {isOffline && (
        <div className="fixed bottom-4 right-4 bg-amber-50 dark:bg-amber-900/30 text-amber-800 dark:text-amber-300 p-4 rounded-lg shadow-lg flex items-center gap-3 max-w-md z-50">
          <div className="bg-amber-200 dark:bg-amber-800 p-2 rounded-full">
            <WifiOff className="h-5 w-5 text-amber-700 dark:text-amber-300" />
          </div>
          <div>
            <h3 className="font-medium mb-1">Offline Mode</h3>
            <p className="text-sm">You're currently offline. You can view saved analyses, but cannot make new requests.</p>
          </div>
        </div>
      )}
    </div>
  );
}