import React, { useState, useEffect, useRef } from 'react';
import { Textarea } from '../ui/textarea';
import { Button } from '../ui/button';
import { AlertCircle } from 'lucide-react';

export interface AnalysisOptions {
  [key: string]: any;
}

export interface PromptInputProps {
  onSubmit: (prompt: string, options: AnalysisOptions) => void;
  isLoading: boolean;
  maxLength?: number;
  placeholder?: string;
  initialValue?: string;
}

export const EnhancedPromptInput: React.FC<PromptInputProps> = ({
  onSubmit,
  isLoading,
  maxLength = 4000,
  placeholder = 'Enter your prompt here...',
  initialValue = '',
}) => {
  const [prompt, setPrompt] = useState(initialValue);
  const [charCount, setCharCount] = useState(initialValue.length);
  const [errorMessage, setErrorMessage] = useState<string | undefined>();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    // Auto-resize the textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [prompt]);

  // Handle keyboard shortcut (Ctrl/Cmd + Enter)
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      handleSubmit();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    
    // Check if exceeding maximum length
    if (value.length > maxLength) {
      return;
    }
    
    setPrompt(value);
    setCharCount(value.length);
    
    // Clear error when user starts typing
    if (errorMessage) {
      setErrorMessage(undefined);
    }
  };

  const handleSubmit = () => {
    // Validate minimum length
    if (prompt.trim().length < 10) {
      setErrorMessage('Please enter at least 10 characters');
      return;
    }

    // Clear any errors
    setErrorMessage(undefined);
    
    // Call the onSubmit prop with prompt
    onSubmit(prompt, {});
  };

  return (
    <div className="space-y-2">
      <Textarea
        ref={textareaRef}
        value={prompt}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className={`min-h-[120px] transition-all duration-200 resize-none ${
          errorMessage ? 'border-red-500 focus-visible:ring-red-500' : ''
        }`}
        disabled={isLoading}
        aria-invalid={!!errorMessage}
        aria-describedby={errorMessage ? 'prompt-error' : undefined}
      />
      
      {/* Character counter and error message */}
      <div className="flex justify-between text-sm">
        <div>
          {errorMessage && (
            <div id="prompt-error" className="flex items-center text-red-600" role="alert">
              <AlertCircle className="h-4 w-4 mr-1" />
              <span>{errorMessage}</span>
            </div>
          )}
        </div>
        <div className={`text-right ${
          charCount > maxLength * 0.9 ? 'text-amber-600' : 'text-gray-500'
        }`}>
          {charCount}/{maxLength}
        </div>
      </div>
      
      {/* Submit button */}
      <div className="flex justify-end">
        <Button
          onClick={handleSubmit}
          disabled={isLoading || !prompt.trim() || !!errorMessage}
          isLoading={isLoading}
          variant="primary"
        >
          {isLoading ? 'Analyzing...' : 'Submit'}
        </Button>
        <div className="text-xs text-gray-500 mt-1 ml-2">
          Press Ctrl+Enter to submit
        </div>
      </div>
    </div>
  );
};

export default EnhancedPromptInput;