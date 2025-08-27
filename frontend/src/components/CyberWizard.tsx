"use client";
import { useEffect, useState } from "react";
import LineOverlay from "./LineOverlay";

interface StepOption { label: string; cost?: number; icon?: string; description?: string }
interface Step {
  title: string;
  color: string;
  type: string;
  narrative?: string;
  options?: StepOption[];
  baseCost?: number;
}

export default function CyberWizard() {
  const [steps, setSteps] = useState<Step[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [summary, setSummary] = useState<string[]>([]);
  const [totalCost, setTotalCost] = useState(0);

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

  const addSelection = (label: string, cost?: number) => {
    const appliedCost = typeof cost === 'number' ? cost : 0;
    setSummary(prev => [...prev, `${label}: $${appliedCost.toFixed(2)}`]);
    setTotalCost(prev => prev + appliedCost);
  };

  if (steps.length === 0) return <div>Loading…</div>;

  const step = steps[currentStep];
  const colorHex = step.color === 'mint' ? '#00ff9f'
    : step.color === 'blue' ? '#00b8ff'
    : step.color === 'deepblue' ? '#001eff'
    : step.color === 'purple' ? '#bd00ff'
    : '#d600ff';
  const colorRGBA = step.color === 'mint' ? 'rgba(0,255,159,0.08)'
    : step.color === 'blue' ? 'rgba(0,184,255,0.08)'
    : step.color === 'deepblue' ? 'rgba(0,30,255,0.08)'
    : step.color === 'purple' ? 'rgba(189,0,255,0.08)'
    : 'rgba(214,0,255,0.08)';

  return (
    <div className="relative flex h-screen w-full items-center justify-center gap-10 p-8 text-white font-cyber"
    >
      {/* Parallax layers */}
      <div className="pointer-events-none absolute inset-0 animate-parallax-slow"
           style={{ backgroundImage: "url('/cityscape-background.jpeg')", backgroundSize: 'cover', backgroundPosition: 'center', zIndex: 0 }} />
      {/* Replace bitmap overlay with inline SVG overlay for targeted animations */}
      <LineOverlay />
      {/* Content layer */}
      <div className="relative z-10 flex items-start justify-center gap-10 w-full">
      {/* Wizard Panel (left), smaller, more transparent, border/lines-focused */}
      <div className="w-[520px] flex-none" style={{ marginTop: '25vh' }}>
        <div
          className={`glass-strong p-7 rounded-2xl transition-all duration-300 min-h-[56vh]
            ${step.color === "mint" ? "shadow-neon-mint"
            : step.color === "blue" ? "shadow-neon-blue"
            : step.color === "deepblue" ? "shadow-neon-deep"
            : step.color === "purple" ? "shadow-neon-purple"
            : "shadow-neon-pink"}`}
          style={{ borderColor: colorHex, borderWidth: 9, background: colorRGBA, boxShadow: `0 0 0 2px rgba(255,255,255,0.1) inset, 0 0 20px ${colorHex}` }}
        >
        {/* Step markers with connecting lines (labels removed) */}
        <div className="w-full mb-6">
          <div className="flex items-center">
            {steps.map((s, i) => {
              const isActive = i === currentStep;
              const isDone = i < currentStep;
              const colorHex = s.color === 'mint' ? '#00ff9f'
                : s.color === 'blue' ? '#00b8ff'
                : s.color === 'deepblue' ? '#001eff'
                : s.color === 'purple' ? '#bd00ff'
                : '#d600ff';
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
                      width: 28,
                      height: 28,
                      backgroundColor: 'transparent',
                      boxShadow: isActive ? `0 0 0 2px ${colorHex}, inset 0 0 10px ${colorHex}` : `0 0 0 1px ${colorHex}`,
                      opacity: isDone || isActive ? 1 : 0.5
                    }}
                  />
                  {i < steps.length - 1 && (
                    <div
                      className="mx-2"
                      style={{
                        height: 2,
                        backgroundColor: i < currentStep ? colorHex : 'rgba(255,255,255,0.25)',
                        boxShadow: i < currentStep ? `0 0 8px ${colorHex}` : undefined,
                        flexGrow: 1
                      }}
                    />
                  )}
                </div>
              );
            })}
          </div>
          {/* labels intentionally removed per request */}
        </div>

        <h2 className={`text-2xl mb-2 text-center ${
          step.color === 'mint' ? 'text-neon-mint'
          : step.color === 'blue' ? 'text-neon-blue'
          : step.color === 'deepblue' ? 'text-neon-deep'
          : step.color === 'purple' ? 'text-neon-purple'
          : 'text-neon-pink'
        } uppercase tracking-wide`}
        style={{ borderBottom: `1px solid ${step.color === 'mint' ? '#00ff9f' : step.color === 'blue' ? '#00b8ff' : step.color === 'deepblue' ? '#001eff' : step.color === 'purple' ? '#bd00ff' : '#d600ff'}`, paddingBottom: 8 }}
        >{step.title}</h2>
        {step.narrative && (
          <p className="text-sm opacity-80 mb-4 text-center">{step.narrative}</p>
        )}

        <div className="space-y-3 mb-6">
          {/* Textarea input */}
          {step.type === "textarea" && (
            <textarea
              className="w-full h-24 glass p-2 text-white"
              placeholder="Type your query…"
              onBlur={() => step.baseCost && addSelection("Query Entry", step.baseCost)}
            />
          )}

          {/* Radio buttons */}
          {step.type === "radio" && step.options?.map(o => (
            <label key={o.label} className="block">
              <input
                type="radio"
                name={`radio-${currentStep}`}
                onChange={() => addSelection(o.label, o.cost)}
              />{" "}
              {o.icon ? `${o.icon} ` : ""}{o.label}{typeof o.cost === 'number' ? ` ($${o.cost})` : ""}
            </label>
          ))}

          {/* Checkboxes and groupboxes */}
          {(step.type === "checkbox" || step.type === "groupbox") && step.options?.map(o => (
            <label key={o.label} className="block">
              <input
                type="checkbox"
                onChange={e => e.target.checked && addSelection(o.label, o.cost)}
              />{" "}
              {o.icon ? `${o.icon} ` : ""}{o.label}{typeof o.cost === 'number' ? ` ($${o.cost})` : ""}
              {o.description ? <span className="block text-xs opacity-75 ml-6">{o.description}</span> : null}
            </label>
          ))}
        </div>

        {/* Navigation buttons */}
        <div className="flex justify-between">
          <button
            disabled={currentStep===0}
            onClick={() => setCurrentStep(currentStep-1)}
            className="px-4 py-2 rounded disabled:opacity-40 border-2 bg-transparent"
            style={{ borderColor: (step.color === 'mint' ? '#00ff9f' : step.color === 'blue' ? '#00b8ff' : step.color === 'deepblue' ? '#001eff' : step.color === 'purple' ? '#bd00ff' : '#d600ff'), color: (step.color === 'mint' ? '#00ff9f' : step.color === 'blue' ? '#00b8ff' : step.color === 'deepblue' ? '#001eff' : step.color === 'purple' ? '#bd00ff' : '#d600ff') }}
          >
            ← Back
          </button>
          <button
            onClick={() => setCurrentStep(Math.min(currentStep+1, steps.length-1))}
            className="px-4 py-2 rounded animate-pulse-neon border-2 bg-transparent"
            style={{ borderColor: (step.color === 'mint' ? '#00ff9f' : step.color === 'blue' ? '#00b8ff' : step.color === 'deepblue' ? '#001eff' : step.color === 'purple' ? '#bd00ff' : '#d600ff'), color: (step.color === 'mint' ? '#00ff9f' : step.color === 'blue' ? '#00b8ff' : step.color === 'deepblue' ? '#001eff' : step.color === 'purple' ? '#bd00ff' : '#d600ff') }}
          >
            {currentStep===steps.length-1 ? "Finish" : "Next →"}
          </button>
        </div>
        </div>
      </div>

      {/* Summary Panel */}
      <div className="glass-strong w-[420px] flex-none p-6 rounded-xl border-2 shadow-neon-blue" style={{ marginTop: '25vh' }}>
        <h2 className="text-xl mb-4">Itemized Summary</h2>
        {summary.map((s,i) => <div key={i}>{s}</div>)}
        <div className="mt-4 font-bold text-pink-400 text-2xl text-neon-pink">
          Total: ${totalCost.toFixed(2)}
        </div>
        <button
          disabled={currentStep!==steps.length-1}
          className="w-full mt-4 px-4 py-3 glass border-2 shadow-neon-pink rounded animate-flicker text-neon-pink"
        >
          Proceed – Pay ${totalCost.toFixed(2)}
        </button>
      </div>
      </div>
    </div>
  );
}