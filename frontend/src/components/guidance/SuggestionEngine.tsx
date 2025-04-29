import React, { useState, useEffect } from 'react';
import { Lightbulb, ArrowRight, X } from 'lucide-react';
import { Button } from '../ui/button';
import { Card } from '../ui/card';
import { Badge } from '../ui/badge';

interface Suggestion {
  id: string;
  type: 'feather' | 'prompt' | 'model' | 'feature';
  title: string;
  description: string;
  actionText?: string;
  actionCallback?: () => void;
  tags?: string[];
  priority: number; // 1-10, higher is more important
}

interface SuggestionEngineProps {
  currentStep: string;
  prompt: string;
  selectedModels: string[];
  selectedAnalysisType: string;
  documents: any[]; // Replace with proper document type
  onSuggestionApply: (suggestion: Suggestion) => void;
}

export const SuggestionEngine: React.FC<SuggestionEngineProps> = ({
  currentStep,
  prompt,
  selectedModels,
  selectedAnalysisType,
  documents,
  onSuggestionApply,
}) => {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [dismissed, setDismissed] = useState<string[]>([]);
  const [isVisible, setIsVisible] = useState(true);

  // Filter suggestions by current step context and what hasn't been dismissed
  const filteredSuggestions = suggestions
    .filter(suggestion => !dismissed.includes(suggestion.id))
    .sort((a, b) => b.priority - a.priority);

  // Generate suggestions based on current state
  useEffect(() => {
    const newSuggestions: Suggestion[] = [];

    // Context-specific suggestions
    if (currentStep === 'PROMPT') {
      // Prompt length guidance
      if (prompt.length < 20 && prompt.length > 0) {
        newSuggestions.push({
          id: 'longer-prompt',
          type: 'prompt',
          title: 'Make Your Prompt More Detailed',
          description:
            'More detailed prompts typically yield better and more specific results.',
          tags: ['best-practice'],
          priority: 8,
        });
      }

      // Prompt strategy suggestions
      if (!prompt.includes('?') && prompt.length > 20) {
        newSuggestions.push({
          id: 'frame-as-question',
          type: 'prompt',
          title: 'Frame as a Question',
          description:
            'Consider phrasing your prompt as a specific question for more focused responses.',
          tags: ['strategy'],
          priority: 7,
        });
      }
    }

    if (currentStep === 'MODELS') {
      // Model selection guidance
      if (selectedModels.length < 2) {
        newSuggestions.push({
          id: 'multiple-models',
          type: 'model',
          title: 'Select Multiple Models',
          description:
            'Ultra works best when comparing responses from different models. Try selecting at least 2-3 models for better results.',
          tags: ['recommended'],
          priority: 9,
        });
      }

      // Model diversity suggestion
      const hasGPT = selectedModels.some(m => m.includes('gpt'));
      const hasClaude = selectedModels.some(m => m.includes('claude'));

      if (
        selectedModels.length >= 2 &&
        (!hasGPT || !hasClaude) &&
        selectedModels.length < 4
      ) {
        newSuggestions.push({
          id: 'diverse-models',
          type: 'model',
          title: 'Add Model Diversity',
          description:
            'Try including models from different providers (GPT, Claude, etc.) for more diverse perspectives.',
          tags: ['diversity'],
          priority: 6,
        });
      }
    }

    if (currentStep === 'ANALYSIS_TYPE') {
      // Analysis type recommendations based on prompt
      const lowercasePrompt = prompt.toLowerCase();

      if (
        (lowercasePrompt.includes('compare') ||
          lowercasePrompt.includes('different') ||
          lowercasePrompt.includes('perspectives')) &&
        selectedAnalysisType !== 'perspective'
      ) {
        newSuggestions.push({
          id: 'suggest-perspective',
          type: 'feather',
          title: 'Try "Perspective" Analysis',
          description:
            'Your prompt seems to be asking for different viewpoints. The Perspective analysis pattern could work well for this query.',
          actionText: 'Use Perspective',
          tags: ['context-aware'],
          priority: 8,
        });
      }

      if (
        (lowercasePrompt.includes('fact') ||
          lowercasePrompt.includes('truth') ||
          lowercasePrompt.includes('verify') ||
          lowercasePrompt.includes('accurate')) &&
        selectedAnalysisType !== 'fact_check'
      ) {
        newSuggestions.push({
          id: 'suggest-factcheck',
          type: 'feather',
          title: 'Try "Fact Check" Analysis',
          description:
            'Your prompt seems to be asking for factual verification. The Fact Check analysis pattern could work well for this query.',
          actionText: 'Use Fact Check',
          tags: ['context-aware'],
          priority: 8,
        });
      }
    }

    if (
      currentStep === 'DOCUMENTS' &&
      documents.length === 0 &&
      prompt.length > 50
    ) {
      // Document upload suggestion
      newSuggestions.push({
        id: 'add-documents',
        type: 'feature',
        title: 'Add Supporting Documents',
        description:
          'Your detailed prompt might benefit from additional context. Consider uploading relevant documents.',
        tags: ['enhancement'],
        priority: 7,
      });
    }

    // Feature discovery - randomly show a feature tip if we don't have other high-priority suggestions
    if (newSuggestions.length === 0 && Math.random() > 0.7) {
      const featureTips = [
        {
          id: 'feature-history',
          type: 'feature',
          title: 'Access Your History',
          description:
            'You can access and reuse your past analyses from the History panel.',
          tags: ['tip'],
          priority: 4,
        },
        {
          id: 'feature-export',
          type: 'feature',
          title: 'Export Your Results',
          description:
            'Did you know you can export analysis results in various formats?',
          tags: ['tip'],
          priority: 4,
        },
        {
          id: 'feature-share',
          type: 'feature',
          title: 'Share Analysis Results',
          description:
            'You can share your analysis results with others using the Share button.',
          tags: ['tip'],
          priority: 4,
        },
      ];

      // Add a random feature tip
      newSuggestions.push(
        featureTips[Math.floor(Math.random() * featureTips.length)]
      );
    }

    setSuggestions(newSuggestions);
  }, [currentStep, prompt, selectedModels, selectedAnalysisType, documents]);

  if (!isVisible || filteredSuggestions.length === 0) {
    return (
      <div className="fixed bottom-4 right-4">
        <Button
          variant="outline"
          size="sm"
          className="rounded-full"
          onClick={() => setIsVisible(true)}
        >
          <Lightbulb className="h-4 w-4 text-yellow-500" />
        </Button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 w-80 z-50">
      <Card className="p-4 shadow-lg border-l-4 border-l-yellow-500">
        <div className="flex justify-between items-start mb-2">
          <div className="flex items-center">
            <Lightbulb className="h-5 w-5 text-yellow-500 mr-2" />
            <h3 className="font-medium">Suggestions</h3>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 p-0"
            onClick={() => setIsVisible(false)}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="space-y-3 max-h-60 overflow-y-auto">
          {filteredSuggestions.map(suggestion => (
            <div
              key={suggestion.id}
              className="p-2 border rounded bg-white/50 hover:bg-white transition-colors"
            >
              <div className="flex justify-between items-start">
                <h4 className="font-semibold text-sm">{suggestion.title}</h4>
                {suggestion.tags && suggestion.tags.length > 0 && (
                  <Badge variant="outline" className="text-xs">
                    {suggestion.tags[0]}
                  </Badge>
                )}
              </div>
              <p className="text-xs text-gray-600 mt-1 mb-2">
                {suggestion.description}
              </p>
              <div className="flex justify-between items-center">
                {suggestion.actionText && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-xs"
                    onClick={() => onSuggestionApply(suggestion)}
                  >
                    {suggestion.actionText}
                    <ArrowRight className="h-3 w-3 ml-1" />
                  </Button>
                )}
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-xs ml-auto"
                  onClick={() => setDismissed([...dismissed, suggestion.id])}
                >
                  Dismiss
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

export default SuggestionEngine;
