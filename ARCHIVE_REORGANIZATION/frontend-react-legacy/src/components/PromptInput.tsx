import React, { useState, useRef } from 'react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Card } from './ui/card';
import { useKeyboardNavigation } from '../hooks/useKeyboardNavigation';
import { screenReader } from '../utils/accessibility';
import { ARIA_ROLES, ARIA_STATES } from '../utils/accessibility';

interface PromptInputProps {
  onSubmit: (prompt: string) => void;
  isLoading?: boolean;
}

export const PromptInput: React.FC<PromptInputProps> = ({
  onSubmit,
  isLoading = false,
}) => {
  const [prompt, setPrompt] = useState('');
  const [error, setError] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim()) {
      onSubmit(prompt.trim());
      screenReader.announce('Prompt submitted for analysis');
    } else {
      setError('Please enter a prompt');
      screenReader.announce('Error: Please enter a prompt', 'assertive');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  useKeyboardNavigation({
    onEscape: () => {
      setPrompt('');
      setError(null);
      screenReader.announce('Prompt cleared');
    },
  });

  return (
    <Card className="w-full p-4">
      <form
        onSubmit={handleSubmit}
        className="space-y-4"
        role="form"
        aria-label="Prompt submission form"
      >
        <div>
          <label
            htmlFor="prompt-input"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Enter your prompt
          </label>
          <Textarea
            id="prompt-input"
            ref={textareaRef}
            value={prompt}
            onChange={e => {
              setPrompt(e.target.value);
              setError(null);
            }}
            onKeyDown={handleKeyDown}
            placeholder="Enter your prompt here..."
            className="min-h-[100px] resize-none"
            disabled={isLoading}
            aria-invalid={!!error}
            aria-describedby={error ? 'prompt-error' : undefined}
            role="textbox"
          />
          {error && (
            <div
              id="prompt-error"
              role="alert"
              className="mt-2 text-sm text-red-600"
            >
              {error}
            </div>
          )}
        </div>
        <Button
          type="submit"
          disabled={isLoading || !prompt.trim()}
          className="w-full"
          aria-label={
            isLoading ? 'Analyzing prompt...' : 'Submit prompt for analysis'
          }
        >
          {isLoading ? 'Analyzing...' : 'Analyze Prompt'}
        </Button>
      </form>
    </Card>
  );
};
