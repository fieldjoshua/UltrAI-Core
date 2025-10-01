import React, { useState } from 'react';

interface QueryStepProps {
  onNext: (query: string) => void;
  onBack?: () => void;
}

export function QueryStep({ onNext, onBack }: QueryStepProps) {
  const [query, setQuery] = useState('');

  const handleNext = () => {
    if (query.trim()) {
      onNext(query.trim());
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.ctrlKey && query.trim()) {
      handleNext();
    }
  };

  return (
    <div className="query-step">
      <div className="query-content">
        <h2 className="query-title">What's your specific request?</h2>
        <p className="query-description">
          Describe what you need help with in detail. Be as specific as possible
          to get the best results.
        </p>

        <div className="query-input-container">
          <textarea
            className="query-textarea"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your request here... (Ctrl+Enter to continue)"
            rows={8}
            autoFocus
          />
          <div className="query-char-count">
            {query.length} characters
          </div>
        </div>

        <div className="query-actions">
          {onBack && (
            <button className="query-back-button" onClick={onBack}>
              Back
            </button>
          )}
          <button
            className="query-next-button"
            onClick={handleNext}
            disabled={!query.trim()}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}