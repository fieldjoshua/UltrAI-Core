import React, { useState } from 'react';
import { Button } from '../../ui/Button';
import { Textarea } from '../../ui/Textarea';

interface QueryStepProps {
  query: string;
  onQueryChange: (query: string) => void;
  onOptimize?: () => void;
  isOptimizing?: boolean;
}

export function QueryStep({ query, onQueryChange, onOptimize, isOptimizing }: QueryStepProps) {
  const [isFocused, setIsFocused] = useState(false);

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onQueryChange(e.target.value);
  };

  const handleOptimize = () => {
    if (onOptimize && query.trim()) {
      onOptimize();
    }
  };

  const isQueryEmpty = !query.trim();

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-white">What's your query?</h2>
        <p className="text-gray-300">
          Describe what you want to analyze or explore in detail
        </p>
      </div>

      <div className="space-y-4">
        <div className="relative">
          <Textarea
            value={query}
            onChange={handleTextareaChange}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="Enter your query here... Be as specific as possible for better results."
            className={`min-h-[120px] resize-none transition-all duration-200 ${
              isFocused ? 'border-cyan-400 ring-2 ring-cyan-400/20' : ''
            }`}
            maxLength={2000}
          />

          <div className="absolute bottom-3 right-3 text-xs text-gray-500">
            {query.length}/2000
          </div>
        </div>

        {onOptimize && (
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-400">
              {!isQueryEmpty && (
                <span className="text-green-400">✓ Query looks good</span>
              )}
            </div>

            <Button
              onClick={handleOptimize}
              disabled={isQueryEmpty || isOptimizing}
              className={`px-4 py-2 text-sm transition-all duration-200 ${
                isQueryEmpty || isOptimizing
                  ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white'
              }`}
            >
              {isOptimizing ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                  <span>Optimizing...</span>
                </div>
              ) : (
                '🚀 Optimize Query'
              )}
            </Button>
          </div>
        )}

        <div className="bg-gray-800/50 p-4 rounded-lg border border-gray-600">
          <h3 className="text-sm font-semibold text-white mb-2">Tips for better results:</h3>
          <ul className="text-sm text-gray-300 space-y-1">
            <li>• Be specific about what you want to achieve</li>
            <li>• Include relevant context and background information</li>
            <li>• Mention any specific requirements or constraints</li>
            <li>• Consider including examples of desired output format</li>
          </ul>
        </div>
      </div>
    </div>
  );
}