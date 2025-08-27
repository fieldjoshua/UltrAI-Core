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
    <div className={`glass-strong rounded-xl p-4 border-2 animate-border-hum ${animClass}`}>
      <div className="flex items-center gap-3">
        <div className="text-xl">{s.icon}</div>
        <h3 className="text-sm font-bold tracking-wide uppercase">{s.title}</h3>
      </div>
      {s.narrative && <p className="text-xs opacity-80 mt-1">{s.narrative}</p>}
      {s.substeps && (
        <div className="mt-2 space-y-1">
          {s.substeps.map((ss) => (
            <div key={ss.label} className="flex justify-between text-xs">
              <span className="opacity-80">{ss.label}</span>
              <span className="text-neon-mint">{ss.status}</span>
            </div>
          ))}
        </div>
      )}
      {s.animation === 'progress-bar' && (
        <div className="mt-3 h-1 bg-white/10 rounded overflow-hidden">
          <div className="h-full bg-pink-400 animate-[progressFill_1.5s_ease-in-out_forwards]"></div>
        </div>
      )}
      {s.tabs && (
        <div className="mt-3 flex flex-wrap gap-2">
          {s.tabs.map(tab => (
            <span key={tab} className="px-2 py-1 text-[11px] border rounded border-white/20">{tab}</span>
          ))}
        </div>
      )}
    </div>
  );
}
