import React, { useState } from 'react';
import ProgressStepper, { StepDef } from './ProgressStepper';

export type ReceiptItem = { key: string; value: string };

export interface GuidedChatProps {
  onChangeReceipt?: (items: ReceiptItem[], costCents: number) => void;
  onLaunch?: (payload: any) => void;
}

// Five steps per steps.txt
const STEPS: StepDef[] = [
  { id: 'goals', label: 'Goals', color: 'cyan' },
  { id: 'request', label: 'Request', color: 'purple' },
  { id: 'models', label: 'Models', color: 'orange' },
  { id: 'analysis', label: 'Analysis', color: 'green' },
  { id: 'finish', label: 'Finish', color: 'pink' },
];

const colorToRing: Record<string, string> = {
  cyan: 'focus:ring-cyan-400',
  purple: 'focus:ring-purple-400',
  orange: 'focus:ring-orange-400',
  green: 'focus:ring-green-400',
  pink: 'focus:ring-pink-400',
};

const GuidedChat: React.FC<GuidedChatProps> = ({
  onChangeReceipt,
  onLaunch,
}) => {
  const [index, setIndex] = useState(0);
  const [receipt, setReceipt] = useState<ReceiptItem[]>([]);
  const [costCents, setCostCents] = useState(0);

  const current = STEPS[index];

  function updateReceipt(updater: (prev: ReceiptItem[]) => ReceiptItem[]) {
    setReceipt(prev => {
      const next = updater(prev);
      onChangeReceipt?.(next, costCents);
      return next;
    });
  }

  function next() {
    setIndex(i => Math.min(STEPS.length - 1, i + 1));
  }

  function prev() {
    setIndex(i => Math.max(0, i - 1));
  }

  function addCost(cents: number) {
    setCostCents(c => {
      const n = c + cents;
      onChangeReceipt?.(receipt, n);
      return n;
    });
  }

  // Simple controls per step
  const renderStep = () => {
    switch (current.id) {
      case 'goals':
        return (
          <div>
            <p className="text-sm text-muted-foreground mb-2">
              Select your goal(s)
            </p>
            <div className="grid grid-cols-2 gap-2">
              {[
                'Homework',
                'Research',
                'Assistant',
                'Doc Analysis',
                'Coding',
                'Other',
              ].map(g => (
                <label key={g} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    onChange={e =>
                      updateReceipt(prev => {
                        const other = prev.filter(x => x.key !== 'Goals');
                        const selected = new Set(
                          prev
                            .find(x => x.key === 'Goals')
                            ?.value.split(', ') || []
                        );
                        if (e.target.checked) selected.add(g);
                        else selected.delete(g);
                        return [
                          ...other,
                          {
                            key: 'Goals',
                            value: Array.from(selected).join(', '),
                          },
                        ];
                      })
                    }
                  />
                  <span>{g}</span>
                </label>
              ))}
            </div>
          </div>
        );
      case 'request':
        return (
          <div>
            <p className="text-sm text-muted-foreground mb-2">
              Describe your request
            </p>
            <textarea
              className={`w-full p-3 rounded border bg-background ${colorToRing[current.color]} focus:outline-none focus:ring-2`}
              rows={4}
              placeholder="What would you like UltrAI to do?"
              onBlur={e =>
                updateReceipt(prev => [
                  ...prev.filter(x => x.key !== 'Request'),
                  { key: 'Request', value: e.target.value },
                ])
              }
            />
          </div>
        );
      case 'models':
        return (
          <div>
            <p className="text-sm text-muted-foreground mb-2">
              Choose models or let UltrAI decide
            </p>
            <div className="flex flex-wrap gap-2">
              {['gpt-4o', 'claude-3-5-sonnet', 'gemini-1.5-pro', 'auto'].map(
                m => (
                  <button
                    key={m}
                    className="px-3 py-1 rounded border hover:bg-muted"
                    onClick={() =>
                      updateReceipt(prev => [
                        ...prev.filter(x => x.key !== 'Models'),
                        { key: 'Models', value: m },
                      ])
                    }
                  >
                    {m}
                  </button>
                )
              )}
            </div>
          </div>
        );
      case 'analysis':
        return (
          <div>
            <p className="text-sm text-muted-foreground mb-2">
              Select analysis pattern
            </p>
            <div className="flex flex-wrap gap-2">
              {[
                'gut',
                'confidence',
                'critique',
                'fact_check',
                'perspective',
                'auto',
              ].map(p => (
                <button
                  key={p}
                  className="px-3 py-1 rounded border hover:bg-muted"
                  onClick={() =>
                    updateReceipt(prev => [
                      ...prev.filter(x => x.key !== 'Pattern'),
                      { key: 'Pattern', value: p },
                    ])
                  }
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        );
      case 'finish':
        return (
          <div>
            <p className="text-sm text-muted-foreground mb-2">
              Finishing touches
            </p>
            <div className="grid grid-cols-2 gap-2">
              {[
                'Encrypted',
                'Markdown',
                'PDF',
                'Fact Checked',
                'No AI-Speak',
                'References',
              ].map(f => (
                <label key={f} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    onChange={e => {
                      updateReceipt(prev => {
                        const others = prev.filter(x => x.key !== 'Finish');
                        const set = new Set(
                          prev
                            .find(x => x.key === 'Finish')
                            ?.value.split(', ') || []
                        );
                        if (e.target.checked) set.add(f);
                        else set.delete(f);
                        return [
                          ...others,
                          { key: 'Finish', value: Array.from(set).join(', ') },
                        ];
                      });
                      addCost(5); // mock incremental cost
                    }}
                  />
                  <span>{f}</span>
                </label>
              ))}
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      <ProgressStepper
        steps={STEPS}
        currentIndex={index}
        completedCount={index}
      />

      <div className="p-4 rounded-md border bg-background">{renderStep()}</div>

      <div className="flex justify-between">
        <button
          className="px-4 py-2 rounded border"
          onClick={prev}
          disabled={index === 0}
        >
          Back
        </button>
        {index < STEPS.length - 1 ? (
          <button
            className="px-4 py-2 rounded bg-primary text-primary-foreground"
            onClick={next}
          >
            Next
          </button>
        ) : (
          <button
            className="px-4 py-2 rounded bg-green-600 text-white"
            onClick={() => onLaunch?.({ receipt, costCents })}
          >
            Launch UltrAI
          </button>
        )}
      </div>
    </div>
  );
};

export default GuidedChat;
