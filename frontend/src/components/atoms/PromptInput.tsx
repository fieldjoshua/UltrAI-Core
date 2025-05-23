/**
 * PromptInput Component
 *
 * A reusable component for entering and submitting prompts to the Ultra analysis system.
 * This component provides a textarea for prompt input and a submit button for sending
 * the prompt for analysis.
 */

import React, { useState } from 'react';
import { Textarea } from '../ui/textarea';
import { Button } from '../ui/button';

export interface PromptInputProps {
  /**
   * Callback function called when the prompt is submitted
   * @param prompt The submitted prompt text
   */
  onSubmit: (prompt: string) => void;

  /**
   * Whether the input is currently disabled
   * @default false
   */
  disabled?: boolean;

  /**
   * Placeholder text for the textarea
   * @default "Enter your prompt here..."
   */
  placeholder?: string;

  /**
   * Minimum number of rows for the textarea
   * @default 4
   */
  minRows?: number;

  /**
   * Maximum number of rows for the textarea
   * @default 10
   */
  maxRows?: number;

  /**
   * Whether to show a loading state
   * @default false
   */
  isLoading?: boolean;
}

export const PromptInput: React.FC<PromptInputProps> = ({
  onSubmit,
  disabled = false,
  placeholder = 'Enter your prompt here...',
  minRows = 4,
  maxRows = 10,
  isLoading = false,
}) => {
  const [prompt, setPrompt] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim()) {
      onSubmit(prompt.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-4">
      <Textarea
        value={prompt}
        onChange={e => setPrompt(e.target.value)}
        placeholder={placeholder}
        disabled={disabled || isLoading}
        rows={minRows}
        maxLength={2000}
        className="resize-y"
        aria-label="Prompt input"
      />
      <div className="flex justify-end">
        <Button
          type="submit"
          disabled={!prompt.trim() || disabled || isLoading}
          className="min-w-[100px]"
        >
          {isLoading ? 'Submitting...' : 'Submit'}
        </Button>
      </div>
    </form>
  );
};
