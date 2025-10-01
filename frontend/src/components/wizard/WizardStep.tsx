import React from 'react';

export type WizardStepType = 'intro' | 'checkbox' | 'textarea' | 'groupbox' | string;

export interface WizardStepConfig {
  title: string;
  type: WizardStepType;
  options?: Array<{ label: string; value: string }>; // for checkbox/groupbox
}

export interface WizardStepProps {
  step: WizardStepConfig;
  stepIndex: number;
  selections: Record<number, any>;
  onSelectionsChange: (index: number, value: any) => void;
  inputs: Record<string, string>;
  onInputChange: (key: string, value: string) => void;
}

const WizardStep: React.FC<WizardStepProps> = ({
  step,
  stepIndex,
  selections,
  onSelectionsChange,
  inputs,
  onInputChange,
}) => {
  switch (step.type) {
    case 'intro':
      return (
        <section aria-labelledby={`step-${stepIndex}-title`}>
          <h2 id={`step-${stepIndex}-title`} className="text-xl font-semibold mb-2">
            {step.title}
          </h2>
          <p className="text-white/80">Welcome to the wizard. Follow the steps to proceed.</p>
        </section>
      );

    case 'checkbox': {
      const current: number[] = selections[stepIndex] || [];
      return (
        <fieldset aria-label={step.title} className="space-y-2">
          <legend className="sr-only">{step.title}</legend>
          {(step.options || []).map((opt, i) => {
            const isChecked = current.includes(i);
            return (
              <label key={opt.value} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={e => {
                    const next = e.target.checked
                      ? [...current, i]
                      : current.filter(v => v !== i);
                    onSelectionsChange(stepIndex, next);
                  }}
                  aria-label={opt.label}
                />
                <span>{opt.label}</span>
              </label>
            );
          })}
        </fieldset>
      );
    }

    case 'textarea': {
      const key = `step_${stepIndex}_text`;
      const value = inputs[key] || '';
      return (
        <div className="space-y-2">
          <label htmlFor={key} className="font-medium">
            {step.title}
          </label>
          <textarea
            id={key}
            value={value}
            onChange={e => onInputChange(key, e.target.value)}
            className="w-full min-h-[160px] p-3 rounded border border-white/20 bg-white/5"
            aria-label={step.title}
          />
        </div>
      );
    }

    case 'groupbox': {
      const selected = selections[stepIndex] ?? null;
      return (
        <div role="group" aria-label={step.title} className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {(step.options || []).map((opt, i) => (
            <button
              key={opt.value}
              type="button"
              aria-pressed={selected === i}
              className={
                'px-3 py-2 rounded border transition-colors ' +
                (selected === i ? 'bg-white text-black border-white' : 'border-white/30 hover:border-white')
              }
              onClick={() => onSelectionsChange(stepIndex, i)}
            >
              {opt.label}
            </button>
          ))}
        </div>
      );
    }

    default:
      return (
        <section aria-labelledby={`step-${stepIndex}-title`}>
          <h2 id={`step-${stepIndex}-title`} className="text-xl font-semibold">
            {step.title}
          </h2>
          <p className="text-white/70">Unsupported step type: {step.type}</p>
        </section>
      );
  }
};

export default WizardStep;


