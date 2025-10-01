import React, { useState } from 'react';
import { Button } from '../../Button';
import { Textarea } from '../../Textarea';

interface QueryStepProps {
  query: string;
  onQueryChange: (query: string) => void;
  onNext: () => void;
  onBack: () => void;
}

export function QueryStep({ query, onQueryChange, onNext, onBack }: QueryStepProps) {
  const [isFocused, setIsFocused] = useState(false);

  const handleQueryChange = (value: string) => {
    onQueryChange(value);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault();
      if (query.trim()) {
        onNext();
      }
    }
  };

  const characterCount = query.length;
  const maxLength = 2000;
  const isValid = query.trim().length >= 10;

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-cyber-green mb-2">
          What would you like to analyze?
        </h2>
        <p className="text-gray-300">
          Describe your query, request, or the content you want to work with
        </p>
      </div>

      <div className="space-y-4">
        <div className="relative">
          <Textarea
            value={query}
            onChange={(e) => handleQueryChange(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            onKeyDown={handleKeyDown}
            placeholder="Enter your query here...&#10;&#10;Examples:&#10;• Analyze this document for key insights&#10;• Summarize the main points of this article&#10;• Compare these two approaches&#10;• Generate ideas for improving this process&#10;• Extract all the technical specifications"
            className={`min-h-[200px] text-base resize-none transition-all duration-200 ${
              isFocused
                ? 'border-cyber-green bg-cyber-green/5'
                : 'border-gray-600 hover:border-gray-400'
            }`}
            maxLength={maxLength}
          />
        </div>

        <div className="flex justify-between items-center text-sm">
          <div className={`${
            characterCount > maxLength * 0.8 ? 'text-yellow-400' :
            characterCount > maxLength * 0.9 ? 'text-red-400' : 'text-gray-400'
          }`}>
            {characterCount}/{maxLength} characters
          </div>
          <div className={`${
            !isValid ? 'text-red-400' : 'text-green-400'
          }`}>
            {!isValid ? 'Minimum 10 characters required' : '✓ Valid query'}
          </div>
        </div>
      </div>

      <div className="bg-cyber-green/10 border border-cyber-green/30 rounded-lg p-4">
        <h3 className="font-semibold text-cyber-green mb-2">Tips for better results:</h3>
        <ul className="text-sm text-gray-300 space-y-1">
          <li>• Be specific about what you want to achieve</li>
          <li>• Include relevant context or background information</li>
          <li>• Mention any specific formats or structures you prefer</li>
          <li>• If comparing items, clearly identify what to compare</li>
        </ul>
      </div>

      <div className="flex justify-between pt-6">
        <Button
          onClick={onBack}
          variant="outline"
          className="border-gray-400 text-gray-400 hover:bg-gray-400/10"
        >
          Back
        </Button>
        <Button
          onClick={onNext}
          disabled={!isValid}
          className="bg-cyber-green hover:bg-cyber-green/80 text-black disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Continue
        </Button>
      </div>

      <div className="text-center text-xs text-gray-500">
        Press Ctrl+Enter to continue
      </div>
    </div>
  );
}