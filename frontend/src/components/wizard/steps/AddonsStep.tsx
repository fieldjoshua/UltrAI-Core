import React from 'react';
import { Button } from '../../Button';
import { Checkbox } from '../../Checkbox';

interface Addon {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: 'enhancement' | 'format' | 'integration';
  cost: 'free' | 'premium';
}

interface AddonsStepProps {
  selectedAddons: string[];
  onAddonsChange: (addons: string[]) => void;
  onNext: () => void;
  onBack: () => void;
}

const ADDONS: Addon[] = [
  // Enhancement Addons
  {
    id: 'detailed_reasoning',
    name: 'Detailed Reasoning',
    description: 'Step-by-step reasoning chains for complex analysis',
    icon: '🔗',
    category: 'enhancement',
    cost: 'free'
  },
  {
    id: 'source_citation',
    name: 'Source Citation',
    description: 'Automatic citation of sources and references',
    icon: '📚',
    category: 'enhancement',
    cost: 'free'
  },
  {
    id: 'multilingual',
    name: 'Multilingual Support',
    description: 'Process content in multiple languages',
    icon: '🌐',
    category: 'enhancement',
    cost: 'premium'
  },
  {
    id: 'real_time_web',
    name: 'Real-time Web Search',
    description: 'Include latest web information in analysis',
    icon: '🔍',
    category: 'enhancement',
    cost: 'premium'
  },

  // Format Addons
  {
    id: 'structured_output',
    name: 'Structured Output',
    description: 'Format results as JSON, tables, or custom structures',
    icon: '📋',
    category: 'format',
    cost: 'free'
  },
  {
    id: 'visual_charts',
    name: 'Visual Charts',
    description: 'Generate charts and graphs from data',
    icon: '📊',
    category: 'format',
    cost: 'premium'
  },
  {
    id: 'presentation_ready',
    name: 'Presentation Ready',
    description: 'Format for presentations with slides and summaries',
    icon: '📽️',
    category: 'format',
    cost: 'premium'
  },

  // Integration Addons
  {
    id: 'api_export',
    name: 'API Export',
    description: 'Export results via REST API for integration',
    icon: '🔌',
    category: 'integration',
    cost: 'premium'
  },
  {
    id: 'webhook_notifications',
    name: 'Webhook Notifications',
    description: 'Send notifications when analysis completes',
    icon: '🔔',
    category: 'integration',
    cost: 'free'
  },
  {
    id: 'cloud_storage',
    name: 'Cloud Storage',
    description: 'Automatically save results to cloud storage',
    icon: '☁️',
    category: 'integration',
    cost: 'premium'
  }
];

const CATEGORY_INFO = {
  enhancement: { name: 'Analysis Enhancements', color: 'blue' },
  format: { name: 'Output Formats', color: 'green' },
  integration: { name: 'Integrations', color: 'purple' }
};

export function AddonsStep({ selectedAddons, onAddonsChange, onNext, onBack }: AddonsStepProps) {
  const handleAddonToggle = (addonId: string) => {
    const newAddons = selectedAddons.includes(addonId)
      ? selectedAddons.filter(id => id !== addonId)
      : [...selectedAddons, addonId];
    onAddonsChange(newAddons);
  };

  const getAddonsByCategory = (category: string) => {
    return ADDONS.filter(addon => addon.category === category);
  };

  const freeAddons = ADDONS.filter(addon => addon.cost === 'free').length;
  const premiumAddons = ADDONS.filter(addon => addon.cost === 'premium').length;

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-cyber-green mb-2">
          Additional Features
        </h2>
        <p className="text-gray-300">
          Enhance your analysis with optional add-ons and integrations
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {Object.entries(CATEGORY_INFO).map(([categoryKey, categoryInfo]) => {
          const categoryAddons = getAddonsByCategory(categoryKey);
          const selectedInCategory = categoryAddons.filter(addon =>
            selectedAddons.includes(addon.id)
          ).length;

          return (
            <div key={categoryKey} className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className={`font-semibold text-${categoryInfo.color}-400`}>
                  {categoryInfo.name}
                </h3>
                <span className="text-xs text-gray-400">
                  {selectedInCategory}/{categoryAddons.length} selected
                </span>
              </div>

              <div className="space-y-3">
                {categoryAddons.map((addon) => (
                  <div
                    key={addon.id}
                    className={`p-4 rounded-lg border-2 transition-all duration-200 cursor-pointer ${
                      selectedAddons.includes(addon.id)
                        ? 'border-cyber-green bg-cyber-green/10'
                        : 'border-gray-600 hover:border-gray-400'
                    }`}
                    onClick={() => handleAddonToggle(addon.id)}
                  >
                    <div className="flex items-start space-x-3">
                      <Checkbox
                        checked={selectedAddons.includes(addon.id)}
                        onChange={() => handleAddonToggle(addon.id)}
                        className="mt-1"
                      />
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="text-xl">{addon.icon}</span>
                          <span className="font-medium text-white">{addon.name}</span>
                          {addon.cost === 'premium' && (
                            <span className="px-2 py-1 text-xs bg-cyber-purple text-white rounded">
                              PREMIUM
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-400">{addon.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-gray-800/50 rounded-lg p-4">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-4">
            <span className="text-green-400">
              ✓ {freeAddons} free add-ons available
            </span>
            <span className="text-cyber-purple">
              ⭐ {premiumAddons} premium add-ons
            </span>
          </div>
          {selectedAddons.length > 0 && (
            <span className="text-cyber-green font-semibold">
              {selectedAddons.length} add-on{selectedAddons.length !== 1 ? 's' : ''} selected
            </span>
          )}
        </div>
      </div>

      <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
        <h3 className="font-semibold text-blue-400 mb-2">💡 Premium Add-ons</h3>
        <p className="text-sm text-gray-300">
          Premium add-ons unlock advanced features and integrations. You can upgrade at any time
          or start with free add-ons and add premium features later.
        </p>
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
          className="bg-cyber-green hover:bg-cyber-green/80 text-black"
        >
          Start Analysis
        </Button>
      </div>
    </div>
  );
}