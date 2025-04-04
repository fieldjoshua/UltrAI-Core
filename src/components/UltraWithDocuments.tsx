'use client'

import React, { useState, useEffect } from 'react'
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

const API_URL = 'http://localhost:8080'

const llmOptions = [
  { 
    id: 'gpt4o', 
    label: 'GPT-4o (128k)', 
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
    label: 'GPT-o1 (200k)', 
    price: 0.075, 
    icon: Zap, 
    contextWindow: '200k',
    inputCost: 0.015,
    outputCost: 0.060,
    isThinkingModel: true,
    details: 'OpenAI\'s most powerful model with exceptional reasoning and 200k context'
  },
  { 
    id: 'gpto3mini', 
    label: 'GPT-o3 mini (200k)', 
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
  { id: 'private', label: 'Keep data private', description: 'Process everything locally without sending to external servers', icon: Shield, price: 0.05 },
  { id: 'anti_ai_detect', label: 'Guard against AI detection', description: 'Make output less identifiable as AI-generated', icon: Eye, price: 0.05 },
  { id: 'citation', label: 'Include citations/sources', description: 'Add references and sources to support claims', icon: Quote, price: 0.05 },
  { id: 'express', label: 'Express mode', description: 'Prioritize speed over comprehensiveness', icon: Clock, price: 0.03 },
]

// Output format options
const outputFormats = [
  { id: 'text', label: 'Text only', description: 'Plain text output', price: 0.00, icon: FileText },
  { id: 'standard', label: 'Standard formatting', description: 'Basic formatting with headers and lists', price: 0.00, icon: FileText },
  { id: 'google', label: 'Google Docs/Sheets', description: 'Formatted for Google Workspace', price: 0.10, icon: FileText },
  { id: 'microsoft', label: 'Microsoft Word/Office', description: 'Formatted for Microsoft Office', price: 0.15, icon: FileText },
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
        setDocError('Failed to process documents');
      }
    } catch (err) {
      console.error('Error processing files:', err);
      const errorWithResponse = err as ErrorWithResponse;
      setDocError(errorWithResponse.response?.data?.detail || 'An error occurred while processing files');
    } finally {
      setIsProcessingDocs(false);
    }
  };

  // Handle LLM selection
  const handleLLMChange = (llmId: string) => {
    setSelectedLLMs(prev => 
      prev.includes(llmId) ? prev.filter(id => id !== llmId) : [...prev, llmId]
    )
  }
  
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
    
    // Add prices for selected add-ons
    selectedAddons.forEach(id => {
      const addon = addonOptions.find(a => a.id === id);
      if (addon) price += addon.price;
    });
    
    // Add fact check and perspective prices
    if (includeFactCheck) price += 0.15;
    if (includePerspective) price += 0.10;
    
    // Add output format price
    const format = outputFormats.find(f => f.id === outputFormat);
    if (format) price += format.price;
    
    return price;
  };
  
  // Run analysis with or without documents
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }
    
    if (selectedLLMs.length < 2) {
      setError('Please select at least two LLMs');
      return;
    }
    
    if (!ultraLLM) {
      setError('Please select an Ultra LLM');
      return;
    }
    
    setError(null);
    setIsProcessing(true);
    setIsComplete(false);
    setOutput('');
    setCurrentStep(0);
    
    try {
      // Initialization phase with visual feedback
      await new Promise(resolve => setTimeout(resolve, 1200));
      
      let response;
      
      // Build options object with all selections
      const options = {
        keepDataPrivate: selectedAddons.includes('private'),
        antiAIDetect: selectedAddons.includes('anti_ai_detect'),
        includeCitations: selectedAddons.includes('citation'),
        includeFactCheck,
        includePerspective,
        perspective: includePerspective ? perspective : '',
        outputFormat,
        addonPrice: calculateAddonPrice(),
      };
      
      // If we have files, use the analyze-with-docs endpoint
      if (files.length > 0) {
        setCurrentStep(1);
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        const formData = new FormData();
        formData.append('prompt', prompt);
        formData.append('selectedModels', JSON.stringify(selectedLLMs));
        formData.append('ultraModel', ultraLLM);
        formData.append('pattern', analysisPatterns.find(p => p.id === pattern)?.label || 'Confidence Analysis');
        formData.append('options', JSON.stringify(options));
        
        files.forEach(file => {
          formData.append('files', file);
        });
        
        response = await axios.post(`${API_URL}/api/analyze-with-docs`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
      } else {
        // Otherwise use the regular analyze endpoint
        response = await axios.post(`${API_URL}/api/analyze`, {
          prompt,
          selectedModels: selectedLLMs,
          ultraModel: ultraLLM,
          pattern: analysisPatterns.find(p => p.id === pattern)?.label || 'Confidence Analysis',
          options
        });
      }
      
      // Show analyzing prompt
      setCurrentStep(2);
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Show initial responses
      setCurrentStep(3);
      let currentOutput = `Initial Responses:\n`;
      
      for (const [model, resp] of Object.entries(response.data.data.initial_responses)) {
        currentOutput += `\n${model.toUpperCase()}:\n${resp}\n`;
      }
      
      setOutput(currentOutput);
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Show meta responses
      setCurrentStep(4);
      currentOutput += `\n\nMeta Responses:\n`;
      
      for (const [model, resp] of Object.entries(response.data.data.meta_responses)) {
        currentOutput += `\n${model.toUpperCase()}:\n${resp}\n`;
      }
      
      setOutput(currentOutput);
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Show ultra responses
      setCurrentStep(5);
      currentOutput += `\n\nUltra Analysis:\n`;
      
      for (const [model, resp] of Object.entries(response.data.data.hyper_responses)) {
        currentOutput += `\n${model.toUpperCase()}:\n${resp}\n`;
      }
      
      setOutput(currentOutput);
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Show ultra response
      setCurrentStep(6);
      currentOutput += `\n\nUltra Response:\n${response.data.data.ultra}\n`;
      
      setOutput(currentOutput);
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Show packaging results
      setCurrentStep(7);
      
      // Add document metadata if available
      if (response.data.document_metadata) {
        const meta = response.data.document_metadata;
        currentOutput += `\n\nDocument Analysis:\n`;
        currentOutput += `Documents Used: ${meta.documents_used.join(', ')}\n`;
        currentOutput += `Chunks Used: ${meta.chunks_used}\n`;
      }
      
      currentOutput += `\nOutput Directory: ${response.data.output_directory}\n`;
      setOutput(currentOutput);
      
      // Allow time for the final progress animation to complete
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setIsComplete(true);
    } catch (err) {
      console.error('Error during analysis:', err);
      const errorWithResponse = err as ErrorWithResponse;
      setError(errorWithResponse.response?.data?.detail || 'An error occurred during analysis');
    } finally {
      setIsProcessing(false);
    }
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
    `;
    
    // Append to head
    document.head.appendChild(styleEl);
    
    // Cleanup
    return () => {
      document.head.removeChild(styleEl);
    };
  }, []);
  
  return (
    <div className="min-h-screen bg-gray-900 text-cyan-300 font-mono p-4 md:p-8">
      <div className="max-w-7xl mx-auto bg-black border-4 border-cyan-700 rounded-lg shadow-2xl shadow-cyan-500/20 p-4 md:p-8 relative overflow-hidden">
        {/* Cyberpunk-style animated neon effect for tagline */}
        <div className="absolute top-0 right-0 left-0 p-4 overflow-hidden">
          <div className="relative transform -rotate-2 max-w-2xl mx-auto">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-900 via-cyan-800 to-pink-900 rounded-lg opacity-70 animate-pulse"></div>
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
                ...in 6 UltrAI easy steps
              </p>
              {/* Decorative neon lines */}
              <div className="absolute bottom-0 left-0 w-full h-px bg-gradient-to-r from-pink-500 via-cyan-500 to-purple-500"></div>
              <div className="absolute -bottom-1 left-0 w-full h-px bg-white opacity-30"></div>
            </div>
          </div>
        </div>
        
        <div className="relative z-10 flex flex-col md:flex-row mt-28">
          {/* Spraypaint stencil logo */}
          <div className="absolute -top-16 right-4 md:right-8 transform rotate-12 z-20">
            <div className="relative w-24 h-24 md:w-28 md:h-28">
              <div className="absolute inset-0 bg-black rounded-lg border-2 border-cyan-800"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <h1 className="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-pink-500 via-cyan-500 to-green-500" style={{fontFamily: 'Impact, sans-serif'}}>
                  UltrAI
                </h1>
                <div className="absolute inset-0 bg-black/5 backdrop-blur-[0.5px]"></div>
                <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black/20" style={{maskImage: 'url("data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'100%\' height=\'100%\'><rect width=\'100%\' height=\'100%\' fill=\'black\' rx=\'8\' ry=\'8\'/></svg>")'}}></div>
                {/* Spray effect */}
                <div className="absolute inset-0 opacity-50" style={{
                  background: 'radial-gradient(circle at 30% 30%, rgba(255,255,255,0.1) 1px, transparent 1px), radial-gradient(circle at 70% 40%, rgba(255,255,255,0.1) 1px, transparent 1px), radial-gradient(circle at 40% 60%, rgba(255,255,255,0.1) 1px, transparent 1px), radial-gradient(circle at 60% 70%, rgba(255,255,255,0.1) 1px, transparent 1px)',
                  backgroundSize: '4px 4px'
                }}></div>
              </div>
            </div>
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
            
            <div className="space-y-8">
              {/* Step 1: Ask your question */}
              <div className={`border-2 ${prompt ? 'border-green-500 bg-green-900/10' : 'border-cyan-800 bg-gray-900/20'} rounded-lg p-4 transition-colors duration-500 relative overflow-hidden`}>
                {prompt && (
                  <div className="absolute inset-0 bg-gradient-to-r from-green-500/5 to-cyan-500/5"></div>
                )}
                <div className="relative z-10">
                  <div className="flex items-center mb-4">
                    <div className={`w-8 h-8 rounded-full ${prompt ? 'bg-green-600' : 'bg-cyan-700'} flex items-center justify-center mr-3 text-white font-bold transition-colors duration-500`}>1</div>
                    <Label htmlFor="prompt" className="text-lg font-bold text-green-400">Ask whatever you like</Label>
                  </div>
                  <Textarea
                    id="prompt"
                    placeholder="Enter your question and feel free to attach documents to consider with your input"
                    className="mt-2 h-32 bg-gray-900/50 border-cyan-900 focus:border-cyan-500 text-cyan-100"
                    value={prompt}
                    onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setPrompt(e.target.value)}
                  />
                </div>
              </div>
              
              {/* Step 2: Upload documents */}
              <div className={`border-2 ${files.length > 0 ? 'border-green-500 bg-green-900/10' : 'border-cyan-800 bg-gray-900/20'} rounded-lg p-4 transition-colors duration-500 relative overflow-hidden`}>
                {files.length > 0 && (
                  <div className="absolute inset-0 bg-gradient-to-r from-green-500/5 to-cyan-500/5"></div>
                )}
                <div className="relative z-10">
                  <div className="flex items-center mb-4">
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
              
              {/* Step 3: Select Models */}
              <div className={`border-2 ${selectedLLMs.length > 0 ? 'border-green-500 bg-green-900/10' : 'border-cyan-800 bg-gray-900/20'} rounded-lg p-4 transition-colors duration-500 relative overflow-hidden`}>
                {selectedLLMs.length > 0 && (
                  <div className="absolute inset-0 bg-gradient-to-r from-green-500/5 to-cyan-500/5"></div>
                )}
                <div className="relative z-10">
                  <div className="flex items-center mb-4">
                    <div className={`w-8 h-8 rounded-full ${selectedLLMs.length > 0 ? 'bg-green-600' : 'bg-cyan-700'} flex items-center justify-center mr-3 text-white font-bold transition-colors duration-500`}>3</div>
                    <Label className="text-lg font-bold text-green-400">Select models to assist with your request</Label>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {llmOptions.map((llm) => (
                      <div 
                        key={llm.id}
                        className={`
                          flex items-center space-x-4 p-4 rounded-lg border transition-all duration-300
                          ${selectedLLMs.includes(llm.id) ? 
                            llm.isThinkingModel ? 
                              'bg-purple-900/30 border-purple-500 shadow-[0_0_12px_rgba(168,85,247,0.3)]' : 
                              'bg-green-900/30 border-green-500' : 
                            llm.isThinkingModel ?
                              'bg-purple-900/10 border-purple-700/50 hover:border-purple-500 hover:bg-purple-900/20' :
                              'bg-gray-900/30 border-gray-800 hover:bg-opacity-40'
                          }
                          relative group
                        `}
                      >
                        <Checkbox 
                          id={llm.id} 
                          checked={selectedLLMs.includes(llm.id)}
                          onCheckedChange={() => handleLLMChange(llm.id)}
                          className={selectedLLMs.includes(llm.id) ? 
                            llm.isThinkingModel ? "border-purple-500" : "border-green-500" : 
                            llm.isThinkingModel ? "border-purple-700" : "border-gray-500"}
                        />
                        <Label 
                          htmlFor={llm.id} 
                          className="flex items-center justify-between w-full cursor-pointer"
                        >
                          <div className="flex items-center space-x-2">
                            <llm.icon className={`w-5 h-5 ${
                              selectedLLMs.includes(llm.id) ? 
                                llm.isThinkingModel ? 'text-purple-400' : 'text-green-400' : 
                                llm.isThinkingModel ? 'text-purple-400/70' : 'text-gray-400'
                            }`} />
                            <div>
                              <span className={llm.isThinkingModel ? 'font-semibold' : ''}>{llm.label}</span>
                              {llm.isThinkingModel && (
                                <span className="block text-xs text-purple-300 mt-0.5">Thinking model</span>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center">
                            <span className="text-amber-300 text-xs font-mono ml-2">${llm.price.toFixed(4)}</span>
                            <div className="relative group/tooltip">
                              <AlertCircle className="w-4 h-4 ml-2 text-gray-400 cursor-help" />
                              <div className="absolute right-0 bottom-full mb-2 opacity-0 group-hover/tooltip:opacity-100 transition-opacity duration-200 invisible group-hover/tooltip:visible z-50">
                                <div className="bg-gray-900 border border-gray-700 rounded-md p-3 shadow-xl">
                                  <ModelInfoTooltip model={llm} />
                                </div>
                              </div>
                            </div>
                          </div>
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              {/* Step 4: Select Ultra Synthesizer */}
              <div className={`border-2 ${ultraLLM ? 'border-green-500 bg-green-900/10' : 'border-cyan-800 bg-gray-900/20'} rounded-lg p-4 transition-colors duration-500 relative overflow-hidden`}>
                {ultraLLM && (
                  <div className="absolute inset-0 bg-gradient-to-r from-green-500/5 to-cyan-500/5"></div>
                )}
                <div className="relative z-10">
                  <div className="flex items-center mb-4">
                    <div className={`w-8 h-8 rounded-full ${ultraLLM ? 'bg-green-600' : 'bg-cyan-700'} flex items-center justify-center mr-3 text-white font-bold transition-colors duration-500`}>4</div>
                    <Label className="text-lg font-bold text-green-400">Select the model to serve as the UltrAI synthesizer</Label>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {llmOptions.map((llm) => {
                      // Determine if this is a thinking model
                      const isThinkingModel = llm.isThinkingModel;
                      
                      return (
                        <div 
                          key={`ultra-${llm.id}`} 
                          className={`
                            flex items-center space-x-4 p-4 rounded-lg border transition-all duration-300
                            ${ultraLLM === llm.id ? 
                              isThinkingModel ? 
                                'bg-purple-900/30 border-purple-500 shadow-[0_0_15px_rgba(168,85,247,0.4)] thinking-model-border' : 
                                'bg-green-900/30 border-green-500' : 
                              isThinkingModel ?
                                'bg-purple-900/10 border-purple-700/50 hover:border-purple-500 hover:bg-purple-900/20' :
                                'bg-gray-900/30 border-gray-800 hover:bg-opacity-40'
                            }
                            relative group
                          `}
                        >
                          <Checkbox 
                            id={`ultra-${llm.id}`} 
                            checked={ultraLLM === llm.id}
                            onCheckedChange={() => handleUltraChange(llm.id)}
                            className={ultraLLM === llm.id ? 
                              isThinkingModel ? "border-purple-500" : "border-green-500" : 
                              isThinkingModel ? "border-purple-700" : "border-gray-500"}
                          />
                          <Label 
                            htmlFor={`ultra-${llm.id}`} 
                            className="flex items-center justify-between w-full cursor-pointer"
                          >
                            <div className="flex items-center space-x-2">
                              <llm.icon className={`w-5 h-5 ${
                                ultraLLM === llm.id ? 
                                  isThinkingModel ? 'text-purple-400' : 'text-green-400' : 
                                  isThinkingModel ? 'text-purple-400/70' : 'text-gray-400'
                              }`} />
                              <div>
                                <span className={isThinkingModel ? 'font-bold' : ''}>{llm.label}</span>
                                {isThinkingModel && (
                                  <span className="block text-xs text-purple-300 mt-1">Recommended for synthesis</span>
                                )}
                              </div>
                            </div>
                            <div className="flex items-center">
                              <span className="text-amber-300 text-xs font-mono ml-2">${llm.price.toFixed(4)}</span>
                              <div className="relative group/tooltip">
                                <AlertCircle className="w-4 h-4 ml-2 text-gray-400 cursor-help" />
                                <div className="absolute right-0 bottom-full mb-2 opacity-0 group-hover/tooltip:opacity-100 transition-opacity duration-200 invisible group-hover/tooltip:visible z-50">
                                  <div className="bg-gray-900 border border-gray-700 rounded-md p-3 shadow-xl">
                                    <ModelInfoTooltip model={llm} />
                                  </div>
                                </div>
                              </div>
                            </div>
                          </Label>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
              
              {/* Step 5: Choose Analysis Type */}
              <div className={`border-2 ${pattern ? 'border-green-500 bg-green-900/10' : 'border-cyan-800 bg-gray-900/20'} rounded-lg p-4 transition-colors duration-500 relative overflow-hidden`}>
                {pattern && (
                  <div className="absolute inset-0 bg-gradient-to-r from-green-500/5 to-cyan-500/5"></div>
                )}
                <div className="relative z-10">
                  <div className="flex items-center mb-4">
                    <div className={`w-8 h-8 rounded-full ${pattern ? 'bg-green-600' : 'bg-cyan-700'} flex items-center justify-center mr-3 text-white font-bold transition-colors duration-500`}>5</div>
                    <Label className="text-lg font-bold text-green-400">Choose how you want the models to multiply their intelligence</Label>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {analysisPatterns.map((option) => (
                      <div
                        key={option.id}
                        onClick={() => setPattern(option.id)}
                        className={`
                          border rounded-md p-3 cursor-pointer transition-colors
                          flex flex-col space-y-2
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
          
          <div className="md:w-1/3 mt-8 md:mt-0 md:border-l md:border-cyan-900/30 md:pl-4">
            <div className="sticky top-4 space-y-6">
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
                        <div className="text-xs text-cyan-500">+${addon.price.toFixed(2)}</div>
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
                            <div className="text-xs text-cyan-500">+${addon.price.toFixed(2)}</div>
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
                      <div className="text-xs text-cyan-500">+$0.15</div>
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
                        <div className="text-xs text-cyan-500">+$0.10</div>
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
                        <div className="text-xs text-cyan-400">{format.price > 0 ? `+$${format.price.toFixed(2)}` : 'Free'}</div>
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
    </div>
  );
}