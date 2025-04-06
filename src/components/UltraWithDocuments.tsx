'use client'

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import { Button } from "./ui/button"
import { Checkbox } from "./ui/checkbox"
import { Label } from "./ui/label"
import { Textarea } from "../components/ui/textarea"
import { 
  Loader2, 
  Zap, 
  Lock, 
  Cpu, 
  FileText,
  AlertCircle,
  Brain,
  Feather,
  Award,
  Shield,
  Quote,
  Eye,
  Clock,
  Users,
  Network,
  Lightbulb,
} from 'lucide-react'
import axios from 'axios'

import { DocumentUpload } from './DocumentUpload'
import { DocumentViewer } from './DocumentViewer'
import { PricingDisplay } from './PricingDisplay'
import AnimatedLogoV3 from './AnimatedLogoV3'
import ErrorDisplay from './ErrorDisplay'
import { addApiErrorListener, removeApiErrorListener } from '../api/config.js'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8081'

const llmOptions = [
  { 
    id: 'gpt4o', 
    label: 'GPT-4o', 
    price: 0.0125, 
    icon: Zap, 
    contextWindow: '128k',
    inputCost: 0.0025,
    outputCost: 0.01,
    isThinkingModel: true,
    details: 'Advanced reasoning capabilities with large context window'
  },
  { 
    id: 'gpto1', 
    label: 'GPT-o1', 
    price: 0.075, 
    icon: Zap, 
    contextWindow: '200k',
    inputCost: 0.015,
    outputCost: 0.060,
    isThinkingModel: true,
    details: 'OpenAI\'s most powerful model with exceptional reasoning'
  },
  { 
    id: 'gpto3mini', 
    label: 'GPT-o3 mini', 
    price: 0.00550, 
    icon: Zap, 
    contextWindow: '200k',
    inputCost: 0.00110,
    outputCost: 0.00440,
    isThinkingModel: false,
    details: 'Efficient model with large context window and good performance'
  },
  { 
    id: 'claude37', 
    label: 'Claude 3.7 Sonnet', 
    price: 0.018, 
    icon: Lock, 
    contextWindow: '200k',
    inputCost: 0.003,
    outputCost: 0.015,
    isThinkingModel: true,
    details: 'Excellent for synthesis and integrating complex information'
  },
  { 
    id: 'claude3opus', 
    label: 'Claude 3 Opus', 
    price: 0.09, 
    icon: Award, 
    contextWindow: '200k',
    inputCost: 0.015,
    outputCost: 0.075,
    isThinkingModel: true,
    details: 'Highest quality reasoning and analysis'
  },
  { 
    id: 'gemini15', 
    label: 'Gemini 1.5', 
    price: 0.000375, 
    icon: Cpu, 
    contextWindow: '128k',
    inputCost: 0.000075,
    outputCost: 0.0003,
    isThinkingModel: false,
    details: 'Cost-efficient model with good overall capabilities'
  },
  { 
    id: 'gpt4turbo', 
    label: 'GPT-4 Turbo', 
    price: 0.04, 
    icon: Zap, 
    contextWindow: '128k',
    inputCost: 0.01,
    outputCost: 0.03,
    isThinkingModel: true,
    details: 'Excellent reasoning with optimized performance'
  },
  { 
    id: 'llama3', 
    label: 'Llama 3', 
    price: 0, 
    icon: Brain,
    contextWindow: 'Varies',
    inputCost: 0,
    outputCost: 0,
    isThinkingModel: false,
    details: 'Open source model that runs locally for complete privacy'
  }
]

const analysisPatterns = [
  { id: 'confidence', label: 'Confidence Analysis', description: 'Evaluates the strength of each model response and selects the most reliable one', icon: <Brain className="w-4 h-4" /> },
  { id: 'critique', label: 'Critique', description: 'Asks models to critically evaluate each other\'s reasoning and answers', icon: <Feather className="w-4 h-4" /> },
  { id: 'gut', label: 'Gut Check', description: 'Rapid evaluation of different perspectives to identify the most likely correct answer', icon: <Zap className="w-4 h-4" /> },
  { id: 'scenario', label: 'Scenario Analysis', description: 'Explores potential future outcomes and alternative possibilities', icon: <Lock className="w-4 h-4" /> },
  { id: 'stakeholder', label: 'Stakeholder Vision', description: 'Analyzes from multiple stakeholder perspectives to reveal diverse interests and needs', icon: <Users className="w-4 h-4" /> },
  { id: 'systems', label: 'Systems Mapper', description: 'Maps complex system dynamics with feedback loops and leverage points', icon: <Network className="w-4 h-4" /> },
  { id: 'time', label: 'Time Horizon', description: 'Analyzes across multiple time frames to balance short and long-term considerations', icon: <Clock className="w-4 h-4" /> },
  { id: 'innovation', label: 'Innovation Bridge', description: 'Uses cross-domain analogies to discover non-obvious patterns and solutions', icon: <Lightbulb className="w-4 h-4" /> }
]

// Additional options
const addonOptions = [
  { id: 'private', label: 'Keep data private', description: 'Process everything locally without sending to external servers', icon: Shield },
  { id: 'anti_ai_detect', label: 'Guard against AI detection', description: 'Make output less identifiable as AI-generated', icon: Eye },
  { id: 'citation', label: 'Include citations/sources', description: 'Add references and sources to support claims', icon: Quote },
  { id: 'express', label: 'Express mode', description: 'Prioritize speed over comprehensiveness', icon: Clock },
]

// Output format options
const outputFormats = [
  { id: 'text', label: 'Text only', description: 'Plain text output', icon: FileText },
  { id: 'standard', label: 'Standard formatting', description: 'Basic formatting with headers and lists', icon: FileText },
  { id: 'google', label: 'Google Docs/Sheets', description: 'Formatted for Google Workspace', icon: FileText },
  { id: 'microsoft', label: 'Microsoft Word/Office', description: 'Formatted for Microsoft Office', icon: FileText },
]

const steps = [
  'Initializing Ultra framework',
  'Processing documents',
  'Analyzing prompt',
  'Generating initial responses',
  'Creating meta synthesis',
  'Performing ultra analysis',
  'Generating hyper response',
  'Packaging results'
]

interface ErrorWithResponse extends Error {
  response?: {
    data?: {
      detail?: string;
    };
  };
}

// Define interface for LLM model
interface LLMModel {
  id: string;
  label: string;
  price: number;
  icon: any; // Icon component type
  contextWindow: string;
  inputCost: number;
  outputCost: number;
  isThinkingModel: boolean;
  details: string;
}

const CyberpunkProgressBar = ({ step, totalSteps, currentMessage }: { step: number; totalSteps: number; currentMessage: string }) => {
  const progress = Math.round((step / totalSteps) * 100);
  const [displayProgress, setDisplayProgress] = React.useState(0);
  
  // Animate the progress value
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setDisplayProgress(progress);
    }, 100);
    
    return () => clearTimeout(timer);
  }, [progress]);
  
  return (
    <div className="my-6 p-4 border-2 border-cyan-500 bg-gray-900 rounded-md shadow-[0_0_15px_rgba(0,255,255,0.5)]">
      <div className="flex justify-between items-center mb-2">
        <div className="flex items-center">
          <span className="text-cyan-400 font-mono mr-2">[SYS]</span>
          <span className="text-cyan-300 font-mono animate-pulse">
            {currentMessage}
          </span>
        </div>
        <span className="text-cyan-400 font-mono">{displayProgress}%</span>
      </div>
      
      <div className="w-full bg-gray-800 h-2 rounded-full overflow-hidden">
        <div 
          className="h-full bg-gradient-to-r from-cyan-500 to-fuchsia-500 rounded-full transition-all duration-500 ease-out"
          style={{ width: `${displayProgress}%`, boxShadow: '0 0 10px rgba(0, 255, 255, 0.7)' }}
        />
      </div>
      
      <div className="grid grid-cols-8 gap-1 mt-2">
        {Array.from({ length: 8 }).map((_, i) => (
          <div 
            key={i} 
            className={`h-1 ${
              i < Math.ceil(displayProgress / 12.5) 
                ? 'bg-gradient-to-r from-cyan-400 to-fuchsia-600 animate-pulse' 
                : 'bg-gray-800'
            }`}
          />
        ))}
      </div>
      
      <div className="flex justify-between text-xs text-gray-500 mt-1 font-mono">
        <span>INIT</span>
        <span>PROCESS</span>
        <span>ANALYZE</span>
        <span>COMPLETE</span>
      </div>
    </div>
  );
};

// Add this function to display detailed model information
const ModelInfoTooltip = ({ model }: { model: LLMModel }) => {
  return (
    <div className="text-xs space-y-1 max-w-[300px]">
      <div className="flex items-center justify-between">
        <span className="text-gray-400">Input:</span>
        <span className="text-cyan-300">${model.inputCost.toFixed(5)}/1K tokens</span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-gray-400">Output:</span>
        <span className="text-cyan-300">${model.outputCost.toFixed(5)}/1K tokens</span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-gray-400">Context:</span>
        <span className="text-cyan-300">{model.contextWindow}</span>
      </div>
      <div className="mt-2 text-gray-300">{model.details}</div>
      {model.isThinkingModel && (
        <div className="mt-1 text-purple-300 font-semibold">
          Recommended thinking model
        </div>
      )}
    </div>
  );
};

// Add status key display component 
const StatusKey = () => (
  <div className="bg-gray-900/70 p-3 rounded-md border border-gray-800 text-xs">
    <div className="text-cyan-400 font-medium mb-2">Model Key</div>
    <div className="flex items-center mb-1">
      <div className="w-3 h-3 rounded-full bg-purple-500 mr-2"></div>
      <span className="text-gray-300">Thinking Model</span>
    </div>
    <div className="flex items-center">
      <div className="w-3 h-3 rounded-full bg-cyan-500 mr-2"></div>
      <span className="text-gray-300">Prime Synthesizer</span>
    </div>
  </div>
)

// Simple Radio component
const Radio = ({ checked, className = "" }: { checked: boolean, className?: string }) => (
  <div className={`w-5 h-5 rounded-full border ${checked ? 'bg-cyan-500 border-cyan-500' : 'border-gray-500'} ${className}`}>
    {checked && <div className="w-2 h-2 rounded-full bg-white m-auto mt-1.5" />}
  </div>
);

// Define error type
interface AppError {
  id: string;
  message: string;
  timestamp: Date;
  type: 'api' | 'general' | 'network';
}

export default function UltraWithDocuments() {
  // State for prompt and LLM selection
  const [prompt, setPrompt] = useState('')
  const [selectedLLMs, setSelectedLLMs] = useState<string[]>([])
  const [ultraLLM, setUltraLLM] = useState<string | null>(null)
  const [pattern, setPattern] = useState('confidence')
  
  // State for files
  const [files, setFiles] = useState<File[]>([])
  const [processedDocuments, setProcessedDocuments] = useState([])
  const [isProcessingDocs, setIsProcessingDocs] = useState(false)
  const [docError, setDocError] = useState<string | null>(null)
  
  // State for analysis
  const [isProcessing, setIsProcessing] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [isComplete, setIsComplete] = useState(false)
  const [output, setOutput] = useState('')
  const [error, setError] = useState<string | null>(null)
  
  // Add state for new options
  const [selectedAddons, setSelectedAddons] = useState<string[]>(['private'])
  const [perspective, setPerspective] = useState('')
  const [includePerspective, setIncludePerspective] = useState(false)
  const [includeFactCheck, setIncludeFactCheck] = useState(false)
  
  // Add state for output format
  const [outputFormat, setOutputFormat] = useState('text')

  // Add state for tracking errors
  const [errors, setErrors] = useState<AppError[]>([])

  // Add state for tracking which models are available
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [modelErrors, setModelErrors] = useState<{[key: string]: string}>({});
  const [isCheckingModels, setIsCheckingModels] = useState(false);

  // Setup API error listener
  useEffect(() => {
    // Handler for API errors
    const handleApiError = (errorDetail: any) => {
      const newError: AppError = {
        id: errorDetail.id || Date.now().toString(),
        message: errorDetail.message || 'Unknown API error',
        timestamp: errorDetail.timestamp || new Date(),
        type: 'api'
      };
      
      setErrors(prev => [...prev, newError]);
    };
    
    // Add listener
    addApiErrorListener(handleApiError);
    
    // Cleanup on unmount
    return () => {
      removeApiErrorListener(handleApiError);
    };
  }, []);

  // Function to add error to the errors array
  const addError = (message: string, type: 'api' | 'general' | 'network' = 'general') => {
    const newError: AppError = {
      id: Date.now().toString(),
      message,
      timestamp: new Date(),
      type
    };
    
    setErrors(prev => [...prev, newError]);
    
    // Also log to console
    console.error(`[${type.toUpperCase()}] ${message}`);
  };

  // Function to dismiss an error
  const dismissError = (id: string) => {
    setErrors(prev => prev.filter(error => error.id !== id));
  };

  // Handle file selection
  const handleFilesSelected = async (selectedFiles: File[]) => {
    setFiles(selectedFiles);
    
    if (selectedFiles.length > 0) {
      await processFiles(selectedFiles);
    } else {
      setProcessedDocuments([]);
    }
  };
  
  // Process files with the backend
  const processFiles = async (selectedFiles: File[]) => {
    setIsProcessingDocs(true);
    setDocError(null);
    
    try {
      const formData = new FormData();
      
      selectedFiles.forEach(file => {
        formData.append('files', file);
      });
      
      const response = await axios.post(`${API_URL}/api/upload-files`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      if (response.data.status === 'success') {
        setProcessedDocuments(response.data.documents);
      } else {
        const errorMsg = 'Failed to process documents';
        setDocError(errorMsg);
        addError(errorMsg, 'api');
      }
    } catch (err) {
      console.error('Error processing files:', err);
      const errorWithResponse = err as ErrorWithResponse;
      const errorMsg = errorWithResponse.response?.data?.detail || 'An error occurred while processing files';
      setDocError(errorMsg);
      addError(errorMsg, 'api');
    } finally {
      setIsProcessingDocs(false);
    }
  };

  // Update handleLLMChange to use our toggleModelSelection function
  const handleLLMChange = (id: string) => {
    toggleModelSelection(id);
    
    // Reset the ultra model if it's no longer selected as an LLM
    if (ultraLLM === id && !selectedLLMs.includes(id)) {
      setUltraLLM(null);
    }
  };
  
  // Handle Ultra LLM selection
  const handleUltraChange = (llmId: string) => {
    setUltraLLM(prev => prev === llmId ? null : llmId)
  }
  
  // Handle addon selection
  const handleAddonChange = (addonId: string) => {
    setSelectedAddons(prev => 
      prev.includes(addonId) ? prev.filter(id => id !== addonId) : [...prev, addonId]
    )
  }
  
  // Calculate total add-on price
  const calculateAddonPrice = () => {
    let price = 0;
    
    // Fixed addon prices
    const addonPrices: Record<string, number> = {
      'private': 0.05,
      'anti_ai_detect': 0.05,
      'citation': 0.05,
      'express': 0.03
    };
    
    // Add price for each selected addon
    selectedAddons.forEach(addon => {
      price += addonPrices[addon] || 0;
    });
    
    // Add price for other options
    if (includeFactCheck) price += 0.15;
    if (includePerspective) price += 0.10;
    
    // Format output options prices
    const outputFormatPrices: Record<string, number> = {
      'text': 0.00,
      'standard': 0.00,
      'google': 0.10,
      'microsoft': 0.15
    };
    
    price += outputFormatPrices[outputFormat] || 0;
    
    return price;
  };
  
  // Handle analyze button click
  const handleAnalyze = async () => {
    try {
      // Validate inputs
      if (!prompt.trim()) {
        setError('Please enter a prompt');
        addError('Please enter a prompt', 'general');
        return;
      }
      
      if (selectedLLMs.length < 2) {
        setError('Please select at least two LLMs');
        addError('Please select at least two LLMs', 'general');
        return;
      }
      
      if (!ultraLLM) {
        setError('Please select an Ultra LLM');
        addError('Please select an Ultra LLM', 'general');
        return;
      }
      
      setIsProcessing(true);
      setCurrentStep(1);
      setIsComplete(false);
      setError(null);
      setOutput('');
      
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
        addError(`Selected Ultra model (${ultraLLM}) is not available. Using ${safeUltraModel} instead.`, 'general');
      }
      
      // Increment the current step as we prepare to process
      setCurrentStep(2);
      
      // Create a payload for the analyze request
      const payload = {
        prompt,
        selectedModels: availableSelectedModels,
        ultraModel: safeUltraModel,
        pattern,
        options: {
          keepDataPrivate: selectedAddons.includes('private'),
          useNoTraceEncryption: selectedAddons.includes('anti_ai_detect'),
          includeCitations: selectedAddons.includes('citation'),
          expressMode: selectedAddons.includes('express'),
          includePerspective,
          includeFactCheck
        }
      };
      
      // Process files if there are any
      let response;
      if (files.length > 0) {
        setCurrentStep(3);
        
        // Create form data for file upload
        const formData = new FormData();
        formData.append('prompt', prompt);
        formData.append('selectedModels', JSON.stringify(availableSelectedModels));
        formData.append('ultraModel', safeUltraModel || '');
        formData.append('pattern', pattern);
        formData.append('options', JSON.stringify(payload.options));
        
        // Add files to form data
        files.forEach(file => {
          formData.append('files', file);
        });
        
        // Send analyze with documents request
        response = await axios.post(`${API_URL}/api/analyze-with-docs`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
      } else {
        // Increment steps to match UI flow even with no files
        setCurrentStep(3);
        setCurrentStep(4);
        
        // Process without files
        response = await axios.post(`${API_URL}/api/analyze`, payload);
      }
      
      // Update UI progress
      setCurrentStep(5);
      setCurrentStep(6);
      setCurrentStep(7);
      
      // Handle the response
      if (response.data) {
        // Check if there was a partial success
        if (response.data.status === 'partial_success' && response.data.error_info) {
          // Show warning about unavailable models
          const unavailableModels = response.data.error_info.unavailable_models || [];
          if (unavailableModels.length > 0) {
            addError(`Some models were unavailable: ${unavailableModels.join(', ')}`, 'api');
          }
          
          // Update the available models list from the response
          if (response.data.available_models) {
            setAvailableModels(response.data.available_models);
          }
        }
        
        // Process the results
        const data = response.data.data;
        setOutput(data.ultra);
        setIsComplete(true);
        setCurrentStep(8);
      } else {
        setError("No data returned from the API");
      }
    } catch (error: any) {
      setError(`An error occurred: ${error.response?.data?.detail || error.message}`);
      addError(error.response?.data?.detail || error.message, 'api');
    } finally {
      setIsProcessing(false);
    }
  };
  
  // Use handleAnalyze for form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await handleAnalyze();
  };
  
  // Add keyframes style to head
  useEffect(() => {
    // Create style element
    const styleEl = document.createElement('style');
    styleEl.innerHTML = `
      @keyframes borderPulse {
        0%, 100% { 
          border-color: rgba(8, 145, 178, 0.4); 
          box-shadow: 0 0 5px rgba(8, 145, 178, 0.3);
        }
        50% { 
          border-color: rgba(14, 165, 233, 1); 
          box-shadow: 0 0 25px rgba(14, 165, 233, 0.8);
        }
      }
      
      .neon-border {
        position: relative;
      }
      
      .neon-border::before {
        content: "";
        position: absolute;
        inset: -3px;
        z-index: -1;
        background: linear-gradient(90deg, #06b6d4, #0ea5e9, #06b6d4);
        border-radius: inherit;
        animation: borderGlow 3s linear infinite;
        filter: blur(8px);
        opacity: 0.7;
      }
      
      @keyframes borderGlow {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 0.8; }
      }
      
      @keyframes flicker {
        0%, 100% { opacity: 1; }
        8% { opacity: 0.8; }
        10% { opacity: 0.9; }
        20% { opacity: 1; }
        40% { opacity: 0.7; }
        42% { opacity: 1; }
        60% { opacity: 0.9; }
        80% { opacity: 1; }
      }
      
      .animate-flicker {
        animation: flicker 4s infinite;
      }
      
      @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
      }
      
      .animate-gradient {
        animation: gradient 3s ease infinite;
      }
      
      .thinking-model-border {
        position: relative;
        overflow: hidden;
      }
      
      .thinking-model-border::before {
        content: "";
        position: absolute;
        inset: -4px;
        background: linear-gradient(90deg, #c084fc, #a855f7, #8b5cf6);
        border-radius: inherit;
        animation: thinkingBorderGlow 3s ease-in-out infinite;
        filter: blur(6px);
        opacity: 0.7;
        z-index: -1;
      }
      
      @keyframes thinkingBorderGlow {
        0%, 100% { opacity: 0.4; transform: scale(0.98); }
        50% { opacity: 0.8; transform: scale(1.01); }
      }
      
      .border-pulse {
        position: relative;
      }
      
      .border-pulse::before {
        content: "";
        position: absolute;
        inset: -3px;
        z-index: -1;
        background: linear-gradient(90deg, #06b6d4, #0ea5e9, #06b6d4);
        border-radius: inherit;
        animation: borderGlow 3s linear infinite;
        filter: blur(8px);
        opacity: 0.7;
      }
      
      @keyframes borderGlow {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 0.8; }
      }
      
      @keyframes flicker {
        0%, 100% { opacity: 1; }
        8% { opacity: 0.8; }
        10% { opacity: 0.9; }
        20% { opacity: 1; }
        40% { opacity: 0.7; }
        42% { opacity: 1; }
        60% { opacity: 0.9; }
        80% { opacity: 1; }
      }
      
      .animate-flicker {
        animation: flicker 4s infinite;
      }
      
      @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
      }
      
      .animate-gradient {
        animation: gradient 3s ease infinite;
      }
      
      @keyframes float {
        0%, 100% { transform: translateY(0) translateX(0); opacity: 0.3; }
        25% { transform: translateY(-5px) translateX(5px); opacity: 0.5; }
        50% { transform: translateY(-8px) translateX(-3px); opacity: 0.8; }
        75% { transform: translateY(-3px) translateX(-7px); opacity: 0.4; }
      }
      
      .animate-float {
        animation: float 10s ease-in-out infinite;
      }
      
      .thinking-model-border {
        position: relative;
        overflow: hidden;
      }
      
      .thinking-model-border::before {
        content: "";
        position: absolute;
        inset: -4px;
        background: linear-gradient(90deg, #c084fc, #a855f7, #8b5cf6);
        border-radius: inherit;
        animation: thinkingBorderGlow 3s ease-in-out infinite;
        filter: blur(6px);
        opacity: 0.7;
        z-index: -1;
      }
      
      @keyframes thinkingBorderGlow {
        0%, 100% { opacity: 0.4; transform: scale(0.98); }
        50% { opacity: 0.8; transform: scale(1.01); }
      }
    `;
    
    // Append to head
    document.head.appendChild(styleEl);
    
    // Cleanup
    return () => {
      document.head.removeChild(styleEl);
    };
  }, []);
  
  // Add the AUTO select handler function
  const handleAutoSelect = () => {
    // Clear any previous error
    setError(null);
    
    if (!prompt.trim()) {
      setError('Please enter a prompt first');
      addError('Please enter a prompt first', 'general');
      return;
    }
    
    // Select a good combination of models based on the query
    const recommendedModels = ['gpt4o', 'claude37', 'gemini15'];
    setSelectedLLMs(recommendedModels);
    
    // Select the best Ultra model 
    setUltraLLM('claude37');
    
    // Select the most appropriate analysis pattern based on query
    // For demo purposes, we're selecting Confidence Analysis
    setPattern('confidence');
    
    // Add curtain effect to show steps 3-5 are handled
    const stepsContainer = document.querySelector('.auto-steps-container');
    if (stepsContainer) {
      // Add the curtain overlay to steps 3-5
      stepsContainer.classList.add('steps-auto-selected');
    }
    
    // Show a temporary success message
    const successElement = document.createElement('div');
    successElement.className = 'fixed top-4 right-4 bg-green-600 text-white p-3 rounded-md shadow-lg z-50';
    successElement.innerHTML = 'AUTO selection complete! Ready to run analysis.';
    document.body.appendChild(successElement);
    
    // Remove after 3 seconds
    setTimeout(() => {
      if (document.body.contains(successElement)) {
        document.body.removeChild(successElement);
      }
    }, 3000);
  };
  
  // Add useEffect hook for curtain styles
  useEffect(() => {
    // Create style element for curtain effect
    const curtainStyleEl = document.createElement('style');
    curtainStyleEl.innerHTML = `
      .steps-auto-selected .auto-curtain {
        display: flex !important;
      }
      
      @keyframes curtainReveal {
        from { opacity: 0; }
        to { opacity: 1; }
      }
      
      .auto-curtain {
        animation: curtainReveal 0.5s ease-out forwards;
      }
    `;
    
    // Append to head
    document.head.appendChild(curtainStyleEl);
    
    // Cleanup
    return () => {
      if (document.head.contains(curtainStyleEl)) {
        document.head.removeChild(curtainStyleEl);
      }
    };
  }, []);
  
  // Add the RANDOM select handler function
  const handleRandomSelect = () => {
    // Clear any previous error
    setError(null);
    
    if (!prompt.trim()) {
      setError('Please enter a prompt first');
      addError('Please enter a prompt first', 'general');
      return;
    }
    
    // Randomly select 2-4 models
    const modelIds = llmOptions.map(model => model.id);
    const shuffledModels = [...modelIds].sort(() => Math.random() - 0.5);
    const randomModelCount = Math.floor(Math.random() * 3) + 2; // Random number between 2 and 4
    const randomModels = shuffledModels.slice(0, randomModelCount);
    setSelectedLLMs(randomModels);
    
    // Randomly select Ultra model
    const randomUltraIndex = Math.floor(Math.random() * llmOptions.length);
    setUltraLLM(llmOptions[randomUltraIndex].id);
    
    // Randomly select analysis pattern
    const patternIds = analysisPatterns.map(pattern => pattern.id);
    const randomPatternIndex = Math.floor(Math.random() * patternIds.length);
    setPattern(patternIds[randomPatternIndex]);
    
    // Add curtain effect
    const stepsContainer = document.querySelector('.auto-steps-container');
    if (stepsContainer) {
      stepsContainer.classList.add('steps-auto-selected');
    }
    
    // Show a temporary success message
    const successElement = document.createElement('div');
    successElement.className = 'fixed top-4 right-4 bg-purple-600 text-white p-3 rounded-md shadow-lg z-50';
    successElement.innerHTML = 'RANDOM selection complete! Caution has been thrown to the wind!';
    document.body.appendChild(successElement);
    
    // Remove after 3 seconds
    setTimeout(() => {
      if (document.body.contains(successElement)) {
        document.body.removeChild(successElement);
      }
    }, 3000);
  };
  
  // Function to reset AUTO selections
  const resetAutoSelections = () => {
    // Clear the selected models
    setSelectedLLMs([]);
    
    // Clear the Ultra model
    setUltraLLM(null);
    
    // Reset pattern to default
    setPattern('confidence');
    
    // Remove the curtain effect
    const stepsContainer = document.querySelector('.auto-steps-container');
    if (stepsContainer) {
      stepsContainer.classList.remove('steps-auto-selected');
    }
    
    // Show a temporary message
    const messageElement = document.createElement('div');
    messageElement.className = 'fixed top-4 right-4 bg-cyan-600 text-white p-3 rounded-md shadow-lg z-50';
    messageElement.innerHTML = 'Selections reset. You can now choose manually.';
    document.body.appendChild(messageElement);
    
    // Remove after 3 seconds
    setTimeout(() => {
      if (document.body.contains(messageElement)) {
        document.body.removeChild(messageElement);
      }
    }, 3000);
  };
  
  // Add this function somewhere inside the UltraWithDocuments component
  useEffect(() => {
    const testApiConnection = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/test`);
        console.log('API connection test:', response.data);
        // If it works, we know the connection is good
      } catch (error) {
        console.error('API connection test failed:', error);
        addError('Could not connect to the backend API. Please check if the backend server is running.', 'network');
      }
    };

    // Run the test on component mount
    testApiConnection();
  }, []);

  // Add a function to check available models
  const checkAvailableModels = useCallback(async () => {
    setIsCheckingModels(true);
    try {
      const response = await axios.get(`${API_URL}/api/available-models`);
      setAvailableModels(response.data.available_models || []);
      setModelErrors(response.data.errors || {});
      
      // Log any errors for debugging
      if (Object.keys(response.data.errors || {}).length > 0) {
        console.warn('Some models are unavailable:', response.data.errors);
      }
    } catch (error) {
      console.error('Failed to check available models:', error);
      // Assume all models are available if we can't check
      setAvailableModels(llmOptions.map(model => model.id));
    } finally {
      setIsCheckingModels(false);
    }
  }, []);

  // Check available models on component mount
  useEffect(() => {
    checkAvailableModels();
  }, [checkAvailableModels]);

  // Filter LLM options to only show available models
  const filteredLlmOptions = useMemo(() => {
    if (availableModels.length === 0) {
      // If we don't have availability data yet, show all models
      return llmOptions;
    }
    
    // Only show models that are available
    return llmOptions.filter(model => availableModels.includes(model.id));
  }, [availableModels]);

  // Add a function to check if a model is available
  const isModelAvailable = useCallback((modelId: string) => {
    return availableModels.includes(modelId);
  }, [availableModels]);

  // Modify the renderModelOptions function to use filteredLlmOptions
  const renderModelOptions = () => {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2 mt-2">
        {isCheckingModels ? (
          <div className="col-span-full flex items-center justify-center py-4">
            <Loader2 className="h-6 w-6 animate-spin text-cyan-500 mr-2" />
            <span>Checking available models...</span>
          </div>
        ) : (
          filteredLlmOptions.map((model) => (
            <div
              key={model.id}
              className={`border rounded-lg p-3 cursor-pointer transition-all ${
                selectedLLMs.includes(model.id)
                  ? 'border-cyan-500 bg-cyan-900/30 shadow-[0_0_10px_rgba(0,255,255,0.2)]'
                  : 'border-gray-700 bg-gray-800/40 hover:bg-gray-800/70'
              }`}
              onClick={() => toggleModelSelection(model.id)}
            >
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center">
                  <div className={`w-4 h-4 rounded-full mr-2 ${model.isThinkingModel ? 'bg-purple-500' : 'bg-cyan-500'}`}></div>
                  <h3 className="text-sm font-medium">{model.label}</h3>
                </div>
                <model.icon className="h-4 w-4 text-gray-400" />
              </div>
              <div className="text-xs text-gray-400 flex justify-between items-center">
                <span>${model.price.toFixed(4)}/1K tokens</span>
                <span className="text-xs text-cyan-300">{model.contextWindow}</span>
              </div>
            </div>
          ))
        )}
        {Object.keys(modelErrors).length > 0 && (
          <div className="col-span-full mt-2 text-xs text-amber-400 bg-amber-950/30 p-2 rounded border border-amber-700">
            Some models are unavailable due to API configuration issues.
          </div>
        )}
      </div>
    );
  };
  
  // Define the toggleModelSelection function
  const toggleModelSelection = (modelId: string) => {
    if (selectedLLMs.includes(modelId)) {
      setSelectedLLMs(selectedLLMs.filter(id => id !== modelId));
    } else {
      setSelectedLLMs([...selectedLLMs, modelId]);
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white">
      <div className="max-w-7xl mx-auto bg-black border-4 border-cyan-700 rounded-lg shadow-2xl shadow-cyan-500/20 p-4 md:p-8 relative overflow-hidden">
        {/* Cyberpunk city backdrop */}
        <div className="absolute inset-0 overflow-hidden opacity-5 pointer-events-none">
          {/* Distant city skyline */}
          <div className="absolute bottom-0 left-0 right-0 h-40 bg-gray-900">
            {/* Distant buildings */}
            <div className="absolute bottom-0 left-5 w-10 h-20 bg-gray-800"></div>
            <div className="absolute bottom-0 left-14 w-8 h-28 bg-gray-800"></div>
            <div className="absolute bottom-0 left-22 w-12 h-32 bg-gray-800"></div>
            <div className="absolute bottom-0 left-36 w-14 h-24 bg-gray-800"></div>
            <div className="absolute bottom-0 left-52 w-10 h-36 bg-gray-800"></div>
            <div className="absolute bottom-0 left-64 w-16 h-30 bg-gray-800"></div>
            
            {/* Distant building lights */}
            <div className="absolute bottom-10 left-8 w-1 h-1 bg-yellow-400 opacity-80 animate-pulse" style={{animationDelay: '1.2s'}}></div>
            <div className="absolute bottom-15 left-16 w-1 h-1 bg-cyan-400 opacity-80 animate-pulse" style={{animationDelay: '0.8s'}}></div>
            <div className="absolute bottom-20 left-24 w-1 h-1 bg-pink-400 opacity-80 animate-pulse" style={{animationDelay: '2.1s'}}></div>
            <div className="absolute bottom-18 left-40 w-1 h-1 bg-purple-400 opacity-80 animate-pulse" style={{animationDelay: '1.5s'}}></div>
            <div className="absolute bottom-25 left-54 w-1 h-1 bg-yellow-400 opacity-80 animate-pulse" style={{animationDelay: '0.4s'}}></div>
            
            {/* Center buildings */}
            <div className="absolute bottom-0 right-1/3 left-1/3 flex justify-center items-end">
              <div className="w-24 h-48 bg-gray-800 mx-1"></div>
              <div className="w-20 h-32 bg-gray-800 mx-1"></div>
              <div className="w-16 h-42 bg-gray-800 mx-1"></div>
            </div>
            
            {/* Right side buildings */}
            <div className="absolute bottom-0 right-5 w-10 h-26 bg-gray-800"></div>
            <div className="absolute bottom-0 right-14 w-8 h-22 bg-gray-800"></div>
            <div className="absolute bottom-0 right-22 w-12 h-30 bg-gray-800"></div>
            <div className="absolute bottom-0 right-36 w-14 h-28 bg-gray-800"></div>
            <div className="absolute bottom-0 right-52 w-10 h-24 bg-gray-800"></div>
          </div>
        </div>
        
        {/* Cyberpunk Billboard on a building rooftop */}
        <div className="absolute top-0 right-0 left-0 p-4 overflow-visible z-30">
          {/* Building structure and roof */}
          <div className="relative mx-auto max-w-3xl h-40">
            {/* Building structure */}
            <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-full max-w-md h-16 bg-gradient-to-b from-gray-900 to-gray-800 rounded-t-lg">
              {/* Building facade details */}
              <div className="absolute top-0 left-0 w-full h-2 bg-gray-700 rounded-t-lg"></div>
              <div className="absolute top-3 left-4 right-4 h-8 bg-gray-800 rounded-sm border border-gray-700"></div>
              
              {/* Building windows - small neon lights */}
              <div className="absolute top-1 left-4 w-3 h-2 bg-cyan-500 rounded-sm opacity-70 animate-pulse"></div>
              <div className="absolute top-3 left-10 w-2 h-2 bg-pink-500 rounded-sm opacity-70 animate-pulse" style={{animationDelay: '0.3s'}}></div>
              <div className="absolute top-5 left-16 w-2 h-2 bg-purple-500 rounded-sm opacity-70 animate-pulse" style={{animationDelay: '0.7s'}}></div>
              <div className="absolute top-2 left-24 w-3 h-2 bg-cyan-500 rounded-sm opacity-70 animate-pulse" style={{animationDelay: '1.1s'}}></div>
              <div className="absolute top-4 left-32 w-2 h-2 bg-pink-500 rounded-sm opacity-70 animate-pulse" style={{animationDelay: '0.5s'}}></div>
              
              <div className="absolute top-1 right-4 w-3 h-2 bg-cyan-500 rounded-sm opacity-70 animate-pulse" style={{animationDelay: '0.9s'}}></div>
              <div className="absolute top-3 right-10 w-2 h-2 bg-pink-500 rounded-sm opacity-70 animate-pulse" style={{animationDelay: '0.2s'}}></div>
              <div className="absolute top-5 right-16 w-2 h-2 bg-purple-500 rounded-sm opacity-70 animate-pulse" style={{animationDelay: '0.6s'}}></div>
              <div className="absolute top-2 right-24 w-3 h-2 bg-cyan-500 rounded-sm opacity-70 animate-pulse" style={{animationDelay: '1.3s'}}></div>
              <div className="absolute top-4 right-32 w-2 h-2 bg-pink-500 rounded-sm opacity-70 animate-pulse" style={{animationDelay: '0.4s'}}></div>
              
              {/* Neon tubing along building top */}
              <div className="absolute -top-1 left-2 right-2 h-1 bg-pink-500 rounded-full animate-flicker" style={{animationDuration: '4s', animationDelay: '0.7s'}}></div>
              <div className="absolute -top-1 left-1/4 w-1/2 h-1 bg-cyan-400 rounded-full animate-flicker" style={{animationDuration: '3s'}}></div>
            </div>
            
            {/* Billboard with proper 3D perspective - right side closer */}
            <div className="relative mx-auto max-w-2xl group hover:shadow-[0_0_15px_rgba(6,182,212,0.5)] transition-shadow duration-300"
                 style={{
                    transform: 'perspective(2000px) rotateY(-15deg) rotateX(5deg)',
                    transformOrigin: 'center',
                 }}>
              {/* Billboard frame */}
              <div className="absolute inset-0 rounded-lg border-4 border-gray-700 shadow-md"></div>
              <div className="absolute inset-1 bg-gray-800 rounded-md"></div>
              <div className="absolute inset-0 bg-gradient-to-r from-purple-900 via-cyan-800 to-pink-900 rounded-lg opacity-70 animate-pulse"></div>
              
              {/* Detailed scaffolding structure like in the reference image */}
              <div className="absolute -bottom-28 inset-x-0 flex justify-center">
                {/* Main support structure */}
                <div className="relative w-full">
                  {/* Central vertical beam */}
                  <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-4 h-28 bg-gray-600 border border-gray-700"></div>
                  
                  {/* Crossbeam metal supports */}
                  <div className="absolute -bottom-1 left-1/4 w-1 h-20 bg-gray-500 transform rotate-12"></div>
                  <div className="absolute -bottom-1 left-1/3 w-1 h-18 bg-gray-500 transform rotate-6"></div>
                  <div className="absolute -bottom-1 right-1/4 w-1 h-20 bg-gray-500 transform -rotate-12"></div>
                  <div className="absolute -bottom-1 right-1/3 w-1 h-18 bg-gray-500 transform -rotate-6"></div>
                  
                  {/* Horizontal support beams */}
                  <div className="absolute -bottom-8 inset-x-0 h-2 bg-gray-600"></div>
                  <div className="absolute -bottom-16 inset-x-0 h-2 bg-gray-600"></div>
                  <div className="absolute -bottom-24 inset-x-0 h-2 bg-gray-600"></div>
                  
                  {/* Metal lattice framework */}
                  <div className="absolute -bottom-25 left-6 w-[calc(100%-48px)] h-24 border border-gray-500 opacity-40"></div>
                  <div className="absolute -bottom-25 left-6 w-[calc(100%-48px)] h-24 border-l border-r border-gray-500 opacity-40"></div>
                  
                  {/* Cross braces */}
                  <div className="absolute -bottom-25 left-6 w-[calc(100%-48px)] h-24 border-t border-b border-gray-500 opacity-40"
                     style={{ clipPath: 'polygon(0 0, 100% 100%, 100% 0, 0 100%)' }}></div>
                  
                  {/* Support plates */}
                  <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-8 h-4 bg-gray-500"></div>
                  <div className="absolute -bottom-25 left-1/2 -translate-x-1/2 w-10 h-5 bg-gray-600"></div>
                  
                  {/* Rivets and bolts */}
                  <div className="absolute -bottom-2 left-1/2 -translate-x-4 w-1.5 h-1.5 rounded-full bg-gray-400 border border-gray-500"></div>
                  <div className="absolute -bottom-2 left-1/2 translate-x-3 w-1.5 h-1.5 rounded-full bg-gray-400 border border-gray-500"></div>
                  <div className="absolute -bottom-8 left-1/2 -translate-x-4 w-1.5 h-1.5 rounded-full bg-gray-400 border border-gray-500"></div>
                  <div className="absolute -bottom-8 left-1/2 translate-x-3 w-1.5 h-1.5 rounded-full bg-gray-400 border border-gray-500"></div>
                  <div className="absolute -bottom-16 left-1/2 -translate-x-4 w-1.5 h-1.5 rounded-full bg-gray-400 border border-gray-500"></div>
                  <div className="absolute -bottom-16 left-1/2 translate-x-3 w-1.5 h-1.5 rounded-full bg-gray-400 border border-gray-500"></div>
                  <div className="absolute -bottom-24 left-1/2 -translate-x-4 w-1.5 h-1.5 rounded-full bg-gray-400 border border-gray-500"></div>
                  <div className="absolute -bottom-24 left-1/2 translate-x-3 w-1.5 h-1.5 rounded-full bg-gray-400 border border-gray-500"></div>
                </div>
              </div>
              
              {/* Side metal support beams */}
              <div className="absolute -top-2 -left-3 -bottom-6 w-1 bg-gray-500"></div>
              <div className="absolute -top-2 -right-3 -bottom-6 w-1 bg-gray-500"></div>
              
              {/* Billboard content */}
              <div className="relative p-3 text-left">
                <div className="overflow-hidden">
                  <h2 
                    className="text-xl md:text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-400 via-cyan-300 to-purple-400 animate-gradient"
                    style={{
                      animationDuration: '3s',
                      backgroundSize: '200% 200%',
                    }}
                  >
                    Exponential Intelligence:
                  </h2>
                </div>
                <div className="overflow-hidden mt-1">
                  <p className="italic text-lg md:text-xl font-semibold text-cyan-300 animate-flicker">
                    Harness the power of <span className="text-pink-400">multiple AI Models</span> at a time!
                  </p>
                </div>
                <p className="text-sm mt-2 text-cyan-300/80">
                  ...in 7 UltrAI easy steps
                </p>
                
                {/* Decorative neon lines */}
                <div className="absolute bottom-0 left-0 w-full h-px bg-gradient-to-r from-pink-500 via-cyan-500 to-purple-500"></div>
                <div className="absolute -bottom-1 left-0 w-full h-px bg-white opacity-30"></div>
              </div>
              
              {/* Billboard spotlights - interactive on hover */}
              <div className="absolute -top-4 -left-2 w-10 h-3 bg-gray-700 rounded-lg">
                <div className="absolute bottom-0 left-1 w-3 h-8 bg-yellow-500/20 transform rotate-12 origin-bottom rounded-t-xl group-hover:bg-yellow-500/40 transition-colors duration-300"></div>
                <div className="absolute bottom-0 right-1 w-3 h-8 bg-cyan-500/20 transform -rotate-12 origin-bottom rounded-t-xl group-hover:bg-cyan-500/40 transition-colors duration-300"></div>
                <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-4 h-1 bg-amber-400 rounded animate-pulse group-hover:animate-none group-hover:bg-amber-300 transition-colors duration-300"></div>
              </div>
              
              <div className="absolute -top-4 -right-2 w-10 h-3 bg-gray-700 rounded-lg">
                <div className="absolute bottom-0 left-1 w-3 h-8 bg-pink-500/20 transform rotate-12 origin-bottom rounded-t-xl group-hover:bg-pink-500/40 transition-colors duration-300"></div>
                <div className="absolute bottom-0 right-1 w-3 h-7 bg-purple-500/20 transform -rotate-12 origin-bottom rounded-t-xl group-hover:bg-purple-500/40 transition-colors duration-300"></div>
                <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-4 h-1 bg-pink-400 rounded animate-pulse group-hover:animate-none group-hover:bg-pink-300 transition-colors duration-300" style={{animationDelay: '0.5s'}}></div>
              </div>
            </div>
            
            {/* Render light rays from the spotlights */}
            <div className="absolute top-0 left-1/3 w-1/3 h-full pointer-events-none">
              <div className="absolute top-0 left-0 w-full h-16 bg-gradient-to-b from-amber-500/10 to-transparent transform -rotate-12 origin-top-left animate-pulse"></div>
              <div className="absolute top-0 right-0 w-full h-24 bg-gradient-to-b from-pink-500/10 to-transparent transform rotate-12 origin-top-right animate-pulse" style={{animationDelay: '0.7s'}}></div>
            </div>
            
            {/* Floating dust particles */}
            <div className="absolute inset-0 pointer-events-none">
              <div className="absolute top-1/4 left-1/4 w-1 h-1 bg-white opacity-40 rounded-full animate-float" style={{animationDuration: '6s'}}></div>
              <div className="absolute top-1/3 left-2/3 w-0.5 h-0.5 bg-white opacity-30 rounded-full animate-float" style={{animationDuration: '8s', animationDelay: '1s'}}></div>
              <div className="absolute top-2/3 left-1/5 w-0.5 h-0.5 bg-white opacity-20 rounded-full animate-float" style={{animationDuration: '10s', animationDelay: '2s'}}></div>
              <div className="absolute top-1/2 left-3/4 w-1 h-1 bg-white opacity-30 rounded-full animate-float" style={{animationDuration: '7s', animationDelay: '1.5s'}}></div>
            </div>
          </div>
        </div>
        
        <div className="relative z-10 flex flex-col md:flex-row mt-48">
          {/* Animated Ultra Logo */}
          <div className="absolute -top-16 right-4 md:right-8 transform rotate-6 z-20">
            <AnimatedLogoV3 
              isProcessing={isProcessing} 
              size="large" 
              theme="dark"
              color="orange"
            />
          </div>
          
          <div className="flex-1 md:pr-4">
            <div className="flex justify-between items-center mb-8">
              <h1 className="text-4xl md:text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-pink-500 via-cyan-500 to-green-500">
                UltrAI
              </h1>
              <div className="flex items-center text-xs md:text-sm text-gray-400">
                <FileText className="w-4 h-4 mr-1 text-cyan-500" />
                <span>AI Multiplier</span>
              </div>
            </div>
            
            <div className="space-y-6">
              {/* Step 1: Enter your prompt */}
              <div className={`border-2 ${prompt ? 'border-green-500 bg-green-900/10' : 'border-cyan-800 bg-gray-900/20'} rounded-lg p-4 transition-colors duration-500 relative overflow-hidden mb-3`}>
                {prompt && (
                  <div className="absolute inset-0 bg-gradient-to-r from-green-500/5 to-cyan-500/5"></div>
                )}
                <div className="relative z-10">
                  <div className="flex items-center mb-3">
                    <div className={`w-8 h-8 rounded-full ${prompt ? 'bg-green-600' : 'bg-cyan-700'} flex items-center justify-center mr-3 text-white font-bold transition-colors duration-500`}>1</div>
                    <Label className="text-lg font-bold text-green-400" htmlFor="prompt">Enter your prompt</Label>
                  </div>
                  <div className="relative">
                    <Textarea
                      id="prompt"
                      placeholder="How might I improve the security of my API endpoints?"
                      className="min-h-[100px] bg-black/40 border-cyan-800 focus:border-cyan-600 text-sm"
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                    />
                  </div>
                </div>
              </div>

              {/* Step 2: Upload documents */}
              <div className={`border-2 ${files.length > 0 ? 'border-green-500 bg-green-900/10' : 'border-cyan-800 bg-gray-900/20'} rounded-lg p-4 transition-colors duration-500 relative overflow-hidden mb-3`}>
                {files.length > 0 && (
                  <div className="absolute inset-0 bg-gradient-to-r from-green-500/5 to-cyan-500/5"></div>
                )}
                <div className="relative z-10">
                  <div className="flex items-center mb-3">
                    <div className={`w-8 h-8 rounded-full ${files.length > 0 ? 'bg-green-600' : 'bg-cyan-700'} flex items-center justify-center mr-3 text-white font-bold transition-colors duration-500`}>2</div>
                    <Label className="text-lg font-bold text-green-400">Upload documents (optional)</Label>
                  </div>
                  <DocumentUpload 
                    onFilesSelected={handleFilesSelected}
                    maxFiles={5}
                    maxSizeMB={10}
                    acceptedTypes={['.pdf', '.txt', '.doc', '.docx', '.md']}
                  />
                  
                  {(processedDocuments.length > 0 || isProcessingDocs || docError) && (
                    <div className="mt-4">
                      <DocumentViewer 
                        documents={processedDocuments}
                        isLoading={isProcessingDocs}
                        error={docError}
                      />
                    </div>
                  )}
                </div>
              </div>
              
              {/* AUTO and RANDOM Selection Buttons */}
              <div className="flex gap-2 mb-4">
                <button 
                  onClick={handleAutoSelect}
                  className="w-full py-4 text-lg font-bold rounded-lg bg-gradient-to-r from-amber-500 to-amber-700 hover:from-amber-400 hover:to-amber-600 text-white relative overflow-hidden transition-all duration-300"
                >
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-full h-full bg-gradient-to-r from-amber-400/10 to-amber-700/10 absolute transform skew-x-12 animate-pulse"></div>
                  </div>
                  <div className="relative z-10 flex flex-col items-center">
                    <span className="text-xl mb-1">AUTO</span>
                    <span className="text-sm font-normal">Let UltrAI choose the best search parameters and models for my query</span>
                    <span className="text-xs mt-1 text-amber-200">(free service)</span>
                  </div>
                </button>
                
                <button 
                  onClick={handleRandomSelect}
                  className="w-full py-4 text-lg font-bold rounded-lg bg-gradient-to-r from-purple-500 to-pink-700 hover:from-purple-400 hover:to-pink-600 text-white relative overflow-hidden transition-all duration-300"
                >
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-full h-full bg-gradient-to-r from-purple-400/10 to-pink-700/10 absolute transform -skew-x-12 animate-pulse"></div>
                  </div>
                  <div className="relative z-10 flex flex-col items-center">
                    <span className="text-xl mb-1">RANDOM</span>
                    <span className="text-sm font-normal">Throw caution to the wind!</span>
                    <span className="text-xs mt-1 text-pink-200">(feeling lucky?)</span>
                  </div>
                </button>
              </div>

              <div className="auto-steps-container relative">
                {/* Step 3: Select LLMs */}
                <div className={`border-2 ${selectedLLMs.length > 0 ? 'border-green-500 bg-green-900/10' : 'border-cyan-800 bg-gray-900/20'} rounded-lg p-4 transition-colors duration-500 relative overflow-hidden mb-3`}>
                  {selectedLLMs.length > 0 && (
                    <div className="absolute inset-0 bg-gradient-to-r from-green-500/5 to-cyan-500/5"></div>
                  )}
                  <div className="relative z-10">
                    <div className="flex items-center mb-3">
                      <div className={`w-8 h-8 rounded-full ${selectedLLMs.length > 0 ? 'bg-green-600' : 'bg-cyan-700'} flex items-center justify-center mr-3 text-white font-bold transition-colors duration-500`}>3</div>
                      <Label className="text-lg font-bold text-green-400">Select 2+ models to run your analysis</Label>
                    </div>
                    <div className="space-y-2">
                      <Label className="text-cyan-300">Select models</Label>
                      {renderModelOptions()}
                    </div>
                  </div>
                </div>

                {/* Step 4: Select Ultra Synthesizer */}
                <div className={`border-2 ${ultraLLM ? 'border-green-500 bg-green-900/10' : 'border-cyan-800 bg-gray-900/20'} rounded-lg p-4 transition-colors duration-500 relative overflow-hidden mb-3`}>
                  {ultraLLM && (
                    <div className="absolute inset-0 bg-gradient-to-r from-green-500/5 to-cyan-500/5"></div>
                  )}
                  <div className="relative z-10">
                    <div className="flex items-center mb-3">
                      <div className={`w-8 h-8 rounded-full ${ultraLLM ? 'bg-green-600' : 'bg-cyan-700'} flex items-center justify-center mr-3 text-white font-bold transition-colors duration-500`}>4</div>
                      <Label className="text-lg font-bold text-green-400">Select the model to serve as the UltrAI synthesizer</Label>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      {llmOptions.map((option) => (
                        <div
                          key={option.id}
                          onClick={() => handleUltraChange(option.id)}
                          className={`
                            relative border rounded-md p-2 cursor-pointer transition-colors
                            flex items-center justify-between
                            ${ultraLLM === option.id ? 'bg-gray-800/80 border-cyan-500' : 'bg-gray-900/30 border-gray-800 hover:border-gray-700'}
                          `}
                        >
                          {ultraLLM === option.id && (
                            <div className="absolute top-2 right-2">
                              <div className="w-3 h-3 rounded-full bg-cyan-500"></div>
                            </div>
                          )}
                          <div className="flex items-center gap-2">
                            <option.icon className="w-5 h-5 text-cyan-400" />
                            <h3 className="font-medium">{option.label}</h3>
                          </div>
                          <Radio checked={ultraLLM === option.id} />
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                
                {/* Step 5: Choose Analysis Type */}
                <div className={`border-2 ${pattern ? 'border-green-500 bg-green-900/10' : 'border-cyan-800 bg-gray-900/20'} rounded-lg p-4 transition-colors duration-500 relative overflow-hidden mb-3`}>
                  {pattern && (
                    <div className="absolute inset-0 bg-gradient-to-r from-green-500/5 to-cyan-500/5"></div>
                  )}
                  <div className="relative z-10">
                    <div className="flex items-center mb-3">
                      <div className={`w-8 h-8 rounded-full ${pattern ? 'bg-green-600' : 'bg-cyan-700'} flex items-center justify-center mr-3 text-white font-bold transition-colors duration-500`}>5</div>
                      <Label className="text-lg font-bold text-green-400">Choose how you want the models to multiply their intelligence</Label>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {analysisPatterns.map((option) => (
                        <div
                          key={option.id}
                          onClick={() => setPattern(option.id)}
                          className={`
                            border rounded-md p-2 cursor-pointer transition-colors
                            flex flex-col space-y-1
                            ${pattern === option.id ? 'bg-cyan-900/30 border-cyan-500' : 'bg-gray-900/30 border-gray-800 hover:border-gray-700'}
                          `}
                        >
                          <div className="flex items-center space-x-2">
                            {option.icon}
                            <span className="font-medium">{option.label}</span>
                          </div>
                          <p className="text-xs text-gray-400">{option.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Transparent curtain overlay that appears after AUTO is clicked */}
                <div className="auto-curtain hidden absolute inset-0 bg-gray-900/70 backdrop-blur-[2px] rounded-lg z-20 flex flex-col items-center justify-center transition-all duration-500" style={{ display: 'none' }}>
                  <div className="text-center p-4">
                    <Zap className="w-8 h-8 text-amber-400 mx-auto mb-2" />
                    <h3 className="text-lg font-bold text-cyan-300 mb-1">AUTO Selected!</h3>
                    <p className="text-sm text-cyan-400">UltrAI has automatically configured these settings for you</p>
                    <div className="flex flex-wrap justify-center gap-2 mt-3">
                      <div className="bg-gray-800/80 py-1 px-3 rounded-full text-xs border border-cyan-800">3 Models</div>
                      <div className="bg-gray-800/80 py-1 px-3 rounded-full text-xs border border-cyan-800">Claude 3.7 Synth</div>
                      <div className="bg-gray-800/80 py-1 px-3 rounded-full text-xs border border-cyan-800">Confidence Analysis</div>
                    </div>
                    <button 
                      onClick={resetAutoSelections}
                      className="mt-4 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-cyan-300 rounded-md border border-cyan-700 text-sm transition-colors"
                    >
                      Reset and Choose Manually
                    </button>
                  </div>
                </div>
              </div>
              
              {error && (
                <div className="mt-6 flex items-center gap-2 text-red-400 bg-red-900/20 p-3 rounded-md">
                  <AlertCircle className="w-5 h-5" />
                  <span>{error}</span>
                </div>
              )}
              
              {isComplete && output && (
                <div className="mt-8 p-4 bg-black border border-green-900 rounded-lg">
                  <h3 className="text-lg font-bold text-green-400 mb-2">Results</h3>
                  <pre className="whitespace-pre-wrap text-gray-300 font-mono text-sm overflow-auto max-h-96 p-4 bg-gray-900/50 rounded border border-gray-800">
                    {output}
                  </pre>
                </div>
              )}
            </div>
          </div>
          
          <div className="md:w-1/3 mt-8 md:mt-0 md:border-l md:border-cyan-900/30 md:pl-4">
            <div className="sticky top-4 space-y-6">
              <StatusKey />
              {/* Step 6: Choose Add-ons with breathing border effect */}
              <div 
                className="border-2 border-cyan-800 rounded-lg p-4 bg-gray-900/30 relative overflow-hidden addon-container neon-border"
                style={{ animation: 'borderPulse 4s infinite' }}
              >
                <div className="absolute inset-0 border-2 border-cyan-500/40 rounded-lg" style={{ filter: 'blur(10px)' }}></div>
                <div className="relative z-10">
                  <div className="flex items-center mb-4">
                    <div className="w-8 h-8 rounded-full bg-cyan-700 flex items-center justify-center mr-3 text-white font-bold">6</div>
                    <Label className="text-lg font-bold text-green-400">Add special features</Label>
                  </div>
                  
                  {/* Quick toggles for popular add-ons with uniform layout and prices */}
                  <div className="space-y-2 mb-3">
                    {addonOptions.slice(0, 4).map((addon) => (
                      <div 
                        key={addon.id}
                        onClick={() => handleAddonChange(addon.id)}
                        className={`
                          px-3 py-2 rounded border cursor-pointer transition-colors flex items-center justify-between
                          ${selectedAddons.includes(addon.id) ? 'bg-cyan-900/50 border-cyan-500' : 'bg-gray-900/30 border-gray-800 hover:bg-gray-900/50'}
                        `}
                      >
                        <div className="flex items-center">
                          <addon.icon className={`w-4 h-4 mr-2 ${selectedAddons.includes(addon.id) ? 'text-cyan-400' : 'text-gray-400'}`} />
                          <p className="text-xs font-medium">{addon.label}</p>
                        </div>
                        <Checkbox 
                          checked={selectedAddons.includes(addon.id)}
                          className={selectedAddons.includes(addon.id) ? "border-cyan-500" : ""}
                        />
                      </div>
                    ))}
                  </div>
                  
                  {/* Accordion for more options with prices */}
                  <div className="space-y-2">
                    <details className="group">
                      <summary className="flex items-center justify-between cursor-pointer list-none text-sm text-cyan-400 hover:text-cyan-300 py-1">
                        <span>More add-ons...</span>
                        <span className="transform group-open:rotate-180 transition-transform">▼</span>
                      </summary>
                      <div className="space-y-2 pt-2">
                        {addonOptions.slice(4).map((addon) => (
                          <div 
                            key={addon.id}
                            onClick={() => handleAddonChange(addon.id)} 
                            className={`
                              px-3 py-2 rounded border cursor-pointer transition-colors flex items-center justify-between
                              ${selectedAddons.includes(addon.id) ? 'bg-cyan-900/50 border-cyan-500' : 'bg-gray-900/30 border-gray-800 hover:bg-gray-900/50'}
                            `}
                          >
                            <div className="flex items-center">
                              <addon.icon className={`w-4 h-4 mr-2 ${selectedAddons.includes(addon.id) ? 'text-cyan-400' : 'text-gray-400'}`} />
                              <p className="text-xs font-medium">{addon.label}</p>
                            </div>
                            <Checkbox 
                              checked={selectedAddons.includes(addon.id)}
                              className={selectedAddons.includes(addon.id) ? "border-cyan-500" : ""}
                            />
                          </div>
                        ))}
                      </div>
                    </details>
                    
                    {/* Fact Check option with price */}
                    <div
                      onClick={() => setIncludeFactCheck(!includeFactCheck)}
                      className={`
                        px-3 py-2 rounded border cursor-pointer transition-colors flex items-center justify-between
                        ${includeFactCheck ? 'bg-cyan-900/50 border-cyan-500' : 'bg-gray-900/30 border-gray-800 hover:bg-gray-900/50'}
                      `}
                    >
                      <div className="flex items-center">
                        <AlertCircle className={`w-4 h-4 mr-2 ${includeFactCheck ? 'text-cyan-400' : 'text-gray-400'}`} />
                        <p className="text-xs font-medium">Fact check results</p>
                      </div>
                      <Checkbox 
                        checked={includeFactCheck}
                        className={includeFactCheck ? "border-cyan-500" : ""}
                      />
                    </div>
                    
                    {/* Perspective option with conditional input and price */}
                    <div>
                      <div 
                        onClick={() => setIncludePerspective(!includePerspective)}
                        className={`
                          px-3 py-2 rounded border cursor-pointer transition-colors flex items-center justify-between
                          ${includePerspective ? 'bg-cyan-900/50 border-cyan-500' : 'bg-gray-900/30 border-gray-800 hover:bg-gray-900/50'}
                        `}
                      >
                        <div className="flex items-center">
                          <Eye className={`w-4 h-4 mr-2 ${includePerspective ? 'text-cyan-400' : 'text-gray-400'}`} />
                          <p className="text-xs font-medium">Alternative perspective</p>
                        </div>
                        <Checkbox 
                          checked={includePerspective}
                          className={includePerspective ? "border-cyan-500" : ""}
                        />
                      </div>
                      
                      {includePerspective && (
                        <div className="mt-2">
                          <input
                            type="text"
                            placeholder="e.g., economist, historian, skeptic"
                            className="w-full p-2 text-xs rounded bg-gray-900/50 border border-cyan-900 focus:border-cyan-500 text-cyan-100"
                            value={perspective}
                            onChange={(e) => setPerspective(e.target.value)}
                          />
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="mt-3 pt-3 border-t border-cyan-900/30">
                    <div className="flex justify-between items-center">
                      <p className="text-xs text-cyan-400 flex items-center">
                        <Award className="w-3 h-3 mr-1" />
                        <span>{selectedAddons.length + (includeFactCheck ? 1 : 0) + (includePerspective ? 1 : 0)} features</span>
                      </p>
                      <p className="text-xs text-cyan-300">+${calculateAddonPrice().toFixed(2)}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Step 7: Output Format (Moved here from main column) */}
              <div className={`border-2 ${outputFormat ? 'border-green-500 bg-green-900/10' : 'border-cyan-800 bg-gray-900/20'} rounded-lg p-4 transition-colors duration-500 relative overflow-hidden`}>
                {outputFormat && (
                  <div className="absolute inset-0 bg-gradient-to-r from-green-500/5 to-cyan-500/5"></div>
                )}
                <div className="relative z-10">
                  <div className="flex items-center mb-4">
                    <div className={`w-8 h-8 rounded-full ${outputFormat ? 'bg-green-600' : 'bg-cyan-700'} flex items-center justify-center mr-3 text-white font-bold transition-colors duration-500`}>7</div>
                    <Label className="text-lg font-bold text-green-400">Select output format</Label>
                  </div>
                  <div className="grid grid-cols-1 gap-2">
                    {outputFormats.map((format) => (
                      <div
                        key={format.id}
                        onClick={() => setOutputFormat(format.id)}
                        className={`
                          border rounded-md p-3 cursor-pointer transition-colors
                          flex items-center justify-between
                          ${outputFormat === format.id ? 'bg-cyan-900/30 border-cyan-500' : 'bg-gray-900/30 border-gray-800 hover:border-gray-700'}
                        `}
                      >
                        <div className="flex items-center space-x-2">
                          <format.icon className={`w-4 h-4 ${outputFormat === format.id ? 'text-cyan-400' : 'text-gray-400'}`} />
                          <div>
                            <p className="text-xs font-medium">{format.label}</p>
                            <p className="text-xs text-gray-400">{format.description}</p>
                          </div>
                        </div>
                        <Checkbox 
                          checked={outputFormat === format.id}
                          className={outputFormat === format.id ? "border-cyan-500" : ""}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="bg-gradient-to-r from-purple-900 via-cyan-800 to-pink-900 p-3 rounded-lg border border-cyan-500 relative overflow-hidden">
                <div className="absolute inset-0 border-2 border-cyan-500/40 rounded-lg" style={{ filter: 'blur(10px)' }}></div>
                <div className="relative z-10">
                  <h2 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-400 via-cyan-300 to-purple-400 mb-2 flex items-center">
                    <Feather className="w-5 h-5 mr-2 text-amber-400" />
                    Price Estimate
                  </h2>
                  
                  <div className="bg-black/50 rounded-lg p-3 backdrop-blur-sm">
                    <PricingDisplay 
                      selectedModels={[...selectedLLMs, ultraLLM].filter(Boolean) as string[]} 
                      promptText={prompt}
                      attachments={files}
                      analysisType={pattern}
                      showDetails={true}
                      className="justify-center text-xl"
                      addonCost={calculateAddonPrice()}
                    />
                  </div>
                </div>
              </div>
              
              <div className="mt-6">
                <Button
                  className={`
                    w-full py-6 text-lg font-bold rounded-lg 
                    relative overflow-hidden transition-all duration-500
                    ${!isProcessing && (selectedLLMs.length >= 2 && ultraLLM) ?
                      'bg-gradient-to-r from-cyan-600 to-blue-700 hover:from-cyan-500 hover:to-blue-600 text-white' :
                      'bg-gray-800 text-gray-400 cursor-not-allowed'
                    }
                  `}
                  disabled={isProcessing || selectedLLMs.length < 2 || !ultraLLM}
                  onClick={handleSubmit}
                >
                  {isProcessing ? (
                    <span className="flex items-center">
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Processing...
                    </span>
                  ) : (
                    <span>Run UltrAI Analysis</span>
                  )}
                </Button>
              </div>
              
              {isProcessing && (
                <div className="mt-6">
                  <CyberpunkProgressBar 
                    step={currentStep} 
                    totalSteps={steps.length} 
                    currentMessage={steps[currentStep]} 
                  />
                </div>
              )}
              
              <div className="mt-4 bg-black/30 p-3 rounded-lg border border-cyan-900/30">
                <h3 className="text-sm font-bold text-cyan-400 mb-2">
                  Pricing Breakdown
                </h3>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-cyan-500 rounded-full mr-2"></div>
                      <span>Models</span>
                    </div>
                    <span className="text-cyan-300">
                      {selectedLLMs.length + (ultraLLM ? 1 : 0)}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-cyan-500 rounded-full mr-2"></div>
                      <span>Prompt</span>
                    </div>
                    <span className="text-cyan-300">{prompt.length} chars</span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-cyan-500 rounded-full mr-2"></div>
                      <span>Documents</span>
                    </div>
                    <span className="text-cyan-300">{files.length} files</span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-cyan-500 rounded-full mr-2"></div>
                      <span>Add-ons</span>
                    </div>
                    <span className="text-cyan-300">
                      ${calculateAddonPrice().toFixed(2)}
                    </span>
                  </div>
                </div>
                <div className="mt-3 text-xs text-gray-500">
                  <p className="flex items-center">
                    <Award className="w-3 h-3 text-amber-500 mr-1 inline" />
                    Premium models and add-ons increase cost
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Update animation keyframes to make the border glow more intense */}
      <style>
        {`
        @keyframes borderPulse {
          0%, 100% { 
            border-color: rgba(8, 145, 178, 0.4); 
            box-shadow: 0 0 5px rgba(8, 145, 178, 0.3);
          }
          50% { 
            border-color: rgba(14, 165, 233, 1); 
            box-shadow: 0 0 25px rgba(14, 165, 233, 0.8);
          }
        }
        
        .neon-border {
          position: relative;
        }
        
        .neon-border::before {
          content: "";
          position: absolute;
          inset: -3px;
          z-index: -1;
          background: linear-gradient(90deg, #06b6d4, #0ea5e9, #06b6d4);
          border-radius: inherit;
          animation: borderGlow 3s linear infinite;
          filter: blur(8px);
          opacity: 0.7;
        }
        
        @keyframes borderGlow {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 0.8; }
        }
        
        @keyframes flicker {
          0%, 100% { opacity: 1; }
          8% { opacity: 0.8; }
          10% { opacity: 0.9; }
          20% { opacity: 1; }
          40% { opacity: 0.7; }
          42% { opacity: 1; }
          60% { opacity: 0.9; }
          80% { opacity: 1; }
        }
        
        .animate-flicker {
          animation: flicker 4s infinite;
        }
        
        @keyframes gradient {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        
        .animate-gradient {
          animation: gradient 3s ease infinite;
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0) translateX(0); opacity: 0.3; }
          25% { transform: translateY(-5px) translateX(5px); opacity: 0.5; }
          50% { transform: translateY(-8px) translateX(-3px); opacity: 0.8; }
          75% { transform: translateY(-3px) translateX(-7px); opacity: 0.4; }
        }
        
        .animate-float {
          animation: float 10s ease-in-out infinite;
        }
        
        .thinking-model-border {
          position: relative;
          overflow: hidden;
        }
        
        .thinking-model-border::before {
          content: "";
          position: absolute;
          inset: -4px;
          background: linear-gradient(90deg, #c084fc, #a855f7, #8b5cf6);
          border-radius: inherit;
          animation: thinkingBorderGlow 3s ease-in-out infinite;
          filter: blur(6px);
          opacity: 0.7;
          z-index: -1;
        }
        
        @keyframes thinkingBorderGlow {
          0%, 100% { opacity: 0.4; transform: scale(0.98); }
          50% { opacity: 0.8; transform: scale(1.01); }
        }
        `}
      </style>
      
      {/* Add ErrorDisplay at the end of the component */}
      <ErrorDisplay errors={errors} onDismiss={dismissError} />
    </div>
  );
}