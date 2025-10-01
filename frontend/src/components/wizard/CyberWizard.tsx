import React, { useState, useEffect } from 'react';
import { useWizardSteps } from '../../hooks/useWizardSteps';
import { useReceipt } from '../../hooks/useReceipt';
import { useOrchestration } from '../../hooks/useOrchestration';
import StepNavigation from './StepNavigation';
import WizardStep from './WizardStep';
import Receipt from './Receipt';
import IntroStep from './steps/IntroStep';
import GoalStep from './steps/GoalStep';
import QueryStep from './steps/QueryStep';
import AnalysisStep from './steps/AnalysisStep';
import ModelStep from './steps/ModelStep';
import AddonsStep from './steps/AddonsStep';

interface WizardStepData {
  title: string;
  color: string;
  type: string;
  narrative?: string;
  options?: any[];
}

const WIZARD_STEPS: WizardStepData[] = [
  { title: '0. Welcome to UltrAI', color: 'mint', type: 'intro', narrative: 'Get better AI answers by combining multiple AI models...', options: [] },
  { title: '1. Select your goals', color: 'mint', type: 'checkbox', narrative: 'What are you working on today?', options: [
    { label: 'Research', icon: '🔬' }, { label: 'Writing/Editing', icon: '✍️' }, { label: 'Document Analysis', icon: '📄' },
    { label: 'Code Creation', icon: '💻' }, { label: 'Business Strategy', icon: '📊' }, { label: 'Creative Projects', icon: '🎨' }
  ]},
  { title: '2. Enter your query', color: 'blue', type: 'textarea', narrative: 'Describe what you need help with...', options: [] },
  { title: '3. Analyses', color: 'purple', type: 'groupbox', narrative: 'Choose how we should combine...', options: [
    { label: 'UltrAI Intelligence Multiplier', icon: '🚀', description: 'Combine the best insights from all models into one answer.', cost: 0.08 },
    { label: 'Fact-check & Confidence (Coming soon)', icon: '✔️', cost: 0.1 },
    { label: "Devil's Advocate (Coming soon)", icon: '⚔️', cost: 0.07 }
  ]},
  { title: '4. Model selection', color: 'deepblue', type: 'checkbox', narrative: 'Which AI models should work on this?', options: [] },
  { title: '5. Add-ons & formatting', color: 'pink', type: 'checkbox', narrative: 'Add extras like PDF export...', options: [
    { label: 'Export as PDF/Word', icon: '📄', cost: 0.02 }, { label: 'Priority Processing', icon: '⚡', cost: 0.05 },
    { label: 'Advanced Formatting', icon: '✨', cost: 0.03 }, { label: 'Source Citations', icon: '📚', cost: 0.04 }
  ]}
];

const MOCK_MODELS = [
  { name: 'gpt-4', provider: 'OpenAI', cost_per_1k_tokens: 0.03 },
  { name: 'claude-3-opus', provider: 'Anthropic', cost_per_1k_tokens: 0.04 },
  { name: 'gemini-1.5-pro', provider: 'Google', cost_per_1k_tokens: 0.02 },
  { name: 'gpt-4o-mini', provider: 'OpenAI', cost_per_1k_tokens: 0.01 },
  { name: 'claude-3-haiku', provider: 'Anthropic', cost_per_1k_tokens: 0.01 },
  { name: 'gpt-3.5-turbo', provider: 'OpenAI', cost_per_1k_tokens: 0.005 },
];

export default function CyberWizardV2() {
  const wizard = useWizardSteps(WIZARD_STEPS);
  const receipt = useReceipt();
  const orchestration = useOrchestration();

  const [selectedGoals, setSelectedGoals] = useState<string[]>([]);
  const [query, setQuery] = useState('');
  const [selectedAnalysis, setSelectedAnalysis] = useState<string[]>([]);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [selectedAddons, setSelectedAddons] = useState<string[]>([]);
  const [isReadyToInitialize, setIsReadyToInitialize] = useState(false);

  // Setup keyboard navigation
  useEffect(() => {
    window.addEventListener('keydown', wizard.handleKeyboard);
    return () => window.removeEventListener('keydown', wizard.handleKeyboard);
  }, [wizard.handleKeyboard]);

  const handleGoalToggle = (goal: string) => {
    setSelectedGoals(prev => 
      prev.includes(goal) ? prev.filter(g => g !== goal) : [...prev, goal]
    );
  };

  const handleAnalysisToggle = (analysis: string) => {
    setSelectedAnalysis(prev => 
      prev.includes(analysis) ? prev.filter(a => a !== analysis) : [...prev, analysis]
    );
  };

  const handleAddonToggle = (addon: string) => {
    setSelectedAddons(prev => 
      prev.includes(addon) ? prev.filter(a => a !== addon) : [...prev, addon]
    );
  };

  const handleSubmitAddons = () => {
    setIsReadyToInitialize(true);
  };

  const handleInitialize = async () => {
    if (selectedModels.length < 2) {
      alert('Please select at least 2 models');
      return;
    }

    try {
      await orchestration.startOrchestration({
        prompt: query,
        models: selectedModels,
        pattern: 'comparative',
        ultraModel: null,
        outputFormat: 'plain',
      });
    } catch (error) {
      console.error('Orchestration failed:', error);
    }
  };

  const currentStep = WIZARD_STEPS[wizard.currentStep];

  // Render current step content
  const renderStepContent = () => {
    switch (wizard.currentStep) {
      case 0:
        return <IntroStep onEnter={() => wizard.goToStep(1)} />;
      case 1:
        return (
          <GoalStep
            options={currentStep.options || []}
            selectedGoals={selectedGoals}
            onToggle={handleGoalToggle}
          />
        );
      case 2:
        return <QueryStep query={query} onChange={setQuery} />;
      case 3:
        return (
          <AnalysisStep
            options={currentStep.options || []}
            selectedAnalysis={selectedAnalysis}
            onToggle={handleAnalysisToggle}
          />
        );
      case 4:
        return (
          <ModelStep
            availableModels={MOCK_MODELS}
            onSelectionChange={setSelectedModels}
          />
        );
      case 5:
        return (
          <AddonsStep
            options={currentStep.options || []}
            selectedAddons={selectedAddons}
            onToggle={handleAddonToggle}
            onSubmit={handleSubmitAddons}
          />
        );
      default:
        return null;
    }
  };

  // Show orchestration status
  if (orchestration.isProcessing || orchestration.isSuccess || orchestration.isError) {
    return (
      <div className="min-h-screen flex items-center justify-center p-8">
        <div className="max-w-2xl w-full">
          {orchestration.isProcessing && (
            <div className="text-center">
              <h2 className="text-3xl font-bold mb-4">ULTRA SYNTHESIS™</h2>
              <div className="mb-4">
                <div className="w-full bg-gray-700 rounded-full h-4">
                  <div
                    className="bg-purple-600 h-4 rounded-full transition-all duration-500"
                    style={{ width: `${orchestration.progress}%` }}
                  />
                </div>
              </div>
              <p className="text-gray-400">Processing your query...</p>
            </div>
          )}

          {orchestration.isSuccess && (
            <div>
              <h2 className="text-2xl font-bold mb-4">Analysis Complete</h2>
              <div className="bg-gray-800 p-6 rounded-lg mb-4">
                <p className="whitespace-pre-wrap">{orchestration.result?.ultra_response}</p>
              </div>
              <button
                onClick={orchestration.reset}
                className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg"
              >
                Start New
              </button>
            </div>
          )}

          {orchestration.isError && (
            <div>
              <h2 className="text-2xl font-bold mb-4 text-red-500">Error Occurred</h2>
              <p className="text-gray-400 mb-4">{orchestration.error?.message}</p>
              <button
                onClick={orchestration.reset}
                className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg"
              >
                Try Again
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto p-8">
        <div className="grid grid-cols-12 gap-8">
          {/* Main wizard panel */}
          <div className="col-span-8">
            {/* Step navigation (skip step 0) */}
            {wizard.currentStep > 0 && (
              <StepNavigation
                steps={WIZARD_STEPS}
                currentStep={wizard.currentStep}
                onStepClick={wizard.goToStep}
              />
            )}

            {/* Current step content */}
            <div className="bg-gray-800 rounded-lg mt-6">
              {renderStepContent()}
            </div>

            {/* Initialize button (show after addons submitted) */}
            {isReadyToInitialize && selectedModels.length >= 2 && (
              <div className="mt-6 text-center">
                <button
                  onClick={handleInitialize}
                  className="px-12 py-4 text-xl font-bold bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 rounded-lg transition-all transform hover:scale-105"
                >
                  Initialize UltrAI
                </button>
              </div>
            )}
          </div>

          {/* Receipt panel */}
          <div className="col-span-4">
            <Receipt items={receipt.items} total={receipt.total} />
          </div>
        </div>
      </div>
    </div>
  );
}
