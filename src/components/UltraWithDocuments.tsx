'use client'

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Checkbox } from './ui/checkbox';
import { Progress } from './ui/progress';
import { Zap, Award, Brain, Feather, Shield, FileText, Users, Network, Clock, Lightbulb } from 'lucide-react';

// Simplified API URL
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8081';

// Step definitions - add INTRO as the first step
type Step = 'INTRO' | 'PROMPT' | 'MODELS' | 'PROCESSING' | 'RESULTS';

// Define the model price mapping
const prices: {[key: string]: number} = {
  'gpt4o': 0.0125,
  'gpt4turbo': 0.04,
  'gpto3mini': 0.00550,
  'gpto1': 0.075,
  'claude37': 0.018,
  'claude3opus': 0.09,
  'gemini15': 0.000375,
  'llama3': 0
};

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
  
  // Step flow state
  const [currentStep, setCurrentStep] = useState<Step>('INTRO');
  const [progress, setProgress] = useState(0);
  
  // Animation state
  const [animating, setAnimating] = useState(false);
  
  // Check for available models on component mount
  useEffect(() => {
    const fetchAvailableModels = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/available-models`);
        if (response.data && response.data.available_models) {
          setAvailableModels(response.data.available_models);
        } else {
          setError('Could not retrieve available models');
        }
      } catch (err) {
        setError('Could not connect to the backend API. Please check if the backend server is running.');
      }
    };
    
    fetchAvailableModels();
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

  // Main function to analyze the prompt
  const handleAnalyze = async () => {
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
      setProgress(30);
      
      // Make API request
      const response = await axios.post(`${API_URL}/api/analyze`, {
        prompt,
        llms: availableSelectedModels,
        ultraLLM: safeUltraModel,
        pattern: "Confidence Analysis" // Default pattern
      });
      
      setProgress(90);
      
      // Handle response
      if (response.data && response.data.ultra_response) {
        setOutput(response.data.ultra_response);
        setIsComplete(true);
        setCurrentStep('RESULTS');
      } else {
        setError('Received invalid response from server');
      }
    } catch (err: any) {
      setError(`An error occurred: ${err.message || err}`);
    } finally {
      setIsProcessing(false);
      setProgress(100);
    }
  };

  // Handle step navigation with animation
  const goToNextStep = () => {
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
    const modelNames: {[key: string]: string} = {
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
        className={`border rounded-lg p-3 cursor-pointer transition-all ${
          selectedLLMs.includes(model)
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
        return (
          <div className="space-y-6 py-8 fadeIn">
            <h2 className="text-2xl font-bold text-center text-cyan-400">Analyzing your prompt...</h2>
            <div className="max-w-md mx-auto">
              <Progress value={progress} className="h-2 bg-gray-800" indicatorClassName="bg-gradient-to-r from-cyan-500 to-cyan-400" />
            </div>
            <p className="text-center text-cyan-200">
              Multiple AI models are analyzing your prompt. The synthesizer will combine their insights.
            </p>
          </div>
        );
        
      case 'RESULTS':
        return (
          <div className="space-y-4 fadeIn">
            <div className="border-2 border-cyan-700 rounded-lg p-6 bg-black/50 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-900/20 to-purple-900/20"></div>
              <div className="relative z-10">
                <div className="flex items-center mb-4">
                  <div className="w-8 h-8 rounded-full bg-cyan-700 flex items-center justify-center mr-3 text-white font-bold">3</div>
                  <h2 className="text-2xl font-bold text-cyan-400">Analysis Results</h2>
                </div>
                
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

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white p-4 md:p-6">
      <div className="max-w-4xl mx-auto bg-black border-4 border-cyan-700 rounded-lg shadow-2xl shadow-cyan-500/20 p-6 md:p-8 relative overflow-hidden">
        {/* Background effects */}
        <div className="absolute inset-0 overflow-hidden opacity-10 pointer-events-none">
          <div className="absolute bottom-0 left-0 right-0 h-40 bg-gray-900">
            {/* Distant buildings */}
            <div className="absolute bottom-0 left-5 w-10 h-20 bg-gray-800"></div>
            <div className="absolute bottom-0 left-14 w-8 h-28 bg-gray-800"></div>
            <div className="absolute bottom-0 left-22 w-12 h-32 bg-gray-800"></div>
            <div className="absolute bottom-0 left-36 w-14 h-24 bg-gray-800"></div>
            <div className="absolute bottom-0 left-52 w-10 h-36 bg-gray-800"></div>
            
            {/* Building lights */}
            <div className="absolute bottom-10 left-8 w-1 h-1 bg-yellow-400 opacity-80 animate-pulse"></div>
            <div className="absolute bottom-15 left-16 w-1 h-1 bg-cyan-400 opacity-80 animate-pulse"></div>
            <div className="absolute bottom-20 left-24 w-1 h-1 bg-pink-400 opacity-80 animate-pulse"></div>
          </div>
        </div>
        
        {/* Step indicator */}
        {renderStepIndicator()}
        
        {/* Error display */}
        {error && (
          <div className="mb-6 bg-red-900/20 border border-red-800 rounded-lg p-4 text-red-400">
            {error}
          </div>
        )}
        
        {/* Step content */}
        {renderStepContent()}
        
        {/* Footer note */}
        <div className="mt-6 text-center text-sm text-gray-500">
          Ultra AI combines multiple AI models to provide more balanced and thorough analysis.
        </div>
      </div>
      
      {/* Add styles for animations */}
      <style dangerouslySetInnerHTML={{ __html: `
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