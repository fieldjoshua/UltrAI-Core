import React, { memo } from 'react';
import { Checkbox } from '@components/ui/checkbox';
import { RadioGroup, RadioGroupItem } from '@components/ui/radio-group';
import { Input } from '@components/ui/input';
import { Button } from '@components/ui/button';
import { Wand2, Sparkles } from 'lucide-react';

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
}

interface WizardStepContentProps {
  step: Step;
  stepNumber: number;
  selections: Record<string, any>;
  stepInput: Record<string, string>;
  onSelectionsChange: (stepNumber: number, value: any) => void;
  onInputChange: (key: string, value: string) => void;
  mapColorHex: (color: string) => string;
  isDemoMode?: boolean;
}

const WizardStepContent = memo(function WizardStepContent({
  step,
  stepNumber,
  selections,
  stepInput,
  onSelectionsChange,
  onInputChange,
  mapColorHex,
  isDemoMode = false,
}: WizardStepContentProps) {
  // Handle checkbox selection
  const handleCheckboxChange = (optionIdx: number, checked: boolean) => {
    const currentSelections = selections[stepNumber] || [];
    if (checked) {
      onSelectionsChange(stepNumber, [...currentSelections, optionIdx]);
    } else {
      onSelectionsChange(
        stepNumber,
        currentSelections.filter((idx: number) => idx !== optionIdx)
      );
    }
  };

  // Handle query optimization
  const handleOptimizeQuery = () => {
    const currentQuery = stepInput.query || '';
    const optimizedQuery = `${currentQuery}\n\n[Please provide a comprehensive, specific, and detailed analysis with the following considerations:\n- Include multiple perspectives and viewpoints\n- Provide concrete examples where applicable\n- Consider potential edge cases and limitations\n- Suggest actionable next steps\n- Use clear structure and formatting]`;
    onInputChange('query', optimizedQuery);
  };

  return (
    <div className="space-y-6 relative" role="group" aria-labelledby={`step-${stepNumber}-title`}>
      {/* Step title */}
      <h2
        id={`step-${stepNumber}-title`}
        className="text-2xl font-bold text-center mb-6"
        style={{ color: mapColorHex(step.color) }}
      >
        {step.title}
      </h2>

      {/* Step narrative */}
      {step.narrative && (
        <p className="text-lg text-center text-white/80 mb-8 max-w-2xl mx-auto">
          {step.narrative}
        </p>
      )}

      {/* Step type: checkbox options */}
      {step.type === 'checkbox' && step.options && (
        <div className="space-y-3" role="group" aria-label="Select options">
          {step.options.map((option, idx) => {
            const isSelected = (selections[stepNumber] || []).includes(idx);
            return (
              <label
                key={idx}
                className={`
                  flex items-center gap-4 p-4 rounded-lg border cursor-pointer
                  transition-all duration-200 group
                  ${isSelected 
                    ? 'bg-white/10 border-white/40' 
                    : 'hover:bg-white/5 border-white/20'
                  }
                `}
              >
                <Checkbox
                  checked={isSelected}
                  onCheckedChange={(checked) => handleCheckboxChange(idx, checked as boolean)}
                  className="data-[state=checked]:bg-white data-[state=checked]:text-black"
                  aria-label={option.label}
                />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    {option.icon && <span className="text-2xl">{option.icon}</span>}
                    <span className="font-medium">{option.label}</span>
                  </div>
                  {option.description && (
                    <p className="text-sm text-white/60 mt-1">{option.description}</p>
                  )}
                </div>
                {option.cost !== undefined && (
                  <div className="text-right">
                    <span className="text-lg font-mono">${option.cost.toFixed(2)}</span>
                    <span className="text-xs text-white/60 block">per use</span>
                  </div>
                )}
              </label>
            );
          })}
        </div>
      )}

      {/* Step type: radio options */}
      {step.type === 'radio' && step.options && (
        <RadioGroup
          value={selections[stepNumber]?.toString() || ''}
          onValueChange={(value) => onSelectionsChange(stepNumber, parseInt(value))}
        >
          <div className="space-y-3" role="group" aria-label="Select one option">
            {step.options.map((option, idx) => (
              <label
                key={idx}
                className={`
                  flex items-center gap-4 p-4 rounded-lg border cursor-pointer
                  transition-all duration-200
                  ${selections[stepNumber] === idx 
                    ? 'bg-white/10 border-white/40' 
                    : 'hover:bg-white/5 border-white/20'
                  }
                `}
              >
                <RadioGroupItem
                  value={idx.toString()}
                  className="text-white"
                  aria-label={option.label}
                />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    {option.icon && <span className="text-2xl">{option.icon}</span>}
                    <span className="font-medium">{option.label}</span>
                  </div>
                  {option.description && (
                    <p className="text-sm text-white/60 mt-1">{option.description}</p>
                  )}
                </div>
                {option.cost !== undefined && (
                  <div className="text-right">
                    <span className="text-lg font-mono">${option.cost.toFixed(2)}</span>
                  </div>
                )}
              </label>
            ))}
          </div>
        </RadioGroup>
      )}

      {/* Step type: textarea */}
      {step.type === 'textarea' && (
        <div className="space-y-4">
          <div className="relative">
            <textarea
              value={stepInput.query || ''}
              onChange={(e) => onInputChange('query', e.target.value)}
              className="w-full min-h-[200px] p-4 rounded-lg border border-white/20 
                bg-white/5 text-white placeholder-white/40
                focus:border-white/40 focus:bg-white/10 
                transition-all duration-200 resize-none"
              placeholder="Describe what you need analyzed, created, or explained..."
              aria-label="What do you need analyzed?"
              autoFocus
            />
            <div className="absolute bottom-3 right-3 text-xs text-white/40">
              {(stepInput.query || '').length} / 1000
            </div>
          </div>

          {/* Query optimization button */}
          {stepInput.query && stepInput.query.length > 10 && (
            <div className="flex justify-center animate-fade-in">
              <Button
                onClick={handleOptimizeQuery}
                variant="outline"
                className="group"
              >
                <Wand2 className="w-4 h-4 mr-2 group-hover:rotate-12 transition-transform" />
                Optimize my query with AI
                <Sparkles className="w-4 h-4 ml-2 opacity-50 group-hover:opacity-100" />
              </Button>
            </div>
          )}

          {/* Demo mode indicator */}
          {isDemoMode && !stepInput.query && (
            <p className="text-center text-cyan-400/60 text-sm animate-pulse">
              Demo mode: A sample query will be loaded automatically
            </p>
          )}
        </div>
      )}

      {/* Step type: custom input */}
      {step.type === 'input' && (
        <div className="space-y-4">
          <Input
            type="text"
            value={stepInput[`step_${stepNumber}`] || ''}
            onChange={(e) => onInputChange(`step_${stepNumber}`, e.target.value)}
            className="w-full p-4 text-lg bg-white/5 border-white/20 
              focus:bg-white/10 focus:border-white/40"
            placeholder="Enter your response..."
            aria-label={step.narrative || step.title}
          />
        </div>
      )}
    </div>
  );
});

export default WizardStepContent;