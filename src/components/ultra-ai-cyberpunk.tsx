'use client'

import React, { useState, useEffect } from 'react'
import { Button } from "./ui/button"
import { Checkbox } from "./ui/checkbox"
import { Label } from "./ui/label"
import { Loader2, User, Zap, Shield, Lock, Cpu } from 'lucide-react'
import axios from 'axios'

const cyberpunkAnimation = `
  @keyframes neonPulse {
    0%, 100% { text-shadow: 0 0 10px #ff00de, 0 0 20px #ff00de, 0 0 30px #ff00de, 0 0 40px #ff00de; }
    50% { text-shadow: 0 0 20px #00ffff, 0 0 30px #00ffff, 0 0 40px #00ffff, 0 0 50px #00ffff; }
  }
  @keyframes backgroundShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
  @keyframes glitch {
    0% { transform: translate(0) }
    20% { transform: translate(-5px, 5px) }
    40% { transform: translate(-5px, -5px) }
    60% { transform: translate(5px, 5px) }
    80% { transform: translate(5px, -5px) }
    100% { transform: translate(0) }
  }
  @keyframes flicker {
    0%, 19.999%, 22%, 62.999%, 64%, 64.999%, 70%, 100% { opacity: 1; }
    20%, 21.999%, 63%, 63.999%, 65%, 69.999% { opacity: 0.33; }
  }
`;

const llmOptions = [
  { id: 'llama', label: 'LLaMA', price: 5, icon: Cpu },
  { id: 'gpt4', label: 'GPT-4.0', price: 10, icon: Zap },
  { id: 'gpt01', label: 'GPT-0.1', price: 8, icon: Shield },
  { id: 'claude', label: 'Claude 3.5', price: 7, icon: Lock },
  { id: 'gemini', label: 'Gemini', price: 6, icon: Cpu }
]

const steps = [
  'Initializing neural engines',
  'Analyzing prompt',
  'Generating initial responses',
  'Creating meta synthesis',
  'Performing ultra analysis',
  'Generating hyper response',
  'Packaging results'
]

const calculatePrice = (selectedLLMs: string[], ultraLLM: string | null) => {
  let total = 0;
  selectedLLMs.forEach((llm, index) => {
    const option = llmOptions.find(o => o.id === llm);
    if (option) {
      total += option.price * (index + 1);
    }
  });
  if (ultraLLM) {
    const ultraOption = llmOptions.find(o => o.id === ultraLLM);
    if (ultraOption) {
      total += ultraOption.price * 2;
    }
  }
  return total;
};

const API_URL = 'http://localhost:11434'

export default function UltrAICyberpunk() {
  const [prompt, setPrompt] = useState('')
  const [selectedLLMs, setSelectedLLMs] = useState<string[]>([])
  const [ultraLLM, setUltraLLM] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [isComplete, setIsComplete] = useState(false)
  const [output, setOutput] = useState('')
  const [calculatedPrice, setCalculatedPrice] = useState(0)
  const [userCredit, setUserCredit] = useState(100)
  const [keepDataPrivate, setKeepDataPrivate] = useState(false)
  const [useNoTraceEncryption, setUseNoTraceEncryption] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setCalculatedPrice(calculatePrice(selectedLLMs, ultraLLM));
  }, [selectedLLMs, ultraLLM]);

  const handleLLMChange = (llmId: string) => {
    setSelectedLLMs(prev => 
      prev.includes(llmId) ? prev.filter(id => id !== llmId) : [...prev, llmId]
    )
  }

  const handleUltraChange = (llmId: string) => {
    setUltraLLM(prev => prev === llmId ? null : llmId)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (selectedLLMs.length < 2 || !ultraLLM || calculatedPrice > userCredit) return;
    setIsProcessing(true)
    setIsComplete(false)
    setOutput('')

    try {
      // Show initialization
      setCurrentStep(0)
      await new Promise(resolve => setTimeout(resolve, 1000))

      // Show analyzing prompt
      setCurrentStep(1)
      await new Promise(resolve => setTimeout(resolve, 1000))

      // Send request to your Python script
      const response = await axios.post(`${API_URL}/api/analyze`, {
        prompt,
        engine: ultraLLM,
        selectedEngines: selectedLLMs,
        options: {
          keepDataPrivate,
          useNoTraceEncryption
        }
      })

      // Show initial responses
      setCurrentStep(2)
      const initialOutput = `Initial Responses:\n${Object.entries(response.data.data.initial_responses)
        .map(([model, resp]) => `\n${model.toUpperCase()}:\n${resp}`)
        .join('\n')}`
      setOutput(initialOutput)
      await new Promise(resolve => setTimeout(resolve, 1000))

      // Show meta responses
      setCurrentStep(3)
      const metaOutput = `${initialOutput}\n\nMeta Responses:\n${Object.entries(response.data.data.meta_responses)
        .map(([model, resp]) => `\n${model.toUpperCase()}:\n${resp}`)
        .join('\n')}`
      setOutput(metaOutput)
      await new Promise(resolve => setTimeout(resolve, 1000))

      // Show ultra responses
      setCurrentStep(4)
      const ultraOutput = `${metaOutput}\n\nUltra Responses:\n${Object.entries(response.data.data.ultra_responses)
        .map(([model, resp]) => `\n${model.toUpperCase()}:\n${resp}`)
        .join('\n')}`
      setOutput(ultraOutput)
      await new Promise(resolve => setTimeout(resolve, 1000))

      // Show hyper response
      setCurrentStep(5)
      const hyperOutput = `${ultraOutput}\n\nHyper Response:\n${response.data.data.hyper_response}`
      setOutput(hyperOutput)
      await new Promise(resolve => setTimeout(resolve, 1000))

      // Show final packaging
      setCurrentStep(6)
      const finalOutput = `${hyperOutput}\n\nOutput Directory: ${response.data.output_directory}`
      setOutput(finalOutput)

      setUserCredit(prevCredit => prevCredit - calculatedPrice)
      setIsComplete(true)
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during processing')
      console.error('Processing error:', err)
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-cyan-300 font-mono p-8" style={{backgroundImage: 'radial-gradient(circle, #1a0b2e 0%, #000000 100%)'}}>
      <div className="max-w-6xl mx-auto bg-black border-4 border-cyan-500 rounded-lg shadow-2xl shadow-cyan-500 p-8 relative overflow-hidden">
        <div className="absolute inset-0 bg-grid-pattern opacity-10 animate-backgroundShift"></div>
        <div className="relative z-10">
          <div className="flex justify-between items-center mb-12">
            <h1 className="text-8xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-pink-500 via-cyan-500 to-green-500 animate-neonPulse">
              UltrAI
            </h1>
            <User className="w-12 h-12 text-cyan-500 animate-pulse" />
          </div>
          
          <div className="grid grid-cols-3 gap-8">
            <div className="col-span-2 space-y-8">
              <form onSubmit={handleSubmit} className="space-y-8">
                <div className="space-y-4">
                  <Label className="text-2xl font-bold text-green-400">Select LLMs: <span className="text-sm font-normal text-pink-400">(choose at least two)<sup>1</sup></span></Label>
                  <div className="grid grid-cols-2 gap-4">
                    {llmOptions.map((llm) => (
                      <div key={llm.id} className="flex items-center space-x-4 bg-cyan-900 bg-opacity-30 p-4 rounded-lg border border-cyan-500 hover:bg-opacity-50 transition-all duration-300">
                        <Checkbox 
                          id={`llm-${llm.id}`} 
                          checked={selectedLLMs.includes(llm.id)}
                          onCheckedChange={() => handleLLMChange(llm.id)}
                          className="border-pink-500"
                        />
                        <Label htmlFor={`llm-${llm.id}`} className="flex items-center space-x-2 text-cyan-300">
                          <llm.icon className="w-6 h-6 text-green-400" />
                          <span>{llm.label}</span>
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-4">
                  <Label className="text-2xl font-bold text-green-400">WHO IS ULTRA? <span className="text-sm font-normal text-pink-400">(select only one)<sup>2</sup></span></Label>
                  <div className="grid grid-cols-2 gap-4">
                    {llmOptions.map((llm) => (
                      <div key={`ultra-${llm.id}`} className="flex items-center space-x-4 bg-pink-900 bg-opacity-30 p-4 rounded-lg border border-pink-500 hover:bg-opacity-50 transition-all duration-300">
                        <Checkbox 
                          id={`ultra-${llm.id}`} 
                          checked={ultraLLM === llm.id}
                          onCheckedChange={() => handleUltraChange(llm.id)}
                          className="border-cyan-500"
                        />
                        <Label htmlFor={`ultra-${llm.id}`} className="flex items-center space-x-2 text-cyan-300">
                          <llm.icon className="w-6 h-6 text-cyan-400" />
                          <span>{llm.label}</span>
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center space-x-4 bg-green-900 bg-opacity-30 p-4 rounded-lg border border-green-500 hover:bg-opacity-50 transition-all duration-300">
                    <Checkbox 
                      id="keep-data-private"
                      checked={keepDataPrivate}
                      onCheckedChange={() => setKeepDataPrivate(!keepDataPrivate)}
                      className="border-cyan-500"
                    />
                    <Label htmlFor="keep-data-private" className="flex items-center space-x-2 text-cyan-300">
                      <Shield className="w-6 h-6 text-green-400" />
                      <span>Keep my data private<sup>3</sup></span>
                    </Label>
                  </div>
                  <div className="flex items-center space-x-4 bg-green-900 bg-opacity-30 p-4 rounded-lg border border-green-500 hover:bg-opacity-50 transition-all duration-300">
                    <Checkbox 
                      id="no-trace-encryption"
                      checked={useNoTraceEncryption}
                      onCheckedChange={() => setUseNoTraceEncryption(!useNoTraceEncryption)}
                      className="border-cyan-500"
                    />
                    <Label htmlFor="no-trace-encryption" className="flex items-center space-x-2 text-cyan-300">
                      <Lock className="w-6 h-6 text-green-400" />
                      <span>Private and NoTrace Encryption<sup>4</sup></span>
                    </Label>
                  </div>
                </div>

                <div className="space-y-4">
                  <Label htmlFor="prompt" className="text-2xl font-bold text-green-400">Enter your prompt:<sup>5</sup></Label>
                  <textarea
                    id="prompt"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Enter your cyberpunk prompt here..."
                    className="w-full h-40 p-4 bg-gray-800 border-2 border-cyan-500 rounded-lg text-cyan-300 placeholder-cyan-600 focus:ring-4 focus:ring-green-500 focus:border-transparent transition-all duration-300"
                    disabled={isProcessing}
                  />
                </div>

                <div className="flex justify-between items-center">
                  <div className="text-3xl font-bold text-green-400 animate-pulse">
                    Estimated Price: <span className="text-pink-500">${calculatedPrice.toFixed(2)}</span><sup>6</sup>
                  </div>
                  <Button 
                    type="submit" 
                    disabled={isProcessing || !prompt || selectedLLMs.length < 2 || !ultraLLM || calculatedPrice > userCredit}
                    className="px-8 py-4 bg-gradient-to-r from-cyan-500 via-pink-500 to-green-500 text-black font-bold text-xl rounded-full hover:from-green-500 hover:via-cyan-500 hover:to-pink-500 transition-all duration-300 animate-pulse disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isProcessing ? <Loader2 className="mr-2 h-6 w-6 animate-spin" /> : 'PROCESS'}
                  </Button>
                </div>
              </form>

              {/* Update the processing steps display */}
              <div className="mt-8 space-y-4 border-2 border-cyan-500 p-4 rounded-lg bg-black bg-opacity-50">
                <h3 className="text-xl font-bold text-green-400 mb-4">Neural Processing Status:</h3>
                {steps.map((step, index) => (
                  <div key={step} className="flex items-center space-x-4">
                    <div 
                      className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 ${
                        index < currentStep 
                          ? 'bg-green-500' 
                          : index === currentStep 
                            ? 'bg-pink-500 animate-pulse' 
                            : 'bg-cyan-900'
                      }`}
                    >
                      {index < currentStep && (
                        <span className="text-black">✓</span>
                      )}
                    </div>
                    <span 
                      className={`text-xl transition-all duration-300 ${
                        index < currentStep 
                          ? 'text-green-400' 
                          : index === currentStep 
                            ? 'text-pink-400 animate-pulse' 
                            : 'text-cyan-600'
                      }`}
                    >
                      {step}
                    </span>
                  </div>
                ))}
              </div>

              {/* Then show the output below */}
              {output && (
                <div className="mt-8 space-y-4">
                  <div className="p-6 bg-cyan-900 bg-opacity-30 rounded-lg border-2 border-cyan-500 animate-glitch">
                    <pre className="whitespace-pre-wrap text-green-400">{output}</pre>
                  </div>
                  {isComplete && (
                    <Button 
                      onClick={() => console.log('Downloading zip file with content:', output)} 
                      className="w-full px-8 py-4 bg-gradient-to-r from-green-500 via-cyan-500 to-pink-500 text-black font-bold text-xl rounded-full hover:from-pink-500 hover:via-green-500 hover:to-cyan-500 transition-all duration-300 animate-pulse"
                    >
                      DOWNLOAD ZIP
                    </Button>
                  )}
                </div>
              )}
            </div>

            <div className="space-y-8">
              <div className="p-6 bg-green-900 bg-opacity-30 rounded-lg border-2 border-green-500 animate-flicker">
                <h2 className="text-3xl font-bold text-green-400 mb-4">Credit Balance</h2>
                <div className="text-5xl font-bold text-pink-500">${userCredit.toFixed(2)}</div>
                <Button 
                  variant="outline" className="mt-4 w-full px-6 py-3 bg-black border-2 border-green-500 text-green-400 font-bold text-xl rounded-full hover:bg-green-900 hover:text-cyan-300 transition-all duration-300"
                >
                  ADD MORE CREDITS
                </Button>
              </div>

              <div className="p-6 bg-pink-900 bg-opacity-30 rounded-lg border-2 border-pink-500">
                <h2 className="text-3xl font-bold text-pink-400 mb-4">UltrAI Stats</h2>
                <ul className="space-y-2 text-cyan-300">
                  <li>Processed Prompts: 1,337</li>
                  <li>Ultra Boosts: 42</li>
                  <li>Encryption Level: MAXIMUM</li>
                  <li>Neural Links: 7,777</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 text-sm text-cyan-400 space-y-2 animate-pulse">
        <p><sup>1</sup> The price skyrockets with every neural engine you choose, based on black market rates.</p>
        <p><sup>2</sup> Selecting an ULTRA LLM doubles its contribution to the total price and unlocks hidden potentials.</p>
        <p><sup>3</sup> Data NOT used for training purposes, cost based on dark web pricing.</p>
        <p><sup>4</sup> It never happened. We were never here.</p>
        <p><sup>5</sup> The longer and more complex the prompt, the higher the neural load and price.</p>
        <p><sup>6</sup> UltrAI guaranteed lowest price in the multiverse or your credits back.</p>
      </div>
      <style jsx>{`
        ${cyberpunkAnimation}
        .animate-neonPulse {
          animation: neonPulse 2s infinite;
        }
        .animate-backgroundShift {
          animation: backgroundShift 10s ease infinite;
        }
        .animate-glitch {
          animation: glitch 0.5s infinite;
        }
        .animate-flicker {
          animation: flicker 2s infinite;
        }
        .bg-grid-pattern {
          background-image: linear-gradient(to right, #1a0b2e 1px, transparent 1px),
                            linear-gradient(to bottom, #1a0b2e 1px, transparent 1px);
          background-size: 20px 20px;
        }
      `}</style>
    </div>
  )
}