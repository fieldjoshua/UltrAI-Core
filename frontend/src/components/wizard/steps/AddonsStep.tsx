import React from 'react';
import { Checkbox } from '../../ui/Checkbox';

export interface Addon {
  id: string;
  name: string;
  description: string;
  category: 'enhancement' | 'output' | 'integration' | 'analysis';
  cost: number;
  popular?: boolean;
}

export const AVAILABLE_ADDONS: Addon[] = [
  // Enhancement Addons
  {
    id: 'web-search',
    name: 'Web Search Integration',
    description: 'Search the web for latest information and current events',
    category: 'enhancement',
    cost: 5,
    popular: true,
  },
  {
    id: 'document-analysis',
    name: 'Document Analysis',
    description: 'Upload and analyze documents, PDFs, and files',
    category: 'enhancement',
    cost: 8,
    popular: true,
  },
  {
    id: 'image-analysis',
    name: 'Image Analysis',
    description: 'Analyze images, charts, and visual content',
    category: 'enhancement',
    cost: 6,
  },
  {
    id: 'code-analysis',
    name: 'Code Analysis',
    description: 'Analyze code repositories and programming patterns',
    category: 'enhancement',
    cost: 7,
  },

  // Output Addons
  {
    id: 'structured-output',
    name: 'Structured Output',
    description: 'Generate structured data formats (JSON, CSV, XML)',
    category: 'output',
    cost: 3,
  },
  {
    id: 'visualization',
    name: 'Data Visualization',
    description: 'Create charts, graphs, and visual representations',
    category: 'output',
    cost: 4,
  },
  {
    id: 'report-generation',
    name: 'Professional Reports',
    description: 'Generate formatted reports with executive summaries',
    category: 'output',
    cost: 6,
    popular: true,
  },
  {
    id: 'presentation-mode',
    name: 'Presentation Mode',
    description: 'Create slide decks and presentation materials',
    category: 'output',
    cost: 5,
  },

  // Integration Addons
  {
    id: 'api-integration',
    name: 'API Integration',
    description: 'Connect with external APIs and services',
    category: 'integration',
    cost: 8,
  },
  {
    id: 'database-query',
    name: 'Database Queries',
    description: 'Query databases and generate insights from data',
    category: 'integration',
    cost: 7,
  },
  {
    id: 'collaboration',
    name: 'Team Collaboration',
    description: 'Share results and collaborate with team members',
    category: 'integration',
    cost: 4,
  },

  // Analysis Addons
  {
    id: 'sentiment-analysis',
    name: 'Sentiment Analysis',
    description: 'Analyze sentiment and emotional tone in content',
    category: 'analysis',
    cost: 3,
  },
  {
    id: 'trend-detection',
    name: 'Trend Detection',
    description: 'Identify trends and patterns in data over time',
    category: 'analysis',
    cost: 5,
  },
  {
    id: 'risk-assessment',
    name: 'Risk Assessment',
    description: 'Evaluate risks and provide mitigation strategies',
    category: 'analysis',
    cost: 6,
  },
  {
    id: 'comparative-analysis',
    name: 'Comparative Analysis',
    description: 'Compare multiple options, scenarios, or alternatives',
    category: 'analysis',
    cost: 4,
  },
];

interface AddonsStepProps {
  selectedAddons: string[];
  onAddonToggle: (addonId: string) => void;
}

export function AddonsStep({ selectedAddons, onAddonToggle }: AddonsStepProps) {
  const categories = ['enhancement', 'output', 'integration', 'analysis'] as const;

  const getCategoryTitle = (category: string) => {
    return category.charAt(0).toUpperCase() + category.slice(1);
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      enhancement: 'text-green-400',
      output: 'text-blue-400',
      integration: 'text-purple-400',
      analysis: 'text-orange-400',
    };
    return colors[category as keyof typeof colors] || 'text-gray-400';
  };

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-white">Choose Your Add-ons</h2>
        <p className="text-gray-300">
          Enhance your analysis with powerful additional capabilities
        </p>
      </div>

      <div className="space-y-8">
        {categories.map(category => {
          const categoryAddons = AVAILABLE_ADDONS.filter(addon => addon.category === category);
          if (categoryAddons.length === 0) return null;

          return (
            <div key={category} className="space-y-4">
              <h3 className={`text-lg font-semibold ${getCategoryColor(category)}`}>
                {getCategoryTitle(category)} Add-ons
              </h3>
              <div className="grid gap-4 md:grid-cols-2">
                {categoryAddons.map(addon => (
                  <div
                    key={addon.id}
                    className={`p-4 rounded-lg border transition-all cursor-pointer ${
                      selectedAddons.includes(addon.id)
                        ? 'border-cyan-400 bg-cyan-400/10'
                        : 'border-gray-600 bg-gray-800/50 hover:border-gray-500'
                    }`}
                    onClick={() => onAddonToggle(addon.id)}
                  >
                    <div className="flex items-start space-x-3">
                      <Checkbox
                        checked={selectedAddons.includes(addon.id)}
                        onChange={() => onAddonToggle(addon.id)}
                        className="mt-1"
                      />
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <label className="text-white font-medium cursor-pointer">
                            {addon.name}
                          </label>
                          {addon.popular && (
                            <span className="px-2 py-1 text-xs bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full">
                              Popular
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-400 mt-1">
                          {addon.description}
                        </p>
                        <div className="flex items-center justify-between mt-2">
                          <span className="text-xs text-cyan-400">
                            +${addon.cost} cost
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {selectedAddons.length > 0 && (
        <div className="bg-gray-800/50 p-4 rounded-lg border border-gray-600">
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-300">
              Selected {selectedAddons.length} add-on{selectedAddons.length !== 1 ? 's' : ''}
            </p>
            <p className="text-sm text-cyan-400">
              Total: +${AVAILABLE_ADDONS
                .filter(addon => selectedAddons.includes(addon.id))
                .reduce((sum, addon) => sum + addon.cost, 0)} cost
            </p>
          </div>
        </div>
      )}

      <div className="bg-yellow-900/20 p-4 rounded-lg border border-yellow-400/30">
        <h4 className="text-sm font-semibold text-yellow-400 mb-2">💡 Add-on Tips</h4>
        <ul className="text-sm text-gray-300 space-y-1">
          <li>• <strong>Popular add-ons</strong> are frequently used and well-tested</li>
          <li>• <strong>Web Search</strong> keeps your analysis current with latest information</li>
          <li>• <strong>Document Analysis</strong> lets you work with your existing files</li>
          <li>• <strong>Professional Reports</strong> help you present findings effectively</li>
        </ul>
      </div>
    </div>
  );
}