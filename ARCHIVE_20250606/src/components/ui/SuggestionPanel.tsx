import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Icons
import {
  LightBulbIcon,
  XMarkIcon,
  CheckIcon,
  PencilSquareIcon,
  UserGroupIcon,
  BeakerIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';

// Types for suggestions
export interface Suggestion {
  id: number;
  type:
    | 'feather_pattern'
    | 'prompt_refinement'
    | 'model_selection'
    | 'feature_discovery';
  content: string;
  title: string;
  description: string;
  confidence: 'high' | 'medium' | 'low';
  actionUrl?: string;
  dismissed?: boolean;
  metadata?: Record<string, any>;
}

interface SuggestionPanelProps {
  suggestions: Suggestion[];
  onSuggestionApply: (suggestion: Suggestion) => void;
  onSuggestionDismiss: (suggestionId: number) => void;
  className?: string;
}

const SuggestionPanel: React.FC<SuggestionPanelProps> = ({
  suggestions,
  onSuggestionApply,
  onSuggestionDismiss,
  className = '',
}) => {
  const [activeSuggestions, setActiveSuggestions] = useState<Suggestion[]>([]);

  useEffect(() => {
    // Filter out dismissed suggestions
    const filtered = suggestions.filter((s) => !s.dismissed);
    setActiveSuggestions(filtered);
  }, [suggestions]);

  if (activeSuggestions.length === 0) {
    return null; // Don't render anything if no active suggestions
  }

  // Get icon based on suggestion type
  const getSuggestionIcon = (type: string) => {
    switch (type) {
      case 'feather_pattern':
        return <SparklesIcon className="w-5 h-5" />;
      case 'prompt_refinement':
        return <PencilSquareIcon className="w-5 h-5" />;
      case 'model_selection':
        return <BeakerIcon className="w-5 h-5" />;
      case 'feature_discovery':
        return <UserGroupIcon className="w-5 h-5" />;
      default:
        return <LightBulbIcon className="w-5 h-5" />;
    }
  };

  // Get background color based on confidence level
  const getConfidenceStyles = (confidence: string): string => {
    switch (confidence) {
      case 'high':
        return 'border-green-400 bg-green-50 dark:bg-green-900/20';
      case 'medium':
        return 'border-blue-400 bg-blue-50 dark:bg-blue-900/20';
      case 'low':
        return 'border-gray-300 bg-gray-50 dark:bg-gray-800/30';
      default:
        return 'border-gray-300 bg-gray-50 dark:bg-gray-800/30';
    }
  };

  return (
    <div
      className={`suggestion-panel p-4 rounded-lg border border-gray-200 dark:border-gray-700 ${className}`}
    >
      <div className="flex items-center mb-3">
        <LightBulbIcon className="w-5 h-5 text-yellow-500 mr-2" />
        <h3 className="text-sm font-medium">Suggestions</h3>
      </div>

      <AnimatePresence>
        {activeSuggestions.map((suggestion) => (
          <motion.div
            key={suggestion.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className={`suggestion-item mb-3 p-3 rounded-md border ${getConfidenceStyles(
              suggestion.confidence
            )} relative`}
          >
            <div className="flex justify-between">
              <div className="flex items-start">
                <div className="mr-2 mt-1 text-gray-600 dark:text-gray-300">
                  {getSuggestionIcon(suggestion.type)}
                </div>
                <div>
                  <h4 className="text-sm font-medium">{suggestion.title}</h4>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                    {suggestion.description}
                  </p>
                </div>
              </div>

              <button
                onClick={() => onSuggestionDismiss(suggestion.id)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                aria-label="Dismiss suggestion"
              >
                <XMarkIcon className="w-4 h-4" />
              </button>
            </div>

            <div className="mt-2 flex justify-end">
              <button
                onClick={() => onSuggestionApply(suggestion)}
                className="inline-flex items-center px-2.5 py-1.5 text-xs font-medium rounded
                text-indigo-700 bg-indigo-100 hover:bg-indigo-200
                dark:text-indigo-300 dark:bg-indigo-900/40 dark:hover:bg-indigo-800/60
                transition-colors duration-150"
              >
                <CheckIcon className="w-3 h-3 mr-1" />
                Apply
              </button>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};

export default SuggestionPanel;
