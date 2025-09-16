'use client';
import { useEffect, useState, useMemo, useCallback, memo } from 'react';
import { Button } from '@components/ui/button';
import { Checkbox } from '@components/ui/checkbox';
import { Card } from '@components/ui/card';
import {
  useAvailableModels,
  useOrchestration,
} from '@api/queries/orchestratorQueries';
import LaunchStatus from '@components/wizard/LaunchStatus';
import { captureNoBadAnswerFromOrchestrator } from '@internal/analysisTracker';
import { RadioGroup, RadioGroupItem } from '@components/ui/radio-group';
import { Input } from '@components/ui/input';
import { OutlineIcon } from '@components/icons/OutlineIcons';
import {
  Rocket,
  Film,
  Check,
  Copy,
  Zap,
  Activity,
  Sparkles,
  Brain,
  Network,
  Download,
} from 'lucide-react';
import SkinSwitcher from '@components/SkinSwitcher';

interface StepOption {
  label: string;
  cost?: number;
  icon?: string;
  description?: string;
}

interface Step {
  title: string;
  color: string;
  type: string;
  narrative?: string;
  options?: StepOption[];
  baseCost?: number;
}

interface SummaryItem {
  label: string;
  cost: number;
  color: string;
  section: string;
}

interface ReceiptSectionProps {
  sectionTitle: string;
  items: SummaryItem[];
}

const ReceiptSection = memo(function ReceiptSection({
  sectionTitle,
  items,
}: ReceiptSectionProps) {
  const dots = '. . . . . . . . . . . . . . . . . . . .';
  return (
    <div className="mb-3">
      <div className="uppercase text-[9px] tracking-[0.2em] mb-2 text-center text-white/60 font-bold">
        {sectionTitle}
      </div>
      {items.map((s, i) => (
        <div
          key={i}
          className="text-[11px] leading-relaxed flex items-center text-white/85 hover:text-white transition-colors duration-200 group cursor-pointer mb-1"
        >
          <span
            className="flex-auto overflow-hidden text-ellipsis whitespace-nowrap group-hover:text-shadow-sm font-medium"
            title={s.label}
          >
            {s.label}
          </span>
          <span className="px-1 select-none opacity-30 group-hover:opacity-50 text-[10px]">
            {dots}
          </span>
          <span className="text-right w-16 group-hover:text-pink-400 transition-colors font-mono">
            ${s.cost.toFixed(2)}
          </span>
        </div>
      ))}
    </div>
  );
});

export default function CyberWizardWithQuery() {
  // Track current skin
  const [currentSkin, setCurrentSkin] = useState(() => {
    return (
      Array.from(document.body.classList)
        .find(cls => cls.startsWith('skin-'))
        ?.replace('skin-', '') || 'night'
    );
  });

  const isNonTimeSkin = ['minimalist', 'business'].includes(currentSkin);
  const isDemoMode = import.meta.env.VITE_API_MODE === 'mock' || import.meta.env.VITE_DEMO_MODE === 'true';

  // Theme URLs
  const themeBgUrl = `/backgrounds/${currentSkin}-bg.webp`;
  const themeBgUrl2x = `/backgrounds/${currentSkin}-bg@2x.webp`;

  // React Query hooks
  const { data: modelsData, isLoading: isLoadingModels } = useAvailableModels(false);
  const orchestrationMutation = useOrchestration();

  // Extract models from React Query data
  const availableModels = useMemo(() => {
    if (!modelsData?.models) return [];
    return modelsData.models
      .map((m: any) => (typeof m === 'string' ? m : m.id || m.name))
      .filter(Boolean);
  }, [modelsData]);

  const availableModelInfos = useMemo(() => {
    if (!modelsData?.models) return {};
    const infoMap: Record<string, { provider: string; cost_per_1k_tokens: number }> = {};
    modelsData.models.forEach((m: any) => {
      const name = typeof m === 'string' ? m : m.id || m.name;
      if (!name) return;
      infoMap[name] = {
        provider: m.provider || '',
        cost_per_1k_tokens: m.cost_per_1k_tokens || 0,
      };
    });
    return infoMap;
  }, [modelsData]);

  const modelStatuses = useMemo(() => {
    const statusMap: Record<string, 'checking' | 'ready' | 'error'> = {};
    availableModels.forEach((modelName: string) => {
      statusMap[modelName] = 'ready';
    });
    return statusMap;
  }, [availableModels]);

  // State
  const [currentStep, setCurrentStep] = useState(0);
  const [stepFadeKey, setStepFadeKey] = useState(0);
  const [selections, setSelections] = useState<Record<string, any>>({});
  const [showStatus, setShowStatus] = useState(false);
  const [steps, setSteps] = useState<Step[]>([]);
  const [stepInput, setStepInput] = useState<Record<string, string>>({});
  const [presetTemplate, setPresetTemplate] = useState<string>('custom');
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [showModelDetails, setShowModelDetails] = useState(false);
  const [hasCompleted, setHasCompleted] = useState(false);
  const [ultraResponseText, setUltraResponseText] = useState('');
  const [ultrasynthesisError, setUltrasynthesisError] = useState<string | null>(null);
  const [demoData, setDemoData] = useState<any>(null);

  // Load wizard steps
  useEffect(() => {
    const load = async () => {
      try {
        const response = await fetch('/wizard_steps.json', {
          cache: 'no-store',
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        if (!Array.isArray(data))
          throw new Error('Invalid steps schema: not an array');
        setSteps(data as Step[]);
      } catch (error) {
        console.error('Failed to load wizard steps', error);
        setSteps([]);
      }
    };
    load();
  }, []);

  // Load demo data in demo mode
  useEffect(() => {
    if (!isDemoMode) return;
    const load = async () => {
      try {
        const response = await fetch('/demo/ultrai_demo.json');
        if (!response.ok) return;
        const data = await response.json();
        setDemoData(data);
      } catch (error) {
        console.error('Failed to load demo data', error);
      }
    };
    load();
  }, [isDemoMode]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) return;

      switch (e.key) {
        case 'ArrowRight':
          if (currentStep < steps.length - 1 && !showStatus) {
            setCurrentStep(prev => prev + 1);
            setStepFadeKey(k => k + 1);
          }
          break;
        case 'ArrowLeft':
          if (currentStep > 0 && !showStatus) {
            setCurrentStep(prev => prev - 1);
            setStepFadeKey(k => k + 1);
          }
          break;
        case 'Enter':
          if (currentStep === 0) {
            setCurrentStep(1);
            setStepFadeKey(k => k + 1);
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentStep, steps.length, showStatus]);

  // Orchestration using React Query mutation
  const runOrchestration = useCallback(async () => {
    const queryText = stepInput['query'] || '';
    if (!queryText) {
      setUltrasynthesisError('No query provided');
      return;
    }

    // Determine selected models
    const modelsToUse = selectedModels.length > 0 
      ? selectedModels 
      : availableModels.slice(0, 3); // Default to first 3 models

    if (modelsToUse.length < 2) {
      setUltrasynthesisError('Please select at least 2 models');
      return;
    }

    try {
      const result = await orchestrationMutation.mutateAsync({
        prompt: queryText,
        models: modelsToUse,
        pattern: 'comparative',
        outputFormat: 'plain',
      });

      if (result) {
        setUltraResponseText(result.ultra_response || 'No response generated');
        captureNoBadAnswerFromOrchestrator(result);
        setHasCompleted(true);
      }
    } catch (error: any) {
      console.error('Orchestration error:', error);
      setUltrasynthesisError(error.message || 'Failed to process request');
    }
  }, [stepInput, selectedModels, availableModels, orchestrationMutation]);

  // Handle step submission
  const handleStepSubmit = useCallback(() => {
    const step = steps[currentStep];
    if (!step) return;

    if (currentStep === steps.length - 1) {
      // Last step - initiate orchestration
      setShowStatus(true);
      runOrchestration();
    } else {
      // Move to next step
      setCurrentStep(prev => prev + 1);
      setStepFadeKey(k => k + 1);
    }
  }, [currentStep, steps, runOrchestration]);

  // Calculate summary items for receipt
  const summaryItems = useMemo(() => {
    const items: SummaryItem[] = [];
    
    Object.entries(selections).forEach(([stepIdx, selected]) => {
      const step = steps[parseInt(stepIdx)];
      if (!step || !step.options) return;

      const selectedOptions = Array.isArray(selected) ? selected : [selected];
      selectedOptions.forEach(optionIdx => {
        const option = step.options?.[optionIdx];
        if (option && option.cost) {
          items.push({
            label: option.label,
            cost: option.cost,
            color: step.color,
            section: step.title,
          });
        }
      });
    });

    // Add model costs
    selectedModels.forEach(modelName => {
      const info = availableModelInfos[modelName];
      if (info) {
        items.push({
          label: modelName,
          cost: info.cost_per_1k_tokens * 10, // Estimate 10k tokens
          color: 'purple',
          section: 'Model selection',
        });
      }
    });

    return items;
  }, [selections, steps, selectedModels, availableModelInfos]);

  const totalCost = summaryItems.reduce((sum, item) => sum + item.cost, 0);

  // Color mapping functions
  const mapColorHex = (color: string): string => {
    const colorMap: Record<string, string> = {
      mint: '#00ff9f',
      blue: '#00d4ff',
      purple: '#bd00ff',
      pink: '#ff6cfc',
      orange: '#ff6600',
      yellow: '#ffd700',
      green: '#00ff00',
      red: '#ff3366',
    };
    return colorMap[color] || '#ffffff';
  };

  const mapColorRGBA = (color: string, alpha: number): string => {
    const hex = mapColorHex(color);
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  };

  // If showing status/results
  if (showStatus) {
    return (
      <LaunchStatus
        summary={summaryItems}
        totalCost={totalCost}
        hasCompleted={hasCompleted}
        ultraResponseText={ultraResponseText}
        ultrasynthesisError={ultrasynthesisError}
        isDemoMode={isDemoMode}
      />
    );
  }

  // If on welcome screen
  if (currentStep === 0) {
    return (
      <div className="relative flex items-center justify-center min-h-screen w-full">
        {/* Background */}
        {!isNonTimeSkin && (
          <div
            className="pointer-events-none fixed inset-0"
            style={{
              backgroundImage: `image-set(url('${themeBgUrl}') 1x, url('${themeBgUrl2x}') 2x)`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
            }}
          />
        )}

        {/* Content */}
        <div className="relative z-10 max-w-5xl mx-auto p-8">
          <h1 className="text-6xl font-bold text-center mb-8 gradient-text">
            Welcome to UltrAI
          </h1>
          <p className="text-xl text-center mb-12 text-white/80">
            Intelligence Multiplication Platform
          </p>
          <div className="text-center">
            <button
              onClick={() => {
                setCurrentStep(1);
                setStepFadeKey(k => k + 1);
              }}
              className="px-12 py-5 text-xl font-bold rounded-lg gradient-button"
              aria-label="Start using UltrAI analysis wizard"
            >
              Enter UltrAI →
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Current step data
  const step = steps[currentStep];
  if (!step) return null;

  // Render step content
  return (
    <div className={`relative flex flex-col min-h-screen w-full ${isNonTimeSkin ? 'text-gray-900' : 'text-white'}`}>
      {/* Skip link */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only fixed top-2 left-2 z-50 bg-black text-white px-3 py-2 rounded"
      >
        Skip to content
      </a>

      {/* Skin Switcher */}
      <SkinSwitcher />

      {/* Background */}
      {!isNonTimeSkin && (
        <div
          className="pointer-events-none fixed inset-0"
          style={{
            backgroundImage: `image-set(url('${themeBgUrl}') 1x, url('${themeBgUrl2x}') 2x)`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        />
      )}

      {/* Main content */}
      <main id="main-content" className="relative z-10 flex-1 flex flex-col items-center justify-center p-8">
        <div className="w-full max-w-4xl mx-auto">
          {/* Step indicators */}
          <nav className="flex justify-center gap-2 mb-8" aria-label="Wizard steps">
            {steps.map((s, idx) => (
              <button
                key={idx}
                onClick={() => {
                  if (idx <= currentStep && !showStatus) {
                    setCurrentStep(idx);
                    setStepFadeKey(k => k + 1);
                  }
                }}
                className={`w-3 h-3 rounded-full transition-all ${
                  idx === currentStep
                    ? 'bg-white scale-125'
                    : idx < currentStep
                    ? 'bg-white/60 hover:bg-white/80'
                    : 'bg-white/20'
                }`}
                disabled={idx > currentStep}
                aria-label={`Go to step ${idx + 1}`}
              />
            ))}
          </nav>

          {/* Step content */}
          <Card className="glass-panel p-8">
            <h2 className="text-2xl font-bold mb-6" style={{ color: mapColorHex(step.color) }}>
              {step.title}
            </h2>

            {step.narrative && (
              <p className="text-lg mb-6 text-white/80">{step.narrative}</p>
            )}

            {/* Step type specific content */}
            {step.type === 'checkbox' && step.options && (
              <div className="space-y-3">
                {step.options.map((option, idx) => (
                  <label key={idx} className="flex items-center gap-3 cursor-pointer hover:bg-white/5 p-3 rounded">
                    <Checkbox
                      checked={selections[currentStep]?.includes(idx) || false}
                      onCheckedChange={(checked) => {
                        setSelections(prev => ({
                          ...prev,
                          [currentStep]: checked
                            ? [...(prev[currentStep] || []), idx]
                            : (prev[currentStep] || []).filter(i => i !== idx)
                        }));
                      }}
                      aria-label={option.label}
                    />
                    <span className="flex-1">{option.label}</span>
                    {option.cost && (
                      <span className="text-sm text-white/60">${option.cost.toFixed(2)}</span>
                    )}
                  </label>
                ))}
              </div>
            )}

            {step.type === 'textarea' && (
              <textarea
                value={stepInput.query || ''}
                onChange={(e) => setStepInput(prev => ({ ...prev, query: e.target.value }))}
                className="w-full h-32 p-4 bg-white/10 border border-white/20 rounded-lg resize-none"
                placeholder="Enter your query..."
                aria-label="What do you need analyzed?"
              />
            )}

            {/* Navigation buttons */}
            <div className="flex justify-between mt-8">
              <Button
                onClick={() => {
                  setCurrentStep(prev => prev - 1);
                  setStepFadeKey(k => k + 1);
                }}
                disabled={currentStep === 0}
                variant="outline"
              >
                Back
              </Button>
              <Button
                onClick={handleStepSubmit}
                disabled={orchestrationMutation.isPending}
              >
                {currentStep === steps.length - 1 ? 'Initialize UltrAI' : 'Next'}
              </Button>
            </div>
          </Card>

          {/* Receipt */}
          {summaryItems.length > 0 && (
            <Card className="mt-8 p-6 glass-panel">
              <h3 className="text-lg font-bold mb-4">Receipt</h3>
              {summaryItems.map((item, idx) => (
                <div key={idx} className="flex justify-between text-sm">
                  <span>{item.label}</span>
                  <span>${item.cost.toFixed(2)}</span>
                </div>
              ))}
              <div className="border-t border-white/20 mt-4 pt-4">
                <div className="flex justify-between font-bold">
                  <span>Total</span>
                  <span>${totalCost.toFixed(2)}</span>
                </div>
              </div>
            </Card>
          )}
        </div>
      </main>
    </div>
  );
}