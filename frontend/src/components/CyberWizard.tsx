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
  const [selectedInputs, setSelectedInputs] = useState<string[]>([]);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [selectedAddons, setSelectedAddons] = useState<string[]>([]);
  const [selectedAnalysisModes, setSelectedAnalysisModes] = useState<string[]>([]);
  const [showStatus, setShowStatus] = useState(0);
  const [stepFadeKey, setStepFadeKey] = useState(0);

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
  const receiptColor = '#bd00ff';

  const handleGoalToggle = (label: string) => {
    const option = step.options?.find(o => o.label === label);
    const cost = option?.cost;
    setSelectedGoals(prev => prev.includes(label) ? (removeSelectionCost(cost), prev.filter(l => l !== label)) : (addSelection(label, cost, step.color), [...prev, label]));
  };
  const handleInputToggle = (label: string) => {
    const option = step.options?.find(o => o.label === label);
    const cost = option?.cost;
    setSelectedInputs(prev => prev.includes(label) ? (removeSelectionCost(cost), prev.filter(l => l !== label)) : (addSelection(label, cost, step.color), [...prev, label]));
  };
  const handleModelToggle = (label: string) => {
    const option = step.options?.find(o => o.label === label);
    const cost = option?.cost;
    setSelectedModels(prev => prev.includes(label) ? (removeSelectionCost(cost), prev.filter(l => l !== label)) : (addSelection(label, cost, step.color), [...prev, label]));
  };
  const handleAddonToggle = (label: string) => {
    const option = step.options?.find(o => o.label === label);
    const cost = option?.cost;
    setSelectedAddons(prev => prev.includes(label) ? (removeSelectionCost(cost), prev.filter(l => l !== label)) : (addSelection(label, cost, step.color), [...prev, label]));
  };
  const handleAnalysisToggle = (label: string) => {
    setSelectedAnalysisModes(prev => prev.includes(label) ? prev.filter(l => l !== label) : [...prev, label]);
  };

  return (
    <div className="relative flex h-screen w-full items-start justify-center p-0 text-white font-cyber text-sm">
      {/* Background layer */}
      <div className="pointer-events-none absolute inset-0" style={{ backgroundImage: "url('/cityscape-background.jpeg')", backgroundSize: 'cover', backgroundPosition: 'center', zIndex: 0 }} />

      {/* Content layer — centered bounded grid */}
      <div className="relative z-10 w-full mx-auto max-w-6xl">
        <div className="grid grid-cols-12 gap-6 items-start" style={{ marginTop: '40vh' }}>
          {/* Site header column (vertical) */}
          <div className="col-start-1 col-span-1 self-start">
            <div className="text-white text-shadow-neon-blue" style={{ writingMode: 'vertical-rl', textOrientation: 'upright', letterSpacing: '0.35em', fontWeight: 800, fontSize: '14px' }}>ULTRAI</div>
          </div>

          {/* Wizard Panel (left) */}
          <div className="col-start-4 col-span-5 self-start">
            <div className={`glass-strong p-4 rounded-2xl transition-all duration-300 h-[42vh] animate-border-hum overflow-hidden ${step.color === "mint" ? "shadow-neon-mint" : step.color === "blue" ? "shadow-neon-blue" : step.color === "deepblue" ? "shadow-neon-deep" : step.color === "purple" ? "shadow-neon-purple" : "shadow-neon-pink"}`} style={{ borderColor: colorHex, borderWidth: 7, background: colorRGBA, boxShadow: `0 0 0 2px rgba(255,255,255,0.10) inset, 0 0 14px ${colorHex}` }}>
              {/* Step markers (centered) */}
              <div className="w-full mb-4">
                <div className="flex items-center justify-center">
                  {steps.map((s, i) => {
                    const isActive = i === currentStep;
                    const isDone = i < currentStep;
                    const dotHex = mapColorHex(s.color);
                    const dotFill = mapColorRGBA(s.color, isActive ? 0.34 : isDone ? 0.2 : 0.1);
                    const shadowClass = s.color === 'mint' ? 'shadow-neon-mint' : s.color === 'blue' ? 'shadow-neon-blue' : s.color === 'deepblue' ? 'shadow-neon-deep' : s.color === 'purple' ? 'shadow-neon-purple' : 'shadow-neon-pink';
                    return (
                      <div key={i} className="flex items-center">
                        <div onClick={() => { setCurrentStep(i); setStepFadeKey(k => k+1); }} className={`rounded-full ${shadowClass} cursor-pointer hover:scale-110 transition-transform`} style={{ width: 24, height: 24, backgroundColor: dotFill, boxShadow: isActive ? `0 0 0 2px #FFD700, 0 0 0 4px ${dotHex}, inset 0 0 8px ${dotHex}` : `0 0 0 1px ${dotHex}`, opacity: isDone || isActive ? 1 : 0.75 }} />
                        {i < steps.length - 1 && (
                          <div className="mx-3 cursor-pointer" onClick={() => { setCurrentStep(i+1); setStepFadeKey(k => k+1); }} style={{ height: 2, width: 56, backgroundColor: i < currentStep ? dotHex : 'rgba(255,255,255,0.3)', boxShadow: i < currentStep ? `0 0 6px ${dotHex}` : undefined }} />
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              <h2 className={`text-white ${step.color === 'mint' ? 'text-shadow-neon-mint' : step.color === 'blue' ? 'text-shadow-neon-blue' : step.color === 'deepblue' ? 'text-shadow-neon-deep' : step.color === 'purple' ? 'text-shadow-neon-purple' : 'text-shadow-neon-pink'} text-base mb-2 text-center uppercase tracking-wide`} style={{ borderBottom: `1px solid ${colorHex}`, paddingBottom: 4 }}>{step.title}</h2>
              {step.narrative && (<p className="text-[11px] text-white opacity-90 mb-2 text-center">{step.narrative}</p>)}

              <div key={stepFadeKey} className="space-y-2 mb-3 animate-fade-in">
                {step.type === "textarea" && (<>
                  <textarea className="w-full h-16 glass p-2 text-white text-sm" placeholder="Type your query…" onBlur={() => addSelection("Query Entry", step.baseCost, step.color)} />
                  {step.options && step.options.map(o => (
                    <label key={o.label} className="block text-[11px] leading-tight truncate opacity-95 hover:opacity-100">
                      <input type="checkbox" onChange={e => e.target.checked ? handleInputToggle(o.label) : handleInputToggle(o.label)} checked={selectedInputs.includes(o.label)} />{" "}
                      <span className="align-middle tracking-wide text-white">{o.icon ? `${o.icon} ` : ""}{o.label}{typeof o.cost === 'number' ? ` ($${o.cost})` : ""}</span>
                    </label>
                  ))}
                </>)}

                {step.type === "radio" && step.options?.map(o => (
                  <label key={o.label} className="block text-[11px] leading-tight truncate opacity-95 hover:opacity-100">
                    <input type="radio" name={`radio-${currentStep}`} onChange={() => addSelection(o.label, o.cost, step.color)} />{" "}
                    <span className="align-middle tracking-wide text-white">{o.icon ? `${o.icon} ` : ""}{o.label}{typeof o.cost === 'number' ? ` ($${o.cost})` : ""}</span>
                  </label>
                ))}

                {step.type === "checkbox" && step.options && (
                  currentStep === 0 ? (
                    <div className="grid grid-cols-2 gap-2">
                      {step.options.map(o => (
                        <label key={o.label} className="flex items-center text-[11px] leading-tight truncate opacity-95 hover:opacity-100">
                          <input type="checkbox" onChange={() => handleGoalToggle(o.label)} checked={selectedGoals.includes(o.label)} />{" "}
                          <span className="align-middle truncate tracking-wide text-white">{o.icon ? `${o.icon} ` : ""}{o.label}</span>
                        </label>
                      ))}
                    </div>
                  ) : currentStep === 2 ? (
                    <div className={step.options.length >= 8 ? "grid grid-cols-2 gap-2" : "space-y-2"}>
                      {step.options.map(o => (
                        <label key={o.label} className="flex items-center text-[11px] leading-tight truncate opacity-95 hover:opacity-100">
                          <input type="checkbox" onChange={() => handleModelToggle(o.label)} checked={selectedModels.includes(o.label)} />{" "}
                          <span className="align-middle truncate tracking-wide text-white">{o.icon ? `${o.icon} ` : ""}{o.label}{typeof o.cost === 'number' ? ` ($${o.cost})` : ""}</span>
                        </label>
                      ))}
                    </div>
                  ) : currentStep === 4 ? (
                    <div className={step.options.length >= 8 ? "grid grid-cols-2 gap-2" : "space-y-2"}>
                      {step.options.map(o => (
                        <label key={o.label} className="flex items-center text-[11px] leading-tight truncate opacity-95 hover:opacity-100">
                          <input type="checkbox" onChange={() => handleAddonToggle(o.label)} checked={selectedAddons.includes(o.label)} />{" "}
                          <span className="align-middle truncate tracking-wide text-white">{o.icon ? `${o.icon} ` : ""}{o.label}{typeof o.cost === 'number' ? ` ($${o.cost})` : ""}</span>
                        </label>
                      ))}
                    </div>
                  ) : (
                    step.options.map(o => (
                      <label key={o.label} className="block text-[11px] leading-tight truncate opacity-95 hover:opacity-100">
                        <input type="checkbox" onChange={e => e.target.checked ? addSelection(o.label, o.cost, step.color) : removeSelectionCost(o.cost)} />{" "}
                        <span className="align-middle tracking-wide text-white">{o.icon ? `${o.icon} ` : ""}{o.label}{typeof o.cost === 'number' ? ` ($${o.cost})` : ""}</span>
                      </label>
                    ))
                  )
                )}

                {step.type === "groupbox" && step.options && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {step.options.map(o => (
                      <div key={o.label} className="glass border-2 rounded-xl p-2 animate-border-hum">
                        <div className="text-center font-bold text-[13px] mb-1 text-white">{o.icon ? `${o.icon} ` : ''}{o.label}</div>
                        {o.description && <div className="text-[11px] text-white/80 text-center leading-snug">{o.description}</div>}
                        {typeof o.cost === 'number' && <div className="text-[11px] text-center mt-1 text-pink-400">+${o.cost.toFixed(2)}</div>}
                      </div>
                    ))}
                  </div>
                )}

                {(step.type === 'checkbox' || step.type === 'textarea' || step.type === 'radio') && currentStep !== 4 && currentStep !== 0 && (
                  <button className="w-full mt-2 px-3 py-2 rounded text-center font-semibold shadow-neon-mint animate-border-hum" style={{ border: '2px solid #00ff9f', color: '#00ff9f', background: 'rgba(0,255,159,0.08)' }} onClick={() => addSelection("Auto: Let UltrAI Optimize My Query", 0, step.color)}>
                    Auto: Let UltrAI Optimize My Query
                  </button>
                )}

                <button className="w-full mt-2 px-3 py-2 rounded text-center font-semibold animate-border-hum" style={{ border: `2px solid ${colorHex}`, color: colorHex, background: mapColorRGBA(step.color, 0.06) }} onClick={() => { setCurrentStep(Math.min(currentStep+1, steps.length-1)); setStepFadeKey(k => k+1); }}>
                  {currentStep===steps.length-1 ? "Finish" : "Submit"}
                </button>
              </div>
            </div>
          </div>

          {/* Receipt Panel (right) */}
          <div className="glass-strong col-start-9 col-span-3 p-3 rounded-xl animate-border-hum self-start" style={{ fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace', border: '7px solid', borderColor: receiptColor as any, boxShadow: `0 0 0 2px rgba(255,255,255,0.08) inset, 0 0 14px ${receiptColor}` }}>
            <div className="text-center mb-2">
              <div className="text-[14px] font-extrabold tracking-[0.35em] text-white text-shadow-neon-blue">ULTRAI</div>
              <div className="text-[10px] text-white/70">— ITEMIZED RECEIPT —</div>
            </div>
            <div className="space-y-2">
              {['mint','blue','deepblue','purple','pink'].map(groupColor => {
                const items = summary.filter(s => s.color === groupColor);
                if (items.length === 0) return null as any;
                const hex = mapColorHex(groupColor);
                return (
                  <div key={groupColor}>
                    <div className="uppercase text-[10px] tracking-wider mb-1 text-center" style={{ color: hex }}>{groupColor}</div>
                    {items.map((s,i) => (
                      <div key={i} className="text-[10px] leading-tight flex items-center">
                        <span className="flex-auto overflow-hidden text-ellipsis whitespace-nowrap" style={{ color: hex }}>{s.label}</span>
                        <span className="px-1 select-none opacity-50">. . . . . . . . . . .</span>
                        <span className="text-right w-14" style={{ color: hex }}>${s.cost.toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                );
              })}
            </div>
            <div className="mt-3 font-bold text-pink-400 text-lg text-neon-pink text-center">Total: ${totalCost.toFixed(2)}</div>
          </div>
        </div>

        {/* Under-main: commence and status below main window */}
        <div className="grid grid-cols-12 gap-6" style={{ marginTop: '8px' }}>
          <div className="col-start-4 col-span-5">
            {currentStep===steps.length-1 && !showStatus && (
              <div className="animate-fade-in">
                <button className="w-full px-4 py-3 rounded text-center font-bold animate-pulse-neon" style={{ border: '3px solid #00ff9f', color: '#001', background: 'rgba(0,255,159,0.2)', textShadow: '0 0 8px #00ff9f' }} onClick={() => setShowStatus(true)}>
                  Commence UltraAI
                </button>
              </div>
            )}
            {showStatus && (
              <div className="glass-strong p-3 rounded-xl border-2 animate-border-hum mt-2" style={{ borderColor: colorHex, boxShadow: `0 0 0 2px rgba(255,255,255,0.08) inset, 0 0 14px ${colorHex}` }}>
                <StatusUpdater />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}