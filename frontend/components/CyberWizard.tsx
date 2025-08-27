"use client";
import React, { useEffect, useState } from "react";

interface Step {
  title: string;
  color: string;
  type: string;
  options?: { label: string; cost: number }[];
  baseCost?: number;
}

export default function CyberWizard() {
  const [steps, setSteps] = useState<Step[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [summary, setSummary] = useState<string[]>([]);
  const [totalCost, setTotalCost] = useState(0);

  useEffect(() => {
    fetch("/steps.json").then(r => r.json()).then(setSteps);
  }, []);

  const addSelection = (label: string, cost: number) => {
    setSummary(prev => [...prev, `${label}: $${cost.toFixed(2)}`]);
    setTotalCost(prev => prev + cost);
  };

  if (steps.length === 0) return <div>Loading…</div>;

  const step = steps[currentStep];

  return (
    <div className="flex h-screen w-full bg-[url('/cityscape-background.jpeg')] bg-cover bg-center items-center justify-center gap-8 p-8 text-white font-cyber">
      {/* Wizard Panel */}
      <div
        className={`glass flex-1 p-6 rounded-xl border-2 transition-all duration-500
          ${step.color === "mint" ? "shadow-neon-mint"
          : step.color === "blue" ? "shadow-neon-blue"
          : step.color === "deepblue" ? "shadow-neon-deep"
          : step.color === "purple" ? "shadow-neon-purple"
          : "shadow-neon-pink"}`}
      >
        {/* Progress bar */}
        <div className="h-2 w-full bg-white/10 rounded mb-6 overflow-hidden">
          <div
            className="h-full bg-cyber-gradient transition-all duration-500"
            style={{ width: `${((currentStep+1)/steps.length)*100}%` }}
          />
        </div>

        <h2 className="text-2xl mb-4 animate-flicker">{step.title}</h2>

        <div className="space-y-3 mb-6">
          {step.type === "textarea" && (
            <textarea
              className="w-full h-24 glass p-2 text-white"
              placeholder="Type your query…"
              onBlur={() => step.baseCost && addSelection("Query Entry", step.baseCost)}
            />
          )}
          {step.type === "radio" && step.options?.map(o => (
            <label key={o.label} className="block">
              <input type="radio" name="choice" onChange={() => addSelection(o.label, o.cost)} /> {o.label} (${o.cost})
            </label>
          ))}
          {step.type === "checkbox" && step.options?.map(o => (
            <label key={o.label} className="block">
              <input type="checkbox" onChange={e => e.target.checked && addSelection(o.label, o.cost)} /> {o.label} (${o.cost})
            </label>
          ))}
        </div>

        <div className="flex justify-between">
          <button
            disabled={currentStep===0}
            onClick={() => setCurrentStep(currentStep-1)}
            className="px-4 py-2 glass rounded disabled:opacity-40"
          >
            ← Back
          </button>
          <button
            onClick={() => setCurrentStep(currentStep+1)}
            className="px-4 py-2 glass rounded animate-pulse-neon"
          >
            {currentStep===steps.length-1 ? "Finish" : "Next →"}
          </button>
        </div>
      </div>

      {/* Summary Panel */}
      <div className="glass w-1/3 p-6 rounded-xl border-2 shadow-neon-blue">
        <h2 className="text-xl mb-4">Itemized Summary</h2>
        {summary.map((s,i) => <div key={i}>{s}</div>)}
        <div className="mt-4 font-bold text-pink-400 text-2xl">Total: ${totalCost.toFixed(2)}</div>
        <button
          disabled={currentStep!==steps.length-1}
          className="w-full mt-4 px-4 py-3 glass border-2 shadow-neon-pink rounded animate-flicker"
        >
          Proceed – Pay ${totalCost.toFixed(2)}
        </button>
      </div>
    </div>
  );
}