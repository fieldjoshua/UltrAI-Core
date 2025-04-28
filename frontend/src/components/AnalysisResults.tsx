import React, { useRef } from 'react';
import { Card } from './ui/card';
import { useKeyboardNavigation } from '../hooks/useKeyboardNavigation';
import { screenReader } from '../utils/accessibility';
import { focusManagement } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';

interface AnalysisResult {
  id: string;
  model: string;
  content: string;
  confidence: number;
  timestamp: string;
}

interface AnalysisResultsProps {
  results: AnalysisResult[];
  isLoading?: boolean;
  onResultSelect?: (result: AnalysisResult) => void;
}

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({
  results,
  isLoading = false,
  onResultSelect,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [focusedIndex, setFocusedIndex] = React.useState<number>(-1);

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setFocusedIndex(Math.min(index + 1, results.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setFocusedIndex(Math.max(index - 1, 0));
        break;
      case 'Enter':
        e.preventDefault();
        onResultSelect?.(results[index]);
        break;
    }
  };

  useKeyboardNavigation({
    onArrowDown: () => {
      if (focusedIndex < results.length - 1) {
        setFocusedIndex(focusedIndex + 1);
      }
    },
    onArrowUp: () => {
      if (focusedIndex > 0) {
        setFocusedIndex(focusedIndex - 1);
      }
    },
    onHome: () => {
      setFocusedIndex(0);
    },
    onEnd: () => {
      setFocusedIndex(results.length - 1);
    },
  });

  React.useEffect(() => {
    if (focusedIndex >= 0 && containerRef.current) {
      const focusableElements =
        containerRef.current.querySelectorAll('[role="article"]');
      const element = focusableElements[focusedIndex] as HTMLElement;
      if (element) {
        element.focus();
        screenReader.announce(
          `Result ${focusedIndex + 1} of ${results.length}`
        );
      }
    }
  }, [focusedIndex, results.length]);

  if (isLoading) {
    return (
      <Card className="w-full p-4">
        <div role="status" aria-label="Loading analysis results">
          <p className="text-center text-gray-500">Loading results...</p>
        </div>
      </Card>
    );
  }

  if (results.length === 0) {
    return (
      <Card className="w-full p-4">
        <div role="status" aria-label="No analysis results">
          <p className="text-center text-gray-500">No results available</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="w-full p-4">
      <div
        ref={containerRef}
        role="region"
        aria-label="Analysis Results"
        className="space-y-4"
      >
        <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>
        <div
          role="list"
          aria-label="List of analysis results"
          className="space-y-4"
        >
          {results.map((result, index) => (
            <div
              key={result.id}
              role="article"
              tabIndex={0}
              onKeyDown={e => handleKeyDown(e, index)}
              onClick={() => onResultSelect?.(result)}
              className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                focusedIndex === index
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-blue-300'
              }`}
              aria-label={`Analysis result from ${result.model}`}
              aria-describedby={`${result.id}-content`}
            >
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-medium" id={`${result.id}-title`}>
                  {result.model}
                </h3>
                <span
                  className="text-sm text-gray-500"
                  aria-label={`Confidence: ${result.confidence}%`}
                >
                  {result.confidence}% confidence
                </span>
              </div>
              <p id={`${result.id}-content`} className="text-gray-700">
                {result.content}
              </p>
              <time
                dateTime={result.timestamp}
                className="text-sm text-gray-500 mt-2 block"
              >
                {new Date(result.timestamp).toLocaleString()}
              </time>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
};
