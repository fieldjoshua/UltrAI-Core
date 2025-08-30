import { useEffect, useState } from "react";

interface Substep { label: string; status: string }
interface StatusStep {
  title: string;
  icon?: string;
  narrative?: string;
  substeps?: Substep[];
  animation?: "fade-in" | "spinner" | "typing-dots" | "flicker" | "gear-spin" | "progress-bar" | "glow-pulse";
  panel?: string;
  tabs?: string[];
}

export default function StatusUpdater() {
  const [steps, setSteps] = useState<StatusStep[]>([]);
  const [idx, setIdx] = useState(0);

  useEffect(() => {
    const load = async () => {
      try {
        const r = await fetch('/status_steps.json', { cache: 'no-store' });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const d = await r.json();
        setSteps(d as StatusStep[]);
      } catch (e) {
        console.error('Failed to load status steps', e);
      }
    };
    load();
  }, []);

  useEffect(() => {
    if (steps.length === 0) return;
    const t = setTimeout(() => setIdx(i => Math.min(i + 1, steps.length - 1)), 1500);
    return () => clearTimeout(t);
  }, [steps, idx]);

  if (steps.length === 0) return null;
  const s = steps[idx];

  const animClass = s.animation === 'spinner' ? 'animate-spin-slow'
    : s.animation === 'typing-dots' ? 'after:content-["…"] after:animate-pulse'
    : s.animation === 'flicker' ? 'animate-flicker'
    : s.animation === 'gear-spin' ? 'animate-spin'
    : s.animation === 'progress-bar' ? 'relative overflow-hidden'
    : s.animation === 'glow-pulse' ? 'animate-pulse-neon'
    : 'animate-fade-in';

  return (
    <div className={`glass-strong rounded-xl p-6 border-2 animate-border-hum ${animClass} relative overflow-hidden`}>
      {/* Background accent glow */}
      <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-transparent to-orange-500/5 pointer-events-none" />
      
      {/* Content centered */}
      <div className="relative z-10 text-center">
        {/* Icon with glow effect */}
        <div className="text-3xl mb-3 inline-block">
          <span className="inline-block animate-bounce-subtle drop-shadow-[0_0_20px_rgba(255,102,0,0.6)]">
            {s.icon}
          </span>
        </div>
        
        {/* Title with gradient text */}
        <h3 className="text-lg font-bold tracking-wider uppercase bg-gradient-to-r from-cyan-400 to-orange-400 bg-clip-text text-transparent">
          {s.title}
        </h3>
        
        {/* Narrative with better spacing */}
        {s.narrative && (
          <p className="text-sm opacity-90 mt-3 max-w-md mx-auto leading-relaxed text-white/80">
            {s.narrative}
          </p>
        )}
        
        {/* Substeps as centered cards */}
        {s.substeps && (
          <div className="mt-4 grid grid-cols-2 gap-2 max-w-sm mx-auto">
            {s.substeps.map((ss) => (
              <div key={ss.label} className="bg-white/5 rounded-lg p-2 border border-white/10">
                <span className="text-xs opacity-70 block">{ss.label}</span>
                <span className="text-sm font-semibold text-cyan-400">{ss.status}</span>
              </div>
            ))}
          </div>
        )}
        
        {/* Enhanced progress bar */}
        {s.animation === 'progress-bar' && (
          <div className="mt-4 max-w-xs mx-auto">
            <div className="h-2 bg-white/10 rounded-full overflow-hidden backdrop-blur-sm">
              <div className="h-full bg-gradient-to-r from-cyan-400 to-orange-400 animate-[progressFill_1.5s_ease-in-out_forwards] shadow-[0_0_10px_rgba(255,102,0,0.5)]"></div>
            </div>
          </div>
        )}
        
        {/* Tabs as pills */}
        {s.tabs && (
          <div className="mt-4 flex flex-wrap gap-2 justify-center">
            {s.tabs.map(tab => (
              <span key={tab} className="px-3 py-1.5 text-xs font-medium border rounded-full border-white/20 bg-white/5 hover:bg-white/10 transition-colors">
                {tab}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
