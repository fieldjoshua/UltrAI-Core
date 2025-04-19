import React from 'react';
import { Button } from '../ui/button'; // Adjust path
import { Textarea } from '../ui/textarea'; // Adjust path
import { Label } from '../ui/label'; // Adjust path

interface PromptStepProps {
    prompt: string;
    setPrompt: (value: string) => void;
    isProcessing: boolean;
    isOffline: boolean;
    error?: string | null;
    goToNextStep: () => void;
    goToPreviousStep: () => void;
}

const PromptStep: React.FC<PromptStepProps> = ({
    prompt,
    setPrompt,
    isProcessing,
    isOffline,
    error,
    goToNextStep,
    goToPreviousStep,
}) => {
    return (
        <div className="space-y-6 fadeIn">
            <div className="border-2 border-cyan-700 rounded-lg p-6 bg-black/50 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-900/20 to-purple-900/20"></div>
                <div className="relative z-10">
                    <div className="flex items-center mb-4">
                        <div className="w-8 h-8 rounded-full bg-cyan-700 flex items-center justify-center mr-3 text-white font-bold">
                            1
                        </div>
                        <h2 className="text-2xl font-bold text-cyan-400">
                            What would you like Ultra to analyze?
                        </h2>
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="prompt-input" className="text-lg text-cyan-200">
                            Enter your prompt or question
                        </Label>
                        <div className="relative">
                            <Textarea
                                id="prompt-input"
                                placeholder="Describe what you want multiple AI models to analyze..."
                                className="w-full min-h-[200px] text-lg p-4 leading-relaxed bg-gray-900 border-gray-700 text-cyan-50"
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                disabled={isProcessing || isOffline}
                                aria-label="Prompt Input"
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
                </div>
            </div>

            {error && (
                <div className="bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-300 p-3 rounded-md mb-4">
                    {error}
                </div>
            )}

            {/* Navigation Buttons moved to parent component */}
        </div>
    );
};

export default PromptStep;