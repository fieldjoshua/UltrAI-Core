'use client'

import React, { useState } from 'react'
import { Button } from "./ui/button"
import { Checkbox } from "./ui/checkbox"
import { Label } from "./ui/label"
import { Textarea } from "../components/ui/textarea"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs"
import { 
  Loader2, 
  Zap, 
  Lock, 
  Cpu, 
  FileText,
  AlertCircle,
  Brain 
} from 'lucide-react'
import axios from 'axios'

import { DocumentUpload } from './DocumentUpload'
import { DocumentViewer } from './DocumentViewer'

const API_URL = 'http://localhost:8080'

const llmOptions = [
  { id: 'chatgpt', label: 'GPT-4.0', price: 10, icon: Zap },
  { id: 'claude', label: 'Claude 3.5', price: 7, icon: Lock },
  { id: 'gemini', label: 'Gemini', price: 6, icon: Cpu },
  { id: 'llama', label: 'Llama 3', price: 0, icon: Brain }
]

const analysisPatterns = [
  { id: 'confidence', label: 'Confidence Analysis', description: 'Evaluates the strength of each model response and selects the most reliable one' },
  { id: 'critique', label: 'Critique', description: 'Asks models to critically evaluate each other\'s reasoning and answers' },
  { id: 'gut', label: 'Gut Check', description: 'Rapid evaluation of different perspectives to identify the most likely correct answer' },
  { id: 'fact_check', label: 'Fact Check', description: 'Cross-verifies factual claims across multiple sources for accuracy' },
  { id: 'perspective', label: 'Perspective Analysis', description: 'Examines an issue from multiple viewpoints for comprehensive understanding' },
  { id: 'scenario', label: 'Scenario Analysis', description: 'Explores potential future outcomes and alternative possibilities' }
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
  
  // Options
  const [keepDataPrivate, setKeepDataPrivate] = useState(false)
  
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
      
      // If we have files, use the analyze-with-docs endpoint
      if (files.length > 0) {
        setCurrentStep(1);
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        const formData = new FormData();
        formData.append('prompt', prompt);
        formData.append('selectedModels', JSON.stringify(selectedLLMs));
        formData.append('ultraModel', ultraLLM);
        formData.append('pattern', analysisPatterns.find(p => p.id === pattern)?.label || 'Confidence Analysis');
        formData.append('options', JSON.stringify({ keepDataPrivate }));
        
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
          options: {
            keepDataPrivate
          }
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
  
  return (
    <div className="min-h-screen bg-gray-900 text-cyan-300 font-mono p-4 md:p-8">
      <div className="max-w-7xl mx-auto bg-black border-4 border-cyan-700 rounded-lg shadow-2xl shadow-cyan-500/20 p-4 md:p-8 relative overflow-hidden">
        <div className="relative z-10">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-4xl md:text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-pink-500 via-cyan-500 to-green-500">
              UltrAI
            </h1>
            <div className="flex items-center text-xs md:text-sm text-gray-400">
              <FileText className="w-4 h-4 mr-1 text-cyan-500" />
              <span>Document Analysis</span>
            </div>
          </div>
          
          <Tabs defaultValue="prompt" className="space-y-6">
            <TabsList className="w-full grid grid-cols-2">
              <TabsTrigger value="prompt">Query & Models</TabsTrigger>
              <TabsTrigger value="documents">Documents</TabsTrigger>
            </TabsList>
            
            <TabsContent value="prompt" className="space-y-6">
              <div>
                <Label htmlFor="prompt" className="text-lg font-bold text-green-400">Enter your prompt</Label>
                <Textarea
                  id="prompt"
                  placeholder="What would you like to ask about the documents?"
                  className="mt-2 h-32 bg-gray-900/50 border-cyan-900 focus:border-cyan-500 text-cyan-100"
                  value={prompt}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setPrompt(e.target.value)}
                />
              </div>
              
              <div className="space-y-4">
                <Label className="text-lg font-bold text-green-400">Select LLMs <span className="text-sm font-normal text-pink-400">(choose at least two)</span></Label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {llmOptions.map((llm) => (
                    <div key={llm.id} className="flex items-center space-x-4 bg-cyan-900 bg-opacity-30 p-4 rounded-lg border border-cyan-800 hover:bg-opacity-40 transition-all duration-300">
                      <Checkbox 
                        id={`llm-${llm.id}`} 
                        checked={selectedLLMs.includes(llm.id)}
                        onCheckedChange={() => handleLLMChange(llm.id)}
                        className="border-pink-500"
                      />
                      <Label htmlFor={`llm-${llm.id}`} className="flex items-center space-x-2 text-cyan-300 cursor-pointer">
                        <llm.icon className="w-5 h-5 text-green-400" />
                        <span>{llm.label}</span>
                      </Label>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="space-y-4">
                <Label className="text-lg font-bold text-green-400">Select Ultra synthesis model</Label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {llmOptions.map((llm) => (
                    <div 
                      key={`ultra-${llm.id}`} 
                      className={`
                        flex items-center space-x-4 p-4 rounded-lg border transition-all duration-300
                        ${ultraLLM === llm.id ? 
                          'bg-green-900 bg-opacity-30 border-green-700' : 
                          'bg-gray-900 bg-opacity-30 border-gray-800 hover:bg-opacity-40'
                        }
                      `}
                    >
                      <Checkbox 
                        id={`ultra-${llm.id}`} 
                        checked={ultraLLM === llm.id}
                        onCheckedChange={() => handleUltraChange(llm.id)}
                        className={ultraLLM === llm.id ? "border-green-500" : "border-gray-500"}
                      />
                      <Label htmlFor={`ultra-${llm.id}`} className="flex items-center space-x-2 text-cyan-300 cursor-pointer">
                        <llm.icon className={`w-5 h-5 ${ultraLLM === llm.id ? 'text-green-400' : 'text-gray-400'}`} />
                        <span>{llm.label}</span>
                      </Label>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="space-y-4">
                <Label className="text-lg font-bold text-green-400">Analysis Pattern</Label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {analysisPatterns.map((p) => (
                    <div 
                      key={`pattern-${p.id}`} 
                      className={`
                        p-4 rounded-lg border transition-all duration-300 cursor-pointer
                        ${pattern === p.id ? 
                          'bg-cyan-900 bg-opacity-30 border-cyan-700' : 
                          'bg-gray-900 bg-opacity-20 border-gray-800 hover:bg-opacity-30'
                        }
                      `}
                      onClick={() => setPattern(p.id)}
                    >
                      <div className="flex items-center space-x-2 mb-2">
                        <div className={`w-3 h-3 rounded-full ${pattern === p.id ? 'bg-cyan-400' : 'bg-gray-600'}`}></div>
                        <span className="font-medium">{p.label}</span>
                      </div>
                      <p className="text-xs text-gray-400">{p.description}</p>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="private" 
                  checked={keepDataPrivate}
                  onCheckedChange={() => setKeepDataPrivate(!keepDataPrivate)}
                  className="border-cyan-500"
                />
                <Label 
                  htmlFor="private" 
                  className="text-sm text-gray-300 cursor-pointer"
                >
                  Keep data private (local output only)
                </Label>
              </div>
            </TabsContent>
            
            <TabsContent value="documents" className="space-y-6">
              <div className="space-y-6">
                <DocumentUpload 
                  onFilesSelected={handleFilesSelected}
                  maxFiles={5}
                  maxSizeMB={10}
                  acceptedTypes={['.pdf', '.txt', '.doc', '.docx', '.md']}
                />
                
                <DocumentViewer 
                  documents={processedDocuments}
                  isLoading={isProcessingDocs}
                  error={docError}
                />
              </div>
            </TabsContent>
          </Tabs>
          
          {error && (
            <div className="mt-6 flex items-center gap-2 text-red-400 bg-red-900/20 p-3 rounded-md">
              <AlertCircle className="w-5 h-5" />
              <span>{error}</span>
            </div>
          )}
          
          <div className="mt-8 flex justify-center">
            <Button
              className={`
                w-full max-w-md py-6 text-lg font-bold rounded-lg 
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
                  {steps[currentStep]}...
                </span>
              ) : (
                <span>Run Analysis</span>
              )}
            </Button>
          </div>
          
          {isComplete && output && (
            <div className="mt-8 p-4 bg-black border border-green-900 rounded-lg">
              <h3 className="text-lg font-bold text-green-400 mb-2">Results</h3>
              <pre className="whitespace-pre-wrap text-gray-300 font-mono text-sm overflow-auto max-h-96 p-4 bg-gray-900/50 rounded border border-gray-800">
                {output}
              </pre>
            </div>
          )}
          
          {isProcessing && (
            <div className="mt-8">
              <CyberpunkProgressBar 
                step={currentStep} 
                totalSteps={steps.length} 
                currentMessage={steps[currentStep]} 
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}