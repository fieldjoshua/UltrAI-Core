"use client";
import { useEffect, useState } from "react";
import OptionCards from "./OptionCards";
import AnalysisModes from "./AnalysisModes";
import StatusUpdater from "./StatusUpdater";

interface StepOption { label: string; cost?: number; icon?: string; description?: string }
interface Step {
  title: string;
  color: string;
  type: string;
  narrative?: string;
  options?: StepOption[];
  baseCost?: number;
}
interface SummaryItem { label: string; cost: number; color: string }

export default function CyberWizard() {
  const [steps, setSteps] = useState<Step[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [summary, setSummary] = useState<SummaryItem[]>([]);
  const [totalCost, setTotalCost] = useState(0);
  const [selectedGoals, setSelectedGoals] = useState<string[]>([]);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [selectedAddons, setSelectedAddons] = useState<string[]>([]);
  const [selectedAnalysisModes, setSelectedAnalysisModes] = useState<string[]>([]);
  const [showStatus, setShowStatus] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const response = await fetch("/wizard_steps.json", { cache: "no-store" });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        if (!Array.isArray(data)) throw new Error("Invalid steps schema: not an array");
        setSteps(data as Step[]);
      } catch (error) {
        console.error("Failed to load wizard steps", error);
        setSteps([]);
      }
    };
    load();
  }, []);

  const addSelection = (label: string, cost: number | undefined, color: string) => {
    const appliedCost = typeof cost === 'number' ? cost : 0;
    setSummary(prev => [...prev, { label, cost: appliedCost, color }]);
    setTotalCost(prev => prev + appliedCost);
  };

  const removeSelectionCost = (cost?: number) => {
    const appliedCost = typeof cost === 'number' ? cost : 0;
    setTotalCost(prev => Math.max(0, prev - appliedCost));
  };

  if (steps.length === 0) return <div>Loading…</div>;

  const step = steps[currentStep];
  const mapColorHex = (c: string) => c === 'mint' ? '#00ff9f'
    : c === 'blue' ? '#00b8ff'
    : c === 'deepblue' ? '#001eff'
    : c === 'purple' ? '#bd00ff'
    : '#d600ff';
  const mapColorRGBA = (c: string, alpha: number) => c === 'mint' ? `rgba(0,255,159,${alpha})`
    : c === 'blue' ? `rgba(0,184,255,${alpha})`
    : c === 'deepblue' ? `rgba(0,30,255,${alpha})`
    : c === 'purple' ? `rgba(189,0,255,${alpha})`
    : `rgba(214,0,255,${alpha})`;

  const colorHex = mapColorHex(step.color);
  const colorRGBA = mapColorRGBA(step.color, 0.08);

  // Toggle handlers per step category
  const handleGoalToggle = (label: string) => {
    const option = step.options?.find(o => o.label === label);
    const cost = option?.cost;
    setSelectedGoals(prev => {
      if (prev.includes(label)) {
        removeSelectionCost(cost);
        return prev.filter(l => l !== label);
      }
      addSelection(label, cost, step.color);
      return [...prev, label];
    });
  };
  const handleModelToggle = (label: string) => {
    const option = step.options?.find(o => o.label === label);
    const cost = option?.cost;
    setSelectedModels(prev => {
      if (prev.includes(label)) {
        removeSelectionCost(cost);
        return prev.filter(l => l !== label);
      }
      addSelection(label, cost, step.color);
      return [...prev, label];
    });
  };
  const handleAddonToggle = (label: string) => {
    const option = step.options?.find(o => o.label === label);
    const cost = option?.cost;
    setSelectedAddons(prev => {
      if (prev.includes(label)) {
        removeSelectionCost(cost);
        return prev.filter(l => l !== label);
      }
      addSelection(label, cost, step.color);
      return [...prev, label];
    });
  };
  const handleAnalysisToggle = (label: string) => {
    setSelectedAnalysisModes(prev => prev.includes(label) ? prev.filter(l => l !== label) : [...prev, label]);
  };

  return (
    <div className="relative flex h-screen w-full items-center justify-center gap-8 p-6 text-white font-cyber text-sm"
    >
      {/* Background layer (overlay removed) */}
      <div className="pointer-events-none absolute inset-0 animate-parallax-slow"
           style={{ backgroundImage: "url('/cityscape-background.jpeg')", backgroundSize: 'cover', backgroundPosition: 'center', zIndex: 0 }} />

      {/* Content layer */}
      <div className="relative z-10 flex items-start justify-center gap-8 w-full">
      {/* Wizard Panel (left) */}
      <div className="w-[420px] flex-none" style={{ marginTop: '25vh' }}>
        <div
          className={`glass-strong p-5 rounded-2xl transition-all duration-300 min-h-[48vh] animate-border-hum
            ${step.color === "mint" ? "shadow-neon-mint"
            : step.color === "blue" ? "shadow-neon-blue"
            : step.color === "deepblue" ? "shadow-neon-deep"
            : step.color === "purple" ? "shadow-neon-purple"
            : "shadow-neon-pink"}`}
          style={{ borderColor: colorHex, borderWidth: 7, background: colorRGBA, boxShadow: `0 0 0 2px rgba(255,255,255,0.08) inset, 0 0 14px ${colorHex}` }}
        >
        {/* Step markers with connecting lines (labels removed) */}
        <div className="w-full mb-5">
          <div className="flex items-center">
            {steps.map((s, i) => {
              const isActive = i === currentStep;
              const isDone = i < currentStep;
              const dotHex = mapColorHex(s.color);
              const dotFill = mapColorRGBA(s.color, isActive ? 0.3 : isDone ? 0.18 : 0.08);
              const shadowClass = s.color === 'mint' ? 'shadow-neon-mint'
                : s.color === 'blue' ? 'shadow-neon-blue'
                : s.color === 'deepblue' ? 'shadow-neon-deep'
                : s.color === 'purple' ? 'shadow-neon-purple'
                : 'shadow-neon-pink';
              return (
                <div key={i} className="flex items-center flex-1">
                  <div
                    className={`rounded-full ${shadowClass}`}
                    style={{
                      width: 24,
                      height: 24,
                      backgroundColor: dotFill,
                      boxShadow: isActive
                        ? `0 0 0 2px #FFD700, 0 0 0 4px ${dotHex}, inset 0 0 8px ${dotHex}`
                        : `0 0 0 1px ${dotHex}`,
                      opacity: isDone || isActive ? 1 : 0.6
                    }}
                  />
                  {i < steps.length - 1 && (
                    <div
                      className="mx-2"
                      style={{
                        height: 2,
                        backgroundColor: i < currentStep ? dotHex : 'rgba(255,255,255,0.25)',
                        boxShadow: i < currentStep ? `0 0 6px ${dotHex}` : undefined,
                        flexGrow: 1
                      }}
                    />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        <h2 className={`${
          step.color === 'mint' ? 'text-neon-mint'
          : step.color === 'blue' ? 'text-neon-blue'
          : step.color === 'deepblue' ? 'text-neon-deep'
          : step.color === 'purple' ? 'text-neon-purple'
          : 'text-neon-pink'
        } text-lg mb-3 text-center uppercase tracking-wide`}
        style={{ borderBottom: `1px solid ${colorHex}`, paddingBottom: 6 }}
        >{step.title}</h2>
        {step.narrative && (
          <p className="text-xs opacity-80 mb-3 text-center">{step.narrative}</p>
        )}

        <div className="space-y-3 mb-5">
          {/* Textarea input */}
          {step.type === "textarea" && (
            <textarea
              className="w-full h-20 glass p-2 text-white text-sm"
              placeholder="Type your query…"
              onBlur={() => addSelection("Query Entry", step.baseCost, step.color)}
            />
          )}

          {/* Radio buttons */}
          {step.type === "radio" && step.options?.map(o => (
            <label key={o.label} className="block text-[11px] leading-tight">
              <input
                type="radio"
                name={`radio-${currentStep}`}
                onChange={() => addSelection(o.label, o.cost, step.color)}
              />{" "}
              {o.icon ? `${o.icon} ` : ""}{o.label}{typeof o.cost === 'number' ? ` ($${o.cost})` : ""}
            </label>
          ))}

          {/* Checkbox steps using OptionCards (limit to six) */}
          {step.type === "checkbox" && step.options && (
            currentStep === 0 ? (
              <OptionCards options={step.options.slice(0,6)} selected={selectedGoals} onToggle={handleGoalToggle} />
            ) : currentStep === 2 ? (
              <OptionCards options={step.options.slice(0,6)} selected={selectedModels} onToggle={handleModelToggle} />
            ) : currentStep === 4 ? (
              <OptionCards options={step.options.slice(0,6)} selected={selectedAddons} onToggle={handleAddonToggle} />
            ) : (
              step.options.slice(0,6).map(o => (
                <label key={o.label} className="block text-[11px] leading-tight">
                  <input
                    type="checkbox"
                    onChange={e => e.target.checked ? addSelection(o.label, o.cost, step.color) : removeSelectionCost(o.cost)}
                  />{" "}
                  {o.icon ? `${o.icon} ` : ""}{o.label}{typeof o.cost === 'number' ? ` ($${o.cost})` : ""}
                </label>
              ))
            )
          )}

          {/* Analysis Modes groupbox */}
          {step.type === "groupbox" && step.options && (
            <AnalysisModes options={step.options as any} selected={selectedAnalysisModes} onToggle={handleAnalysisToggle} />
          )}

          {/* Auto optimize button */}
          {(step.type === 'checkbox' || step.type === 'textarea' || step.type === 'radio') && (
            <button
              className="w-full mt-2 px-3 py-2 glass border-2 rounded text-center hover:shadow-neon-blue"
              style={{ borderColor: colorHex, color: colorHex }}
              onClick={() => addSelection("Auto: Let UltrAI Optimize My Query", 0, step.color)}
            >
              Auto: Let UltrAI Optimize My Query
            </button>
          )}
        </div>

        {/* Navigation buttons */}
        <div className="flex justify-between">
          <button
            disabled={currentStep===0}
            onClick={() => setCurrentStep(currentStep-1)}
            className="px-3 py-2 rounded disabled:opacity-40 border-2 bg-transparent text-sm"
            style={{ borderColor: colorHex, color: colorHex }}
          >
            ← Back
          </button>
          <button
            onClick={() => setCurrentStep(Math.min(currentStep+1, steps.length-1))}
            className="px-3 py-2 rounded animate-pulse-neon border-2 bg-transparent text-sm"
            style={{ borderColor: colorHex, color: colorHex }}
          >
            {currentStep===steps.length-1 ? "Finish" : "Next →"}
          </button>
        </div>
        </div>
      </div>

      {/* Summary Panel */}
      <div className="glass-strong w-[360px] flex-none p-5 rounded-xl border-2 shadow-neon-blue animate-border-hum" style={{ marginTop: '25vh' }}>
        <h2 className="text-lg mb-3 text-center">Itemized Summary</h2>
        {/* Group by color */}
        <div className="space-y-3">
          {['mint','blue','deepblue','purple','pink'].map(groupColor => {
            const items = summary.filter(s => s.color === groupColor);
            if (items.length === 0) return null as any;
            const hex = mapColorHex(groupColor);
            return (
              <div key={groupColor}>
                <div className="uppercase text-[11px] tracking-wider mb-1 text-center" style={{ color: hex }}>{groupColor}</div>
                {items.map((s,i) => (
                  <div key={i} className="text-sm flex items-center">
                    <span className="flex-1" style={{ color: hex }}>{s.label}</span>
                    <span className="px-2 select-none opacity-50">. . . . . . . . . . . . . . .</span>
                    <span className="text-right w-16" style={{ color: hex }}>${s.cost.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            );
          })}
        </div>
        <div className="mt-4 font-bold text-pink-400 text-xl text-neon-pink text-center">
          Total: ${totalCost.toFixed(2)}
        </div>
        {!showStatus && (
          <button
            disabled={currentStep!==steps.length-1}
            className="w-full mt-4 px-4 py-2 glass border-2 shadow-neon-pink rounded animate-flicker text-neon-pink text-sm"
            onClick={() => setShowStatus(true)}
          >
            Proceed – Pay ${totalCost.toFixed(2)}
          </button>
        )}
        {showStatus && (
          <div className="mt-4">
            <StatusUpdater />
          </div>
        )}
      </div>
      </div>
    </div>
  );
}