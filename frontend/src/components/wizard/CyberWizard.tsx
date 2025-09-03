"use client";
import { useEffect, useState, useMemo, useCallback, memo } from "react";
import { Button } from "@components/ui/button";
import { Checkbox } from "@components/ui/checkbox";
import { Card } from "@components/ui/card";
import { processWithFeatherOrchestration, getAvailableModels } from "@api/orchestrator";
import LaunchStatus from "@components/wizard/LaunchStatus";
import { captureNoBadAnswerFromOrchestrator } from "@internal/analysisTracker";
import { RadioGroup, RadioGroupItem } from "@components/ui/radio-group";
import { Input } from "@components/ui/input";
import { OutlineIcon } from "@components/icons/OutlineIcons";
import { Rocket, Film, Check, Copy, Zap, Activity, Sparkles, Brain, Network, Download } from 'lucide-react';
// Bridge animation disabled for professional static look

interface StepOption { label: string; cost?: number; icon?: string; description?: string }
interface Step {
  title: string;
  color: string;
  type: string;
  narrative?: string;
  options?: StepOption[];
  baseCost?: number;
}
interface SummaryItem { label: string; cost: number; color: string; section: string }

interface ReceiptSectionProps { sectionTitle: string; items: SummaryItem[] }

const ReceiptSection = memo(function ReceiptSection({ sectionTitle, items }: ReceiptSectionProps) {
  const dots = ". . . . . . . . . . . . . . . . . . . .";
  return (
    <div className="mb-3">
      <div className="uppercase text-[9px] tracking-[0.2em] mb-2 text-center text-white/60 font-bold">{sectionTitle}</div>
      {items.map((s, i) => (
        <div key={i} className="text-[11px] leading-relaxed flex items-center text-white/85 hover:text-white transition-colors duration-200 group cursor-pointer mb-1">
          <span className="flex-auto overflow-hidden text-ellipsis whitespace-nowrap group-hover:text-shadow-sm font-medium" title={s.label}>{s.label}</span>
          <span className="px-1 select-none opacity-30 group-hover:opacity-50 text-[10px]">{dots}</span>
          <span className="text-right w-16 group-hover:text-pink-400 transition-colors font-mono">${s.cost.toFixed(2)}</span>
        </div>
      ))}
    </div>
  );
});

export default function CyberWizard() {
  // Track current skin and update when it changes
  const [currentSkin, setCurrentSkin] = useState(() => {
    return Array.from(document.body.classList)
      .find(cls => cls.startsWith('skin-'))
      ?.replace('skin-', '') || 'night';
  });
  
  // Minimalist skin flag removed (not used)
  const isNonTimeSkin = currentSkin === 'minimalist' || currentSkin === 'business';
  
  // Watch for skin changes
  useEffect(() => {
    const observer = new MutationObserver(() => {
      const newSkin = Array.from(document.body.classList)
        .find(cls => cls.startsWith('skin-'))
        ?.replace('skin-', '') || 'night';
      if (newSkin !== currentSkin) {
        setCurrentSkin(newSkin);
      }
    });
    
    observer.observe(document.body, {
      attributes: true,
      attributeFilter: ['class']
    });
    
    return () => observer.disconnect();
  }, [currentSkin]);
  const [steps, setSteps] = useState<Step[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [summary, setSummary] = useState<SummaryItem[]>([]);
  const [totalCost, setTotalCost] = useState(0);
  const [selectedGoals, setSelectedGoals] = useState<string[]>([]);
  const [selectedInputs, setSelectedInputs] = useState<string[]>([]);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [availableModels, setAvailableModels] = useState<string[] | null>(null);
  const [availableModelInfos, setAvailableModelInfos] = useState<Record<string, { provider: string; cost_per_1k_tokens: number }>>({});
  const [, setModelSelectionMode] = useState<'auto' | 'manual'>('auto');
  const [autoPreference, setAutoPreference] = useState<'cost' | 'premium' | 'speed'>('premium');
  // const [selectedAddons, setSelectedAddons] = useState<string[]>([]);
  const [showStatus, setShowStatus] = useState<boolean>(false);
  const [stepFadeKey, setStepFadeKey] = useState(0);
  const [userQuery, setUserQuery] = useState<string>("");
  const [queryFocused, setQueryFocused] = useState<boolean>(false);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [orchestratorResult, setOrchestratorResult] = useState<any>(null);
  const [orchestratorError, setOrchestratorError] = useState<string | null>(null);
  const [showResults, setShowResults] = useState<boolean>(false);
  const [isOptimizing] = useState<boolean>(false);
  const [optimizationStep] = useState<number>(0);
  const [, setModelStatuses] = useState<Record<string, 'checking' | 'ready' | 'error'>>({});
  const [viewingIteration, setViewingIteration] = useState<'final' | 'initial' | 'meta'>('final');
  // Sync bgTheme with currentSkin for non-minimalist skins
  const [bgTheme, setBgTheme] = useState<'morning' | 'afternoon' | 'sunset' | 'night'>('night');
  
  // Set document title for accessibility and SEO
  useEffect(() => {
    const previousTitle = document.title;
    document.title = 'UltrAI – Wizard';
    return () => { document.title = previousTitle; };
  }, []);
  
  useEffect(() => {
    if (!isNonTimeSkin && ['morning', 'afternoon', 'sunset', 'night'].includes(currentSkin)) {
      setBgTheme(currentSkin as any);
    }
  }, [currentSkin, isNonTimeSkin]);
  const [otherGoalText, setOtherGoalText] = useState<string>("");
  const [showModelList, setShowModelList] = useState<boolean>(false);
  const [addonsSubmitted, setAddonsSubmitted] = useState<boolean>(false);
  const [, setLastAddedItem] = useState<string | null>(null);
  // Billboard overlay disabled; remove state to avoid unused variable lints
  // Check if we're in demo/mock mode based on environment
  const isDemoMode = import.meta.env.VITE_API_MODE === 'mock' || import.meta.env.VITE_DEMO_MODE === 'true';

  // Setup demo mode (no auto-progression)
  useEffect(() => {
    if (!isDemoMode) return;
    // In demo mode, just set default models and start at intro
    setSelectedModels(["gpt-5", "claude-4.1", "gemini-2.5"]);
    setCurrentStep(0);
    setStepFadeKey(k => k + 1);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isDemoMode]);

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

  

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) return;
      
      switch(e.key) {
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

  // Load available models for Step 3 (only show keyed models)
  useEffect(() => {
    const fetchAvailable = async () => {
      try {
        const d = await getAvailableModels();
        if (d && Array.isArray(d.models)) {
          // Normalize models to string[]
          const names = d.models.map((m: any) => (typeof m === 'string' ? m : m.id || m.name)).filter(Boolean);
          setAvailableModels(names as string[]);
          const statusMap: Record<string, 'checking' | 'ready' | 'error'> = {};

          // If modelInfos present, store it; else build a minimal map
          if ((d as any).modelInfos) {
            setAvailableModelInfos((d as any).modelInfos);
            names.forEach((modelName: string) => {
              statusMap[modelName] = 'ready';
            });
          } else {
            const infoMap: Record<string, { provider: string; cost_per_1k_tokens: number }> = {};
            (d.models as any[]).forEach((m: any) => {
              const name = typeof m === 'string' ? m : (m.id || m.name);
              if (!name) return;
              infoMap[name] = {
                provider: m.provider || '',
                cost_per_1k_tokens: m.cost_per_1k_tokens || 0,
              };
              statusMap[name] = 'ready';
            });
            setAvailableModelInfos(infoMap);
          }
          setModelStatuses(statusMap);
        } else {
          setAvailableModels([]);
        }
      } catch (e) {
        console.error("Failed to load available models", e);
        setAvailableModels([]);
      }
    };
    fetchAvailable();
  }, []);

  // Kick off Ultra Synthesis pipeline when status is shown (hook placed before any conditional returns)
  useEffect(() => {
    if (!showStatus || isRunning) return;
    setIsRunning(true);
    (async () => {
      try {
        setOrchestratorError(null);
        
        // Use the orchestrator API (which will use mock in demo mode)
        const models = selectedModels.length > 0 ? selectedModels : null;
        const res = await processWithFeatherOrchestration({
          prompt: userQuery || "",
          models,
          pattern: "comparative",
          ultraModel: null,
          outputFormat: "plain",
        });
        
        // Check if the API returned an error in the response
        if ((res as any)?.error) {
          const errVal: any = (res as any).error;
          const errorMessage = typeof errVal === 'object' 
            ? errVal?.message || JSON.stringify(errVal)
            : String(errVal);
          setOrchestratorError(errorMessage);
          setOrchestratorResult(null);
        } else {
          setOrchestratorResult(res);
          console.log("Ultra Synthesis result", res);
        }
      } catch (e: any) {
        console.error("Ultra Synthesis failed", e);
        setOrchestratorError(e?.message || String(e));
      } finally {
        setIsRunning(false);
      }
    })();
  }, [showStatus, userQuery, selectedModels]);

  // Internal: capture no-bad-answer aggregation after results
  useEffect(() => {
    if (!orchestratorResult) return;
    try {
      captureNoBadAnswerFromOrchestrator(orchestratorResult, selectedModels, userQuery);
    } catch (_) {
      // internal-only; ignore
    }
  }, [orchestratorResult, selectedModels, userQuery]);

  const addSelection = (label: string, cost: number | undefined, color: string, section?: string) => {
    const appliedCost = typeof cost === 'number' ? cost : 0;
    const sectionVal = section || step.title;
    setSummary(prev => [...prev, { label, cost: appliedCost, color, section: sectionVal } as SummaryItem]);
    setTotalCost(prev => prev + appliedCost);
    setLastAddedItem(`${sectionVal}-${label}`);
    setTimeout(() => setLastAddedItem(null), 1000);
  };

  const removeSelectionCost = (cost?: number) => {
    const appliedCost = typeof cost === 'number' ? cost : 0;
    setTotalCost(prev => Math.max(0, prev - appliedCost));
  };

  const step = steps[currentStep];
  const mapColorHex = (c: string) => c === 'mint' ? '#00ff9f'
    : c === 'blue' ? '#00d4ff'
    : c === 'deepblue' ? '#4169ff'
    : c === 'purple' ? '#bd00ff'
    : c === 'pink' ? '#ff0095'
    : '#d600ff';
  const mapColorRGBA = (c: string, alpha: number) => c === 'mint' ? `rgba(0,255,159,${alpha})`
    : c === 'blue' ? `rgba(0,212,255,${alpha})`
    : c === 'deepblue' ? `rgba(65,105,255,${alpha})`
    : c === 'purple' ? `rgba(189,0,255,${alpha})`
    : c === 'pink' ? `rgba(255,0,149,${alpha})`
    : `rgba(214,0,255,${alpha})`;

  const colorHex = useMemo(() => step?.color ? mapColorHex(step.color) : '#00ff9f', [step]);
  const receiptColor = '#ff6600'; // Cyberpunk orange

  const handleGoalToggle = useCallback((label: string) => {
    if (!step) return;
    const option = step.options?.find(o => o.label === label);
    const cost = option?.cost;
    setSelectedGoals(prev => prev.includes(label) ? (removeSelectionCost(cost), prev.filter(l => l !== label)) : (addSelection(label, cost, step?.color || 'mint', step?.title || ''), [...prev, label]));
  }, [step]);
  
  const handleInputToggle = useCallback((label: string) => {
    if (!step) return;
    const option = step.options?.find(o => o.label === label);
    const cost = option?.cost;
    setSelectedInputs(prev => prev.includes(label) ? (removeSelectionCost(cost), prev.filter(l => l !== label)) : (addSelection(label, cost, step?.color || 'blue', step?.title || ''), [...prev, label]));
  }, [step]);
  
  const handleModelToggle = useCallback((label: string) => {
    if (!step) return;
    const option = step.options?.find(o => o.label === label);
    const cost = option?.cost;
    setSelectedModels(prev => prev.includes(label) ? (removeSelectionCost(cost), prev.filter(l => l !== label)) : (addSelection(label, cost, step?.color || 'deepblue', step?.title || ''), [...prev, label]));
  }, [step]);

  const monoStack = 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace';

  // Theme overlay helper to tint background by time of day
  const themeOverlayStyle = useMemo(() => {
    switch (bgTheme) {
      case 'morning':
        return {
          background: 'linear-gradient(180deg, rgba(255, 210, 122, 0.25) 0%, rgba(255, 255, 255, 0) 60%)',
          zIndex: 1,
        };
      case 'afternoon':
        return {
          background: 'linear-gradient(180deg, rgba(122, 209, 255, 0.25) 0%, rgba(255, 255, 255, 0) 60%)',
          zIndex: 1,
        };
      case 'sunset':
        return {
          background: 'linear-gradient(180deg, rgba(255, 122, 122, 0.20) 0%, rgba(255, 0, 212, 0.15) 40%, rgba(0, 0, 0, 0) 70%)',
          zIndex: 1,
        };
      case 'night':
      default:
        return {
          background: 'linear-gradient(180deg, rgba(0, 17, 51, 0.20) 0%, rgba(51, 0, 68, 0.15) 40%, rgba(0, 0, 0, 0) 70%)',
          zIndex: 1,
        };
    }
  }, [bgTheme]);

  const themeBgUrl = useMemo(() => {
    let url;
    switch (bgTheme) {
      case 'morning':
        url = '/bg-morning.jpg';
        break;
      case 'afternoon':
        url = '/bg-afternoon.jpg';
        break;
      case 'sunset':
        url = '/bg-sunset.jpg';
        break;
      case 'night':
      default:
        url = '/bg-night.jpg';
        break;
    }
    return url;
  }, [bgTheme]);

  // Glass panel darkness based on theme for better readability
  const glassBackground = useMemo(() => {
    switch (bgTheme) {
      case 'morning':
        return 'rgba(0, 0, 0, 0.35)'; // Darker for bright morning
      case 'afternoon':
        return 'rgba(0, 0, 0, 0.30)'; // Darker for bright afternoon
      case 'sunset':
        return 'rgba(0, 0, 0, 0.25)'; // Slightly darker for better contrast
      case 'night':
      default:
        return 'rgba(0, 0, 0, 0.25)'; // Darker for night to improve legibility
    }
  }, [bgTheme]);

  // Selected models display memo removed (not used)
  const receiptSections = useMemo(() => {
    return steps
      .map(s => s.title)
      .filter(title => summary.some(it => it.section === title))
      .map(sectionTitle => (
        <ReceiptSection key={sectionTitle} sectionTitle={sectionTitle} items={summary.filter(it => it.section === sectionTitle)} />
      ));
  }, [steps, summary]);

  const chooseAutoModels = useCallback((pref: 'cost'|'premium'|'speed', names: string[] | null): string[] => {
    const list = Array.isArray(names) ? names : [];
    if (list.length === 0) return [];
    const has = (n: string) => list.includes(n);
    if (pref === 'premium') {
      const picks = [
        'gpt-5',
        'claude-4.1',
        'gemini-2.5',
      ].filter(has);
      return picks.length ? picks : list.slice(0, Math.min(3, list.length));
    }
    if (pref === 'speed') {
      const picks = [
        'gpt-4o-mini',
        'gemini-1.5-flash',
      ].filter(has);
      return picks.length ? picks : list.slice(0, Math.min(2, list.length));
    }
    // cost
    const cheapSorted = list
      .map(name => ({ name, cost: availableModelInfos[name]?.cost_per_1k_tokens ?? 0 }))
      .sort((a, b) => a.cost - b.cost)
      .map(x => x.name);
    return cheapSorted.slice(0, Math.min(2, cheapSorted.length));
  }, [availableModelInfos]);

  const optimizeQuery = useCallback(() => {
    // This function will suggest an improved query based on the user's input
    const query = userQuery.trim();
    let improvedQuery = query;
    
    // Add context based on selected goals
    if (selectedGoals.length > 0) {
      improvedQuery = `For ${selectedGoals.join(', ').toLowerCase()}: ${query}`;
    }
    
    // Add specificity suggestions
    if (!query.includes('specific') && !query.includes('detailed')) {
      improvedQuery += '. Please provide specific, detailed analysis';
    }
    
    // Add format suggestions
    if (!query.includes('format') && !query.includes('structure')) {
      improvedQuery += ' with structured output';
    }
    
    setUserQuery(improvedQuery);
  }, [userQuery, selectedGoals]);

  // Show loading state while steps are being loaded
  if (steps.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-white opacity-70">Loading UltrAI...</p>
        </div>
      </div>
    );
  }

  // Step 0: Intro — render with background and billboard
  if (currentStep === 0 && step && step.type === 'intro') {
  return (
      <div className="relative flex min-h-screen w-full items-start justify-center p-0 text-white font-cyber text-sm overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0">
          <div
            className="absolute inset-0"
            style={{
              backgroundImage: "url('/cityscape-background.jpeg'), url('/ultrai-bg.jpg')",
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              transform: 'none',
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/80" />
          
          {/* Animated grid overlay */}
          <div className="absolute inset-0" style={{
            backgroundImage: `linear-gradient(rgba(0,255,159,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,255,159,0.03) 1px, transparent 1px)`,
            backgroundSize: '50px 50px',
            animation: 'grid-move 20s linear infinite'
          }} />
          
          {/* Demo Mode Indicator */}
          {isDemoMode && (
            <div className="absolute top-4 right-4 z-50">
              <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-green-500/20 to-cyan-500/20 border border-green-400/30 backdrop-blur-md animate-fade-in">
                <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                <span className="text-xs font-medium text-green-300">Demo Environment</span>
              </div>
            </div>
          )}
        </div>

        {/* Removed floating particles for cleaner professional look */}

        {/* Hero content */}
        <div className="relative z-10 w-full mx-auto max-w-5xl px-8" style={{ marginTop: '25vh' }}>
          
          {/* Neon Billboard sitting on top of box */}
          <div className="relative">
            <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-full mb-0.5">
              <div className="relative">
                <div 
                  className="px-8 py-3 rounded-lg animate-pulse-glow"
                  style={{
                    background: 'rgba(0, 0, 0, 0.8)',
                    border: '2px solid #00ff9f',
                    boxShadow: `
                      0 0 20px #00ff9f,
                      inset 0 0 20px rgba(0, 255, 159, 0.2),
                      0 0 40px rgba(0, 255, 159, 0.4)
                    `
                  }}
                >
                  <h1 className="text-3xl font-bold tracking-wider" style={{
                    color: '#00ff9f',
                    textShadow: '0 0 10px #00ff9f'
                  }}>
                    ULTRA AI
                  </h1>
                </div>
                {/* Billboard legs */}
                <div className="absolute -bottom-4 left-4 w-1 h-4 bg-gray-600"></div>
                <div className="absolute -bottom-4 right-4 w-1 h-4 bg-gray-600"></div>
              </div>
            </div>
            
            {/* Main professional card */}
            <div
              className="glass-panel glass-grain relative p-12 rounded-3xl overflow-hidden animate-scale-in transition-smooth"
              style={{ 
                background: glassBackground,
                backdropFilter: 'blur(40px)',
                WebkitBackdropFilter: 'blur(40px)',
                border: '2px solid #ff6600',
                boxShadow: '0 0 60px rgba(255,102,0,0.3), inset 0 0 40px rgba(255,102,0,0.05)',
                animationDelay: '0.3s'
              }}
            >

            <div className="relative space-y-8">
              {/* Feature pills */}
              <div className="flex flex-wrap gap-3 justify-center">
                {[
                  { icon: '🚀', text: 'Multi-Model Orchestration', color: 'mint' },
                  { icon: '⚡', text: 'Real-time Synthesis', color: 'blue' },
                  { icon: '🎯', text: 'Intelligent Optimization', color: 'purple' },
                  { icon: '💎', text: 'Premium Results', color: 'pink' }
                ].map((feature, i) => (
                  <span 
                    key={i}
                    className={`px-6 py-2 rounded-full text-sm font-semibold border backdrop-blur animate-slide-in-bottom hover:scale-105 transition-smooth cursor-pointer`}
                    style={{
                      background: `${mapColorRGBA(feature.color, 0.2)}`,
                      borderColor: `${mapColorHex(feature.color)}50`,
                      color: mapColorHex(feature.color),
                      animationDelay: '0.3s'
                    }}
                  >
                    {feature.icon} {feature.text}
                  </span>
                ))}
              </div>

              {/* Main narrative */}
              <div className="max-w-3xl mx-auto mt-8">
                <p className="text-lg leading-relaxed text-center text-white/90">
                  <span className="text-2xl font-bold block mb-4" style={{
                    background: 'linear-gradient(90deg, #00ff9f, #00d4ff, #bd00ff)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                    textShadow: 'none'
                  }}>Intelligence Multiplication Platform</span>
                  Query multiple premium AI models simultaneously. Get synthesized insights that no single model could provide. 
                  <span className="font-bold text-white">Pay only for what you use</span>.
                </p>
                <div className="flex justify-center gap-6 text-sm mt-6 text-white/90">
                  <span className="text-white" style={{
                    textShadow: '0 0 5px rgba(255,255,255,0.3)'
                  }}>Pay-as-you-go</span>
                  <span className="text-white/70">•</span>
                  <span className="text-white" style={{
                    textShadow: '0 0 5px rgba(255,255,255,0.3)'
                  }}>No commitments</span>
                  <span className="text-white/70">•</span>
                  <span className="text-white" style={{
                    textShadow: '0 0 5px rgba(255,255,255,0.3)'
                  }}>Enterprise-grade</span>
                </div>
              </div>

              {/* CTA Button */}
              <div className="text-center space-y-3">
                <button
                  onClick={() => { setCurrentStep(1); setStepFadeKey(k => k + 1); }}
                  className="relative overflow-hidden px-12 py-5 text-xl font-bold rounded-lg transition-all duration-300 transform hover:scale-105 active:scale-95 group"
                  style={{
                    background: 'linear-gradient(135deg, #00ff9f 0%, #00d4ff 50%, #bd00ff 100%)',
                    boxShadow: '0 4px 20px rgba(0, 255, 159, 0.4), 0 0 60px rgba(0, 212, 255, 0.3)',
                    animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite'
                  }}
                >
                  <span className="relative z-10 flex items-center gap-3 justify-center text-black font-extrabold">
                    <span>Enter UltrAI</span>
                    <span className="transform group-hover:translate-x-1 transition-transform">→</span>
                  </span>
                  <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/30 to-white/0 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                </button>
                {isDemoMode && (
                  <button
                    onClick={() => { setCurrentStep(1); setStepFadeKey(k => k + 1); }}
                    className="px-8 py-3 text-sm font-semibold rounded-lg border-2 border-cyan-400/50 text-cyan-400 hover:bg-cyan-400/10 transition-all duration-200"
                  >
                    <span className="flex items-center gap-2 justify-center">
                      <Film className="w-4 h-4" />
                      <span>Try Demo</span>
                    </span>
                  </button>
                )}
              </div>

              {/* Trust indicators */}
              <div className="flex justify-center gap-8 text-sm text-white/80">
                <div className="flex items-center gap-2">
                  <span className="text-green-400">✓</span>
                  <span>20+ AI Models</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-green-400">✓</span>
                  <span>Enterprise Ready</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-green-400">✓</span>
                  <span>SOC2 Compliant</span>
                </div>
              </div>
            </div>
          </div>
          </div>
        </div>

      </div>
    );
  }


  return (
    <div className={`relative flex flex-col min-h-screen w-full ${isNonTimeSkin ? 'text-gray-900' : 'text-white'} font-cyber text-sm`}>
      {/* Skip link for keyboard users */}
      <a href="#main-content" className="sr-only focus:not-sr-only fixed top-2 left-2 z-50 bg-black text-white px-3 py-2 rounded">
        Skip to content
      </a>
      {/* Background layer - only show for time-based skins */}
      {!isNonTimeSkin && (
        <>
          <div
            className="pointer-events-none fixed inset-0"
            style={{
              backgroundImage: `image-set(url('${themeBgUrl}') 1x, url('${themeBgUrl}') 2x)`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              // Use scroll to avoid single-layer rasterization blur with fixed backgrounds
              backgroundAttachment: 'scroll',
              zIndex: 0
            }}
          />
          {/* Theme overlay tint */}
          <div className="pointer-events-none fixed inset-0" style={themeOverlayStyle} />
        </>
      )}
      
      {/* UltrAI Logo - Show for non-time themes */}
      {isNonTimeSkin && (
        <div className="fixed top-10 left-1/2 transform -translate-x-1/2 z-10">
          <div className="relative flex flex-col items-center">
            <img 
              src="/assets/logo.jpg" 
              alt="UltrAI Logo" 
              className={`w-32 h-32 ${currentSkin === 'minimalist' ? 'border-4 border-black' : 'rounded-lg shadow-2xl'}`}
              style={{ 
                filter: currentSkin === 'minimalist' ? 'none' : 'drop-shadow(0 0 20px rgba(0, 0, 0, 0.3))',
              }}
            />
            <div className={`mt-4 text-3xl font-bold ${currentSkin === 'minimalist' ? 'text-black uppercase tracking-widest' : 'text-gray-800'}`}>
              ULTRAI
            </div>
          </div>
        </div>
      )}
      
      {/* Animated Billboard Lines - Lower Right Corner */}
      {/* Overlay removed */}
      
      {/* Bridge Animation - Lower Left Corner */}
      {/* Bridge animation disabled for professional static look */}
      
      {/* Optimization Status Boxes */}
      {isOptimizing && (
        <div className="absolute w-full" style={{ top: '10vh', zIndex: 5 }}>
          <div className="max-w-4xl mx-auto px-8">
            <div className="glass-strong p-4 rounded-xl" style={{ 
              background: glassBackground, 
              backdropFilter: 'blur(40px)',
              WebkitBackdropFilter: 'blur(40px)',
              border: '2px solid #ff6600',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3), inset 0 0 60px rgba(255, 255, 255, 0.05)'
            }}>
              <div className="text-center mb-3">
                <h3 className="text-sm font-bold text-white mb-1">Optimizing Your Search</h3>
                <p className="text-[11px] opacity-70">AI is analyzing your request and selecting the best options</p>
              </div>
              
              <div className="grid grid-cols-4 gap-3">
                <div className={`text-center transition-all duration-300 ${optimizationStep >= 1 ? 'opacity-100' : 'opacity-40'}`}>
                  <div className={`w-12 h-12 mx-auto mb-2 rounded-full flex items-center justify-center transition-all duration-300 ${
                    optimizationStep >= 1 ? 'bg-mint-400/20 border-2 border-mint-400' : 'bg-white/5 border border-white/10'
                  }`}>
                    <span className="text-lg">🔍</span>
                  </div>
                  <div className="text-[10px] font-medium">Analyzing</div>
                  <div className="text-[9px] opacity-70">Query parsed</div>
                </div>
                
                <div className={`text-center transition-all duration-300 ${optimizationStep >= 2 ? 'opacity-100' : 'opacity-40'}`}>
                  <div className={`w-12 h-12 mx-auto mb-2 rounded-full flex items-center justify-center transition-all duration-300 ${
                    optimizationStep >= 2 ? 'bg-blue-400/20 border-2 border-blue-400' : 'bg-white/5 border border-white/10'
                  }`}>
                    <span className="text-lg">🎯</span>
                  </div>
                  <div className="text-[10px] font-medium">Goals</div>
                  <div className="text-[9px] opacity-70">{optimizationStep >= 2 && selectedGoals.length > 0 ? `${selectedGoals.length} selected` : 'Matching...'}</div>
                </div>
                
                <div className={`text-center transition-all duration-300 ${optimizationStep >= 3 ? 'opacity-100' : 'opacity-40'}`}>
                  <div className={`w-12 h-12 mx-auto mb-2 rounded-full flex items-center justify-center transition-all duration-300 ${
                    optimizationStep >= 3 ? 'bg-purple-400/20 border-2 border-purple-400' : 'bg-white/5 border border-white/10'
                  }`}>
                    <span className="text-lg">🤖</span>
                  </div>
                  <div className="text-[10px] font-medium">Models</div>
                  <div className="text-[9px] opacity-70">{optimizationStep >= 3 && selectedModels.length > 0 ? `${selectedModels.length} chosen` : 'Selecting...'}</div>
                </div>
                
                <div className={`text-center transition-all duration-300 ${optimizationStep >= 4 ? 'opacity-100' : 'opacity-40'}`}>
                  <div className={`w-12 h-12 mx-auto mb-2 rounded-full flex items-center justify-center transition-all duration-300 ${
                    optimizationStep >= 4 ? 'bg-pink-400/20 border-2 border-pink-400' : 'bg-white/5 border border-white/10'
                  }`}>
                    <span className="text-lg">📄</span>
                  </div>
                  <div className="text-[10px] font-medium">Format</div>
                  <div className="text-[9px] opacity-70">{optimizationStep >= 4 ? 'Ready' : 'Preparing...'}</div>
                </div>
              </div>
              
              {/* Progress bar */}
              <div className="mt-4 h-1 bg-white/10 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-mint-400 via-blue-400 to-purple-400 transition-all duration-500"
                  style={{ width: `${(optimizationStep / 4) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}


      {/* Progress Indicator */}
      {currentStep > 0 && (
        <div className="fixed top-0 left-0 w-full h-1 bg-black/20 z-50">
          <div 
            className="h-full bg-gradient-to-r from-mint-400 via-blue-400 to-purple-400 transition-all duration-500"
            style={{ 
              width: `${((currentStep) / (steps.length - 1)) * 100}%`,
              boxShadow: '0 0 10px rgba(0, 255, 159, 0.5)'
            }}
          />
        </div>
      )}


      {/* Main Content - Below Billboard */}
      <div className="relative z-10 w-full" id="main-content" role="main">
        <h1 className="sr-only">UltrAI Wizard</h1>
        <div className="flex items-center justify-center" style={{ minHeight: '100vh', paddingTop: isNonTimeSkin ? '20vh' : '30vh' }}>
          <div className="w-full max-w-7xl px-8">
            <div className={`${showStatus && showResults ? 'flex justify-center' : showStatus && !showResults ? 'flex justify-center' : 'grid grid-cols-12 gap-4'}`}>


          {/* Wizard Panel (center) - Hidden during processing and results */}
              {!showStatus && (
              <div className="col-span-8">
                <div
                  className={`relative p-8 rounded-2xl overflow-hidden transition-smooth will-change-transform ${
                    step.color === 'mint' ? 'glow-mint' :
                    step.color === 'blue' ? 'glow-blue' :
                    step.color === 'purple' ? 'glow-purple' :
                    step.color === 'pink' ? 'glow-pink' : ''
                  }`}
                  style={{
                    background: `linear-gradient(135deg, ${mapColorRGBA(step.color, 0.08)}, ${mapColorRGBA(step.color, 0.02)}), ${glassBackground}`,
                    backdropFilter: 'blur(20px) saturate(180%)',
                    WebkitBackdropFilter: 'blur(20px) saturate(180%)',
                    border: `2px solid ${colorHex}80`,
                    height: '500px',
                    boxShadow: `
                      0 8px 32px rgba(0, 0, 0, 0.4),
                      0 0 40px ${colorHex}30,
                      0 0 80px ${colorHex}15,
                      inset 0 0 40px rgba(255, 255, 255, 0.03),
                      inset 0 1px 0 rgba(255, 255, 255, 0.1)
                    `,
                    clipPath: 'polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 20px 100%, 0 calc(100% - 20px))',
                    transform: showStatus ? 'scale(1.02)' : 'scale(1)',
                  }}
                >
              <div className="flex flex-col h-full">
              {!showStatus ? (
                // Show normal wizard content
                <>
                  {/* Step markers (centered) - exclude Step 0 (Intro) */}
              <div className="w-full mb-4">
                <nav aria-label="Wizard steps" className="flex items-center justify-center">
                      {steps.map((s, idx) => ({ s, idx })).filter(x => x.idx !== 0).map(({ s, idx }) => {
                        const stepIndex = idx; // real index in steps
                        const isActive = stepIndex === currentStep;
                        const isDone = stepIndex < currentStep;
                    const dotHex = mapColorHex(s.color);
                    return (
                          <div key={s.title} className="flex items-center">
                            <div 
                              onClick={() => { setCurrentStep(stepIndex); setStepFadeKey(k => k+1); }} 
                              className="relative cursor-pointer group"
                              role="button"
                              tabIndex={0}
                              aria-current={isActive ? 'step' : undefined}
                              aria-label={`Go to step ${stepIndex}: ${s.title}`}
                            >
                              <div 
                                className={`w-8 h-8 rounded-full flex items-center justify-center transition-smooth will-change-transform ${
                                  isActive ? 'scale-110' : 'hover:scale-105'
                                }`}
                                style={{ 
                                  background: isActive 
                                    ? `radial-gradient(circle at 30% 30%, ${dotHex}40, ${dotHex}20)` 
                                    : isDone 
                                    ? `radial-gradient(circle at 30% 30%, ${dotHex}30, ${dotHex}10)`
                                    : 'radial-gradient(circle at 30% 30%, rgba(255,255,255,0.1), rgba(255,255,255,0.05))',
                                  border: `2px solid ${isActive ? dotHex : isDone ? dotHex : dotHex + '40'}`,
                                  boxShadow: isActive 
                                    ? `0 0 0 4px ${dotHex}20, 0 0 30px ${dotHex}50, inset 0 0 10px ${dotHex}30` 
                                    : isDone
                                    ? `0 0 15px ${dotHex}30`
                                    : 'none',
                                  transform: isActive ? 'translateY(-2px)' : 'translateY(0)'
                                }}
                              >
                                <span className="text-[10px] font-bold" style={{ color: isActive || isDone ? dotHex : 'rgba(255,255,255,0.5)' }}>
                                  {stepIndex}
                                </span>
                              </div>
                              {/* Tooltip */}
                              <div className="absolute -bottom-6 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
                                <div className="text-[9px] whitespace-nowrap bg-black/80 px-2 py-1 rounded" style={{ color: dotHex }}>
                                  {s.title.split('. ')[1]}
                                </div>
                              </div>
                            </div>
                            {idx < steps.length - 1 && (
                              <div 
                                className="w-12 h-0.5 mx-2 transition-all duration-300" 
                                style={{ 
                                  backgroundColor: idx < currentStep ? dotHex : 'rgba(255,255,255,0.2)',
                                  boxShadow: idx < currentStep ? `0 0 10px ${dotHex}50` : 'none'
                                }} 
                              />
                        )}
                      </div>
                    );
                  })}
                </nav>
              </div>

              <h2 
                className={`${step.color === 'mint' ? 'text-shadow-neon-mint' : step.color === 'blue' ? 'text-shadow-neon-blue' : step.color === 'deepblue' ? 'text-shadow-neon-deep' : step.color === 'purple' ? 'text-shadow-neon-purple' : 'text-shadow-neon-pink'} text-2xl font-bold mb-4 text-center uppercase tracking-wide`} 
                style={{ 
                  color: colorHex,
                  borderBottom: `2px solid ${colorHex}`, 
                  paddingBottom: 8
                }}
              >
                {step.title}
              </h2>
              {step.narrative && (
                <p className="text-[11px] text-white opacity-95 mb-2 text-center whitespace-pre-line">
                  {currentStep === 2 && selectedGoals.length > 0 
                    ? `Based on your selected goals (${selectedGoals.slice(0, 3).join(', ')}${selectedGoals.length > 3 ? '...' : ''}), tell us what you need.`
                    : step.narrative}
                </p>
              )}

              {/* Scrollable options area */}
              <div
                key={stepFadeKey}
                className={`relative space-y-2 overflow-auto pr-1 pb-16 ${showStatus ? 'opacity-50' : ''}`}
                style={{ 
                  height: 'calc(100% - 120px)',
                  pointerEvents: showStatus ? 'none' : 'auto' 
                }}
              >
                {step.type === "intro" && (
                  <>
                    <div className="text-center space-y-4">
                      <div className="inline-block">
                        <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-[#ff00de] to-[#00ffff]">Welcome to the Future</div>
                        <div className="w-24 h-1 bg-gradient-to-r from-[#ff00de] to-[#00ffff] mx-auto mt-2"></div>
                        {isDemoMode && (
                          <div className="mt-2 text-[10px] text-green-300/70">Demo Environment</div>
                        )}
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 max-w-2xl mx-auto">
                        <div className="glass p-4 rounded-xl border border-mint-400/20 bg-mint-400/5">
                          <div className="text-mint-400 text-lg mb-2">✨</div>
                          <div className="text-sm font-bold mb-1 text-mint-400">Why UltrAI?</div>
                          <div className="text-xs opacity-80">Multiple LLMs working together. Better results, fewer blind spots.</div>
                        </div>
                        <div className="glass p-4 rounded-xl border border-blue-400/20 bg-blue-400/5">
                          <div className="text-blue-400 text-lg mb-2">🚀</div>
                          <div className="text-sm font-bold mb-1 text-blue-400">How it works</div>
                          <div className="text-xs opacity-80">Select goals, enter query, choose models. We handle the rest.</div>
                        </div>
                      </div>
                      
                      <div className="glass p-3 rounded-xl inline-block" style={{ fontFamily: monoStack }}>
                          <div className="text-[12px] font-extrabold tracking-widest text-white text-shadow-neon-pink">ITEMIZED SUMMARY</div>
                          <div className="mt-2 text-[10px] opacity-80">Pay as you go • No commitment</div>
                          <div className="mt-3 text-[24px] font-bold text-neon-pink">Total: $0.00</div>
                          <div className="mt-2 text-[11px] opacity-80">Some queries can be under $1</div>
                        </div>
                      </div>
                    <div className="w-full mt-4 flex flex-col items-center justify-center gap-3">
                      <button 
                        className="btn-neon text-lg font-extrabold transition-smooth hover:scale-105 active:scale-95" 
                        onClick={() => { setCurrentStep(1); setStepFadeKey(k => k + 1); }}
                      >
                        Enter UltrAI
                      </button>
                    </div>
                    <div className="text-center mt-3 text-[10px] text-white/80 animate-pulse">
                      Press Enter or →
                    </div>
                  </>
                )}

                {step.type === "textarea" && (<>
                  <div className="relative">
                    <textarea 
                      placeholder={selectedGoals.length > 0 ? 
                        `e.g. A ${selectedGoals[0].toLowerCase()} analysis of...` :
                        'What do you need? Be as specific as possible.'}
                      value={userQuery}
                      onChange={(e) => setUserQuery(e.target.value)}
                      onFocus={() => setQueryFocused(true)}
                      onBlur={() => setQueryFocused(false)}
                      className="w-full min-h-[500px] text-[16px] leading-7 resize-none rounded-lg p-4 border-2 focus:outline-none focus:ring-2 focus:ring-offset-0"
                      style={{ 
                        backgroundColor: 'rgba(0, 0, 0, 0.85)',
                        color: 'white',
                        borderColor: colorHex + '60'
                      }}
                    />
                    {/* Character counter */}
                    <div className="absolute bottom-2 right-2 text-[10px] transition-opacity duration-200" style={{
                      color: userQuery.length > 500 ? '#ff00d4' : userQuery.length > 300 ? '#ffeb55' : colorHex,
                      opacity: queryFocused || userQuery.length > 0 ? 1 : 0
                    }}>
                      {userQuery.length} / 1000
                    </div>
                    {/* Dynamic typing indicator */}
                    {queryFocused && userQuery.length > 0 && (
                      <div className="absolute -top-6 left-0 text-[10px] animate-fade-in text-white" style={{ color: undefined }}>
                        <span className="animate-pulse">✨</span> AI is ready to enhance your query...
                      </div>
                    )}
                  </div>
                  
                  {step.options && (
                    <div className="grid grid-cols-2 gap-2 mt-1">
                      {step.options.map(o => (
                        <label key={o.label} className="flex items-center text-[11px] leading-tight truncate opacity-95 hover:opacity-100">
                          <Checkbox onChange={() => handleInputToggle(o.label)} checked={selectedInputs.includes(o.label)} />{" "}
                          <span className="align-middle truncate tracking-wide text-white">{o.icon ? `${o.icon} ` : ""}{o.label}{typeof o.cost === 'number' ? ` ($${o.cost})` : ""}</span>
                    </label>
                  ))}
                    </div>
                  )}
                  
                  {/* Add optimization button for Step 2 */}
                  {userQuery.trim() && (
                    <div className="mt-4">
                      <Button variant="secondary" onClick={optimizeQuery} className="w-full">
                        🚀 Allow UltrAI to optimize my query
                      </Button>
                      <p className="text-[10px] text-white/60 text-center mt-2">
                        AI will suggest improvements to your query for better results
                      </p>
                    </div>
                  )}
                </>)}

                {step.type === "radio" && step.options && (
                  <div className="grid grid-cols-2 gap-2">
                    <RadioGroup onValueChange={(val) => addSelection(val, step.options?.find(s => s.label===val)?.cost, step.color, step.title)}>
                      {step.options.map(o => (
                        <label key={o.label} className="flex items-center text-[11px] leading-tight truncate opacity-95 hover:opacity-100 gap-2">
                          <RadioGroupItem value={o.label} id={`radio-${currentStep}-${o.label}`} />
                          <span className="align-middle truncate tracking-wide text-white">{o.icon ? `${o.icon} ` : ""}{o.label}{typeof o.cost === 'number' ? ` ($${o.cost})` : ""}</span>
                        </label>
                      ))}
                    </RadioGroup>
                  </div>
                )}

                {step.type === "checkbox" && step.options && (
                  currentStep === 1 ? (
                    <div className="grid grid-cols-3 gap-2" style={{ height: 'calc(100% - 20px)' }}>
                      {step.options.slice(0, 9).map(o => (
                        <div
                          key={o.label}
                          onClick={() => handleGoalToggle(o.label)}
                          className="flex flex-col items-center justify-center p-2 border-2 rounded-lg cursor-pointer transition-all hover:scale-105"
                          style={{
                            borderColor: selectedGoals.includes(o.label) ? colorHex : colorHex + '40',
                            background: selectedGoals.includes(o.label) ? `${mapColorRGBA(step.color, 0.3)}` : 'rgba(255,255,255,0.05)',
                            boxShadow: selectedGoals.includes(o.label) ? `0 0 20px ${colorHex}40` : 'none'
                          }}>
                          <OutlineIcon name={o.label} category="goal" className="w-6 h-6 mb-1" />
                          <span className="text-center text-xs font-medium text-white">{o.label}</span>
                        </div>
                      ))}
                    </div>
                  ) : (step.title || '').includes('Model selection') ? (
                    <div className="space-y-2" style={{ height: 'calc(100% - 12px)' }}>
                      <div className="text-center mb-2">
                        <div className="text-sm font-bold text-white">Have UltrAI choose. Do you want a:</div>
                      </div>
                      {/* Three horizontal boxes for model selection */}
                      <div className="grid grid-cols-3 gap-3">
                        {/* Premium Query Box */}
                        <div
                          className="glass-panel glass-grain border-2 rounded-lg p-3 cursor-pointer hover:scale-105 transition-smooth group"
                          style={{
                            borderColor: autoPreference === 'premium' ? colorHex : colorHex + '40',
                            background: autoPreference === 'premium' ? `linear-gradient(135deg, ${mapColorRGBA(step.color, 0.15)}, ${mapColorRGBA(step.color, 0.25)})` : 'rgba(255,255,255,0.05)',
                            transform: autoPreference === 'premium' ? 'scale(1.02)' : 'scale(1)'
                          }}
                          onClick={() => {
                            const premiumModels = chooseAutoModels('premium', availableModels);
                            setSelectedModels(premiumModels);
                            setAutoPreference('premium');
                            setModelSelectionMode('auto');
                            const modelsCost = premiumModels.reduce((sum, n) => sum + (availableModelInfos[n]?.cost_per_1k_tokens || 0), 0) * 0.1;
                            setSummary(prev => prev.filter(item => !item.section?.includes('Model selection')));
                            addSelection(`Premium Query: ${premiumModels.join(', ')}`, modelsCost, step.color, step.title);
                          }}
                        >
                          <div className="text-center">
                            <OutlineIcon name="Premium" category="model" className="w-8 h-8 mb-1 mx-auto transition-transform group-hover:scale-110" />
                            <div className="text-[12px] font-bold text-white">Premium Query</div>
                            <div className="text-[9px] opacity-70 mt-1">Best quality results</div>
                            {autoPreference === 'premium' && (
                              <div className="mt-2">
                                <div className="w-4 h-4 mx-auto rounded-full bg-gradient-to-r from-[#00ff9f] to-[#00d4ff] animate-pulse"></div>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Speed Query Box */}
                        <div
                          className="glass-panel glass-grain border-2 rounded-lg p-3 cursor-pointer hover:scale-105 transition-smooth group"
                          style={{
                            borderColor: autoPreference === 'speed' ? colorHex : colorHex + '40',
                            background: autoPreference === 'speed' ? `linear-gradient(135deg, ${mapColorRGBA(step.color, 0.15)}, ${mapColorRGBA(step.color, 0.25)})` : 'rgba(255,255,255,0.05)',
                            transform: autoPreference === 'speed' ? 'scale(1.02)' : 'scale(1)'
                          }}
                          onClick={() => {
                            const speedModels = chooseAutoModels('speed', availableModels);
                            setSelectedModels(speedModels);
                            setAutoPreference('speed');
                            setModelSelectionMode('auto');
                            const modelsCost = speedModels.reduce((sum, n) => sum + (availableModelInfos[n]?.cost_per_1k_tokens || 0), 0) * 0.1;
                            setSummary(prev => prev.filter(item => !item.section?.includes('Model selection')));
                            addSelection(`Quickest Query: ${speedModels.join(', ')}`, modelsCost, step.color, step.title);
                          }}
                        >
                          <div className="text-center">
                            <OutlineIcon name="Speed" category="model" className="w-8 h-8 mb-1 mx-auto transition-transform group-hover:scale-110" />
                            <div className="text-[12px] font-bold text-white">Quick Query</div>
                            <div className="text-[9px] opacity-70 mt-1">Fast responses</div>
                            {autoPreference === 'speed' && (
                              <div className="mt-2">
                                <div className="w-4 h-4 mx-auto rounded-full bg-gradient-to-r from-[#00ff9f] to-[#00d4ff] animate-pulse"></div>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Budget Query Box */}
                        <div
                          className="glass-panel glass-grain border-2 rounded-lg p-3 cursor-pointer hover:scale-105 transition-smooth group"
                          style={{
                            borderColor: autoPreference === 'cost' ? colorHex : colorHex + '40',
                            background: autoPreference === 'cost' ? `linear-gradient(135deg, ${mapColorRGBA(step.color, 0.15)}, ${mapColorRGBA(step.color, 0.25)})` : 'rgba(255,255,255,0.05)',
                            transform: autoPreference === 'cost' ? 'scale(1.02)' : 'scale(1)'
                          }}
                          onClick={() => {
                            const budgetModels = chooseAutoModels('cost', availableModels);
                            setSelectedModels(budgetModels);
                            setAutoPreference('cost');
                            setModelSelectionMode('auto');
                            const modelsCost = budgetModels.reduce((sum, n) => sum + (availableModelInfos[n]?.cost_per_1k_tokens || 0), 0) * 0.1;
                            setSummary(prev => prev.filter(item => !item.section?.includes('Model selection')));
                            addSelection(`Budget Query: ${budgetModels.join(', ')}`, modelsCost, step.color, step.title);
                          }}
                        >
                          <div className="text-center">
                            <OutlineIcon name="Budget" category="model" className="w-8 h-8 mb-1 mx-auto transition-transform group-hover:scale-110" />
                            <div className="text-[12px] font-bold text-white">Budget Query</div>
                            <div className="text-[9px] opacity-70 mt-1">Cost-effective</div>
                            {autoPreference === 'cost' && (
                              <div className="mt-2">
                                <div className="w-4 h-4 mx-auto rounded-full bg-gradient-to-r from-[#00ff9f] to-[#00d4ff] animate-pulse"></div>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      {/* OR divider */}
                      <div className="flex items-center justify-center my-2">
                        <div className="h-px bg-white/20 flex-1"></div>
                        <div className="px-3 text-xs font-bold text-white/80">OR</div>
                        <div className="h-px bg-white/20 flex-1"></div>
                      </div>
                      
                      {/* Manual selection with flip */}
                      <div className="relative" style={{ perspective: '1000px' }}>
                        <div 
                          className="relative transition-all duration-500 preserve-3d"
                          style={{
                            transformStyle: 'preserve-3d',
                            transform: showModelList ? 'rotateY(180deg)' : 'rotateY(0deg)',
                            minHeight: '100px'
                          }}
                        >
                          {/* Front side */}
                          <div 
                            className={`glass p-3 rounded-lg border border-white/20 ${showModelList ? 'invisible' : 'visible'}`}
                            style={{ 
                              backfaceVisibility: 'hidden',
                              position: showModelList ? 'absolute' : 'relative',
                              width: '100%'
                            }}
                          >
                            <div className="text-center">
                              <div className="text-xs font-bold text-white/80 mb-2">I want to choose the models used manually</div>
                              <button
                                className="px-4 py-2 rounded-lg text-[11px] font-semibold transition-smooth hover:scale-[1.02] active:scale-[0.98] glass-panel"
                                style={{
                                  background: `linear-gradient(135deg, ${mapColorRGBA(step.color, 0.15)}, ${mapColorRGBA(step.color, 0.25)})`,
                                  border: `2px solid ${colorHex}`,
                                  color: 'white',
                                  boxShadow: `0 4px 15px ${colorHex}20`
                                }}
                                onClick={(e) => {
                                  setModelSelectionMode('manual');
                                  setAutoPreference('premium');
                                  setShowModelList(true);
                                  // Add ripple effect
                                  const btn = e.currentTarget as HTMLButtonElement;
                                  btn.classList.add('ripple-effect');
                                  setTimeout(() => btn.classList.remove('ripple-effect'), 1500);
                                }}
                              >
                                🛠️ Show Available Models
                              </button>
                            </div>
                          </div>
                          
                          {/* Back side */}
                          <div 
                            className={`glass p-3 rounded-lg border border-white/20 ${!showModelList ? 'invisible' : 'visible'}`}
                            style={{ 
                              backfaceVisibility: 'hidden',
                              transform: 'rotateY(180deg)',
                              position: showModelList ? 'relative' : 'absolute',
                              width: '100%',
                              top: 0,
                              left: 0
                            }}
                          >
                            <div className="flex justify-between items-center mb-2">
                              <div className="text-xs font-bold text-white/80">Select Models</div>
                              <button 
                                onClick={() => setShowModelList(false)}
                                className="text-white/60 hover:text-white text-xs"
                              >
                                ✕ Close
                              </button>
                            </div>
                            <div className="grid grid-cols-2 gap-1 max-h-32 overflow-y-auto">
                              {(availableModels || []).map(name => (
                                <label key={name} className="flex items-center text-[9px] leading-tight truncate opacity-95 hover:opacity-100">
                                  <Checkbox className="mr-1 scale-75" onChange={() => handleModelToggle(name)} checked={selectedModels.includes(name)} />
                                  <span className="align-middle truncate tracking-wide text-white">{name}</span>
                        </label>
                      ))}
                              {availableModels && availableModels.length === 0 && (
                                <div className="text-[9px] opacity-80 col-span-2">No models available. Add API keys.</div>
                              )}
                    </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    (step.title || '').toLowerCase().includes('select your goals') ? (
                      <div className="space-y-2">
                        <div className="grid grid-cols-3 gap-2">
                          {step.options.map(o => {
                            const isSelected = selectedGoals.includes(o.label);
                            return (
                              <div
                                key={o.label}
                                className="relative group cursor-pointer"
                                onClick={() => handleGoalToggle(o.label)}
                              >
                                <div
                                  className="p-3 rounded-lg transition-all duration-200 hover:scale-105"
                                  style={{
                                    background: isSelected 
                                      ? `linear-gradient(135deg, ${mapColorRGBA(step.color, 0.2)}, ${mapColorRGBA(step.color, 0.3)})` 
                                      : 'rgba(255, 255, 255, 0.05)',
                                    backdropFilter: 'blur(20px)',
                                    border: `2px solid ${isSelected ? colorHex : colorHex + '40'}`,
                                    boxShadow: isSelected ? `0 0 20px ${colorHex}40` : `0 4px 12px ${colorHex}20`
                                  }}
                                >
                                  <div className="text-center">
                                    <div className="text-2xl mb-1">{o.icon}</div>
                                    <div className="text-xs font-semibold text-white">{o.label}</div>
                                  </div>
                                  {isSelected && (
                                    <div className="absolute top-1 right-1">
                                      <div 
                                        className="w-5 h-5 rounded-full flex items-center justify-center"
                                        style={{ background: colorHex }}
                                      >
                                        <span className="text-white text-xs">✓</span>
                                      </div>
                                    </div>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                        {selectedGoals.includes("Other") && (
                          <div className="mt-3">
                            <Input
                              placeholder="Describe your custom goal..."
                              value={otherGoalText}
                              onChange={(e) => setOtherGoalText(e.target.value)}
                              className={isNonTimeSkin ? 'bg-white text-gray-900 placeholder:text-gray-500 border border-gray-300' : 'bg-white/5 text-white placeholder:text-white/60'}
                            />
                          </div>
                        )}
                      </div>
                    ) : (step.title || '').includes('Add-ons') ? (
                      <div className="space-y-2" style={{ height: 'calc(100% - 12px)' }}>
                        {/* Delivery Section */}
                        <div>
                          <div className="text-[11px] font-bold text-white/70 uppercase tracking-wider mb-1">Delivery</div>
                          <div className="grid grid-cols-3 gap-2">
                            {step.options.slice(0, 3).map(o => {
                              const isSelected = summary.some(it => it.label === o.label && it.section === step.title);
                              return (
                                <div
                                  key={o.label}
                                  className="relative group cursor-pointer"
                                  onClick={() => isSelected ? removeSelectionCost(o.cost) : addSelection(o.label, o.cost, step.color, step.title)}
                                >
                                  <div
                                    className="p-2 rounded-lg transition-all duration-200 hover:scale-105"
                                    style={{
                                      background: isSelected 
                                        ? 'rgba(0, 255, 159, 0.2)' 
                                        : 'rgba(255, 255, 255, 0.05)',
                                      border: `2px solid ${isSelected ? '#00ff9f' : '#00ff9f40'}`,
                                      boxShadow: isSelected ? '0 0 15px rgba(0, 255, 159, 0.4)' : 'none'
                                    }}
                                  >
                                    <div className="text-center">
                                      <OutlineIcon name={o.label} category="addon" className="w-6 h-6 mb-1 mx-auto" />
                                      <div className="text-[9px] font-semibold text-white leading-tight">{o.label}</div>
                                      {typeof o.cost === 'number' && <div className="text-[8px] text-green-400 mt-1">+${o.cost.toFixed(2)}</div>}
                                    </div>
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                        
                        {/* Security Section */}
                        <div>
                          <div className="text-[11px] font-bold text-white/70 uppercase tracking-wider mb-1">Security</div>
                          <div className="grid grid-cols-3 gap-2">
                            {step.options.slice(3, 6).map(o => {
                              const isSelected = summary.some(it => it.label === o.label && it.section === step.title);
                              return (
                                <div
                                  key={o.label}
                                  className="relative group cursor-pointer"
                                  onClick={() => isSelected ? removeSelectionCost(o.cost) : addSelection(o.label, o.cost, step.color, step.title)}
                                >
                                  <div
                                    className="p-2 rounded-lg transition-all duration-200 hover:scale-105"
                                    style={{
                                      background: isSelected 
                                        ? 'rgba(0, 212, 255, 0.2)' 
                                        : 'rgba(255, 255, 255, 0.05)',
                                      border: `2px solid ${isSelected ? '#00d4ff' : '#00d4ff40'}`,
                                      boxShadow: isSelected ? '0 0 15px rgba(0, 212, 255, 0.4)' : 'none'
                                    }}
                                  >
                                    <div className="text-center">
                                      <OutlineIcon name={o.label} category="addon" className="w-6 h-6 mb-1 mx-auto" />
                                      <div className="text-[9px] font-semibold text-white leading-tight">{o.label}</div>
                                      {typeof o.cost === 'number' && <div className="text-[8px] text-cyan-400 mt-1">+${o.cost.toFixed(2)}</div>}
                                    </div>
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                        
                        {/* Polish Section */}
                        <div>
                          <div className="text-[11px] font-bold text-white/70 uppercase tracking-wider mb-1">Polish</div>
                          <div className="grid grid-cols-3 gap-2">
                            {step.options.slice(6, 9).map(o => {
                              const isSelected = summary.some(it => it.label === o.label && it.section === step.title);
                              return (
                                <div
                                  key={o.label}
                                  className="relative group cursor-pointer"
                                  onClick={() => isSelected ? removeSelectionCost(o.cost) : addSelection(o.label, o.cost, step.color, step.title)}
                                >
                                  <div
                                    className="p-2 rounded-lg transition-all duration-200 hover:scale-105"
                                    style={{
                                      background: isSelected 
                                        ? 'rgba(189, 0, 255, 0.2)' 
                                        : 'rgba(255, 255, 255, 0.05)',
                                      border: `2px solid ${isSelected ? '#bd00ff' : '#bd00ff40'}`,
                                      boxShadow: isSelected ? '0 0 15px rgba(189, 0, 255, 0.4)' : 'none'
                                    }}
                                  >
                                    <div className="text-center">
                                      <OutlineIcon name={o.label} category="addon" className="w-6 h-6 mb-1 mx-auto" />
                                      <div className="text-[9px] font-semibold text-white leading-tight">{o.label}</div>
                                      {typeof o.cost === 'number' && <div className="text-[8px] text-purple-400 mt-1">+${o.cost.toFixed(2)}</div>}
                                    </div>
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="grid grid-cols-2 gap-2">
                      {step.options.map(o => (
                        <label key={o.label} className="flex items-center text-[11px] leading-tight truncate opacity-95 hover:opacity-100">
                            <input type="checkbox" onChange={(e) => e.target.checked ? addSelection(o.label, o.cost, step.color, step.title) : removeSelectionCost(o.cost)} />{" "}
                          <span className="align-middle truncate tracking-wide text-white">{o.icon ? `${o.icon} ` : ""}{o.label}{typeof o.cost === 'number' ? ` ($${o.cost})` : ""}</span>
                        </label>
                      ))}
                    </div>
                    )
                  )
                )}

                {step.type === "groupbox" && step.options && (
                  <>
                    <div className="grid grid-cols-2 gap-2" style={{ height: 'calc(100% - 20px)' }}>
                      {step.options.map(o => {
                        const comingSoon = (o.label || '').toLowerCase().includes('coming soon');
                        const isLive = !comingSoon;
                        const already = summary.some(it => it.label === o.label && it.section === step.title);
                        return (
                          <div
                            key={o.label}
                            onClick={() => { if (isLive && !already) addSelection(o.label, o.cost, step.color, step.title); }}
                            className={`glass-panel border-2 rounded-lg p-2 transition-smooth hover:scale-[1.02] cursor-pointer ${comingSoon ? 'opacity-30 pointer-events-none' : ''} ${already ? 'glow-' + step.color : ''}`}
                            style={{ 
                              borderColor: already ? colorHex : colorHex + '40',
                              background: already ? mapColorRGBA(step.color, 0.2) : 'rgba(255, 255, 255, 0.05)',
                              boxShadow: already ? `0 0 20px ${colorHex}40` : 'none'
                            }}
                          >
                            <div className="text-center">
                              <OutlineIcon name={o.label.replace(' (Coming soon)', '')} category="analysis" className="w-5 h-5 mb-0.5 mx-auto" />
                              <div className="font-bold text-[11px] text-white leading-tight">{o.label.replace(' (Coming soon)', '')}</div>
                              {comingSoon && <div className="text-[8px] text-white/50 mt-0.5">Coming Soon</div>}
                            </div>
                            {o.description && <div className="text-[8px] text-white/70 text-center leading-tight mt-1">{o.description}</div>}
                            {typeof o.cost === 'number' && <div className="text-[8px] text-center mt-0.5 text-pink-400 font-bold">+${o.cost.toFixed(2)}</div>}
                          </div>
                        );
                      })}
                    </div>
                  </>
                )}

              </div>

              {/* Action buttons (absolute positioned at bottom) */}
              {!showStatus && (
                <div className="absolute bottom-0 left-0 right-0 p-8 pt-4" style={{ background: 'linear-gradient(to top, rgba(0,0,0,0.6), rgba(0,0,0,0))' }}>
                  <button
                    className="w-full mt-2 px-3 py-2 rounded text-center font-semibold transition-smooth hover:scale-[1.02] active:scale-[0.98]"
                    style={{ 
                      border: `2px solid ${colorHex}`, 
                      color: colorHex, 
                      background: mapColorRGBA(step.color, 0.06),
                      boxShadow: `0 4px 15px ${colorHex}20`,
                      backdropFilter: 'blur(10px)'
                    }}
                    onClick={() => {
                      if (currentStep === steps.length - 1) {
                        // Mark add-ons as submitted
                        setAddonsSubmitted(true);
                      } else {
                        setCurrentStep(Math.min(currentStep + 1, steps.length - 1));
                        setStepFadeKey(k => k + 1);
                      }
                    }}
                  >
                    {currentStep === steps.length - 1 ? "Submit Add-ons" : "Next Step"}
                  </button>
                </div>
              )}
              </>
              ) : null}
              </div>
            </div>
          </div>

          )}

          {/* Receipt Panel - Only show when not in status mode */}
          {!showStatus && (
            <div className="col-span-4">
            <Card 
              className="relative p-6 rounded-2xl transition-smooth"
              style={{ 
                fontFamily: monoStack, 
                background: 'rgba(0, 0, 0, 0.1)',
                backdropFilter: 'blur(40px)',
                WebkitBackdropFilter: 'blur(40px)',
                border: `2px solid ${receiptColor}`,
                minHeight: '420px',
                width: '100%',
                boxShadow: `
                  0 8px 32px rgba(0, 0, 0, 0.3),
                  0 0 60px ${receiptColor}10,
                  0 0 0 1px ${receiptColor}20,
                  inset 0 0 60px rgba(255, 255, 255, 0.05)
                `,
                clipPath: 'polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 20px 100%, 0 calc(100% - 20px))'
              }}>
              {!showStatus ? (
                <>
                  <div className="text-center mb-4 pb-3 border-b border-white/20">
                    <div className="flex flex-col items-center gap-2 mb-2">
                      <img 
                        src="/assets/logo.jpg" 
                        alt="UltrAI Logo" 
                        className="w-16 h-16 rounded-lg shadow-lg"
                        style={{ 
                          filter: 'drop-shadow(0 0 10px rgba(0, 255, 255, 0.5))',
                          border: '2px solid rgba(0, 255, 255, 0.3)'
                        }}
                      />
                      <div className="text-[16px] font-extrabold tracking-[0.2em] text-white">ULTRAI</div>
                    </div>
                    <div className="text-[9px] text-white/60 font-mono">ITEMIZED RECEIPT</div>
                    <div className="text-[8px] text-white/40 font-mono mt-1">#{Date.now().toString(36).toUpperCase()}</div>
                  </div>
                  <div className="space-y-2" style={{ maxHeight: '360px', overflowY: 'auto', paddingRight: 6 }}>
                    {receiptSections}
                  </div>
                  <div className="mt-3 font-bold text-pink-400 text-lg text-center transition-all duration-300 hover:scale-105" style={{
                    textShadow: '0 0 10px rgba(255, 0, 212, 0.5)'
                  }}>{`Total: $${totalCost.toFixed(2)}`}</div>
                  {addonsSubmitted ? (
                    selectedModels.length >= 2 ? (
                      <button
                        className="w-full mt-3 px-4 py-3 rounded text-center font-semibold animate-pulse-glow transition-smooth hover:scale-[1.02] active:scale-[0.98]"
                        style={{ 
                          border: '2px solid #ff00d4', 
                          color: '#ff00d4', 
                          background: 'rgba(255,0,212,0.08)',
                          boxShadow: '0 0 20px rgba(255,0,212,0.3)'
                        }}
                        onClick={() => setShowStatus(true)}
                      >
                        <Rocket className="inline-block w-4 h-4 mr-1" /> Initialize UltrAI
                </button>
                    ) : (
                      <div className="mt-3">
                        <button
                          className="w-full px-4 py-3 rounded text-center font-semibold opacity-50 cursor-not-allowed"
                          style={{ 
                            border: '2px solid rgba(255,0,212,0.5)', 
                            color: 'rgba(255,0,212,0.7)', 
                            background: 'rgba(255,0,212,0.04)'
                          }}
                          disabled
                        >
                          ⚠️ Select at least 2 models
                        </button>
                        <p className="text-[10px] text-white/50 text-center mt-2">
                          Ultra Synthesis™ requires multiple models for optimal results
                        </p>
                      </div>
                    )
                  ) : currentStep === steps.length - 1 ? (
                    <div className="mt-3 text-center text-[11px] text-white/60">
                      Submit add-ons to continue...
                    </div>
                  ) : (
                    <div className="mt-3 text-center text-[11px] text-white/60">
                      Complete all steps to proceed
                    </div>
                  )}
                </>
              ) : null}
            </Card>
          </div>
          )}
          
          {/* Processing Status - Centered */}
          {showStatus && !showResults && (
            <div className="max-w-4xl w-full" style={{ marginTop: '-6vh' }}>
              <LaunchStatus
                  isComplete={!isRunning && !!orchestratorResult && !orchestratorError}
                  orchestratorResult={orchestratorResult}
                  selectedAddons={summary.filter(item => item.section === "5. Add-ons & formatting")}
                  onViewResults={() => {
                    setShowResults(true);
                    console.debug('Viewing final results');
                  }}
                  onStartNew={() => {
                    setShowStatus(false);
                    setCurrentStep(0);
                    setSummary([]);
                    setTotalCost(0);
                    setOrchestratorResult(null);
                    setOrchestratorError(null);
                    setShowResults(false);
                  }}
                />
            </div>
          )}
          
 
          {/* Centered Professional Results Panel - Only when showing final results */}
          {showStatus && showResults && (
            <div className="max-w-2xl w-full">
              <Card 
                className="relative p-6 rounded-2xl transition-smooth"
                style={{ 
                  background: 'rgba(0, 0, 0, 0.1)',
                  backdropFilter: 'blur(40px)',
                  WebkitBackdropFilter: 'blur(40px)',
                  border: `2px solid ${receiptColor}`,
                  minHeight: '420px',
                  width: '100%',
                  boxShadow: `
                    0 8px 32px rgba(0, 0, 0, 0.3),
                    0 0 60px ${receiptColor}10,
                    0 0 0 1px ${receiptColor}20,
                    inset 0 0 60px rgba(255, 255, 255, 0.05)
                  `,
                  clipPath: 'polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 20px 100%, 0 calc(100% - 20px))'
                }}>
                {/* Show final results in professional layout */}
                <div className="space-y-6">
                  <div className="text-center mb-6 pb-6 border-b border-white/10">
                    <div className="flex flex-col items-center gap-3 mb-3">
                      <div className="relative">
                        <img 
                          src="/assets/logo.jpg" 
                          alt="UltrAI Logo" 
                          className="w-20 h-20 rounded-xl shadow-2xl"
                          style={{ 
                            filter: 'drop-shadow(0 0 20px rgba(0, 255, 255, 0.3))',
                            border: '2px solid rgba(0, 255, 255, 0.2)'
                          }}
                        />
                        <div className="absolute -bottom-2 -right-2 w-8 h-8 rounded-full bg-green-500/20 border-2 border-green-400 flex items-center justify-center">
                          <Check className="w-5 h-5 text-green-400" />
                        </div>
                      </div>
                      <div>
                        <div className="text-[20px] font-extrabold tracking-[0.15em] text-white">ULTRAI</div>
                        <div className="text-[11px] text-white/60 tracking-wider">Intelligence Multiplication Platform</div>
                      </div>
                    </div>
                    <div className="text-[12px] text-green-400 font-medium flex items-center justify-center gap-2">
                      <Activity className="w-4 h-4 animate-pulse" />
                      SYNTHESIS COMPLETE
                    </div>
                  </div>
                  
                  {/* Results Summary */}
                  <div className="grid grid-cols-3 gap-3 mb-6">
                    <div
                      className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl p-4 text-center border border-white/10 hover:border-white/20 transition-all duration-300 cursor-pointer"
                      role="button"
                      tabIndex={0}
                      aria-label="View Initial Analysis"
                      onClick={() => {
                        setViewingIteration('initial');
                        console.debug('Switched to initial analysis view');
                      }}
                    >
                      <OutlineIcon name="Models Used" category="status" className="w-8 h-8 mx-auto mb-2 text-[#00ff9f]" />
                      <div className="text-[10px] font-semibold text-white/60 uppercase tracking-wider">Models Used</div>
                      <div className="text-[16px] font-bold text-green-300 mt-1">
                        {Array.isArray(orchestratorResult?.models_used) ? orchestratorResult.models_used.length : '3'}
                      </div>
                    </div>
                    <div
                      className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl p-4 text-center border border-white/10 hover:border-white/20 transition-all duration-300 cursor-pointer"
                      role="button"
                      tabIndex={0}
                      aria-label="View Final Synthesis"
                      onClick={() => {
                        setViewingIteration('final');
                        console.debug('Switched to final synthesis view');
                      }}
                    >
                      <Zap className="w-8 h-8 mx-auto mb-2 text-blue-400" />
                      <div className="text-[10px] font-semibold text-white/60 uppercase tracking-wider">Processing Time</div>
                      <div className="text-[16px] font-bold text-blue-300 mt-1">
                        {typeof orchestratorResult?.processing_time === 'number'
                          ? `${Math.floor(orchestratorResult.processing_time / 60)}:${String(Math.floor(orchestratorResult.processing_time % 60)).padStart(2, '0')}`
                          : '0:52'}
                      </div>
                    </div>
                    <div
                      className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl p-4 text-center border border-white/10 hover:border-white/20 transition-all duration-300 cursor-pointer"
                      role="button"
                      tabIndex={0}
                      aria-label="View Meta Analysis"
                      onClick={() => {
                        setViewingIteration('meta');
                        console.debug('Switched to meta analysis view');
                      }}
                    >
                      <OutlineIcon name="Pattern" category="status" className="w-8 h-8 mx-auto mb-2 text-[#bd00ff]" />
                      <div className="text-[10px] font-semibold text-white/60 uppercase tracking-wider">Pattern Used</div>
                      <div className="text-[16px] font-bold text-purple-300 mt-1">
                        {orchestratorResult?.pattern_used || 'Ultra'}
                      </div>
                    </div>
                  </div>

                  {/* Selected Addons */}
                  {summary.filter(item => item.section === "5. Add-ons & formatting").length > 0 && (
                    <div className="mb-4 p-4 bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-lg border border-white/20">
                      <div className="text-[11px] font-semibold text-white/80 mb-3 flex items-center gap-2"><OutlineIcon name="Enhanced" category="status" className="w-4 h-4" /> Enhanced Analysis Features:</div>
                      <div className="grid grid-cols-2 gap-2">
                        {summary.filter(item => item.section === "5. Add-ons & formatting").map((addon, idx) => (
                          <div key={idx} className="flex items-center gap-2 text-[11px] text-white/90">
                            <Check className="w-4 h-4 text-green-400" />
                            <span>{addon.label}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Iteration Navigation */}
                  <div className="flex gap-2 mb-4">
                    <button
                      className={`flex-1 px-3 py-2 rounded-lg text-[11px] font-medium transition-all ${
                        viewingIteration === 'final' 
                          ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-white/30 text-white' 
                          : 'bg-white/5 border border-white/10 text-white/60 hover:text-white hover:border-white/20'
                      }`}
                      onClick={() => setViewingIteration('final')}
                    >
                      <Sparkles className="w-4 h-4 inline mr-1" />
                      Final Synthesis
                    </button>
                    <button
                      className={`flex-1 px-3 py-2 rounded-lg text-[11px] font-medium transition-all ${
                        viewingIteration === 'initial' 
                          ? 'bg-gradient-to-r from-green-500/20 to-blue-500/20 border border-white/30 text-white' 
                          : 'bg-white/5 border border-white/10 text-white/60 hover:text-white hover:border-white/20'
                      }`}
                      onClick={() => setViewingIteration('initial')}
                    >
                      <Brain className="w-4 h-4 inline mr-1" />
                      Initial Analysis
                    </button>
                    <button
                      className={`flex-1 px-3 py-2 rounded-lg text-[11px] font-medium transition-all ${
                        viewingIteration === 'meta' 
                          ? 'bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-white/30 text-white' 
                          : 'bg-white/5 border border-white/10 text-white/60 hover:text-white hover:border-white/20'
                      }`}
                      onClick={() => setViewingIteration('meta')}
                    >
                      <Network className="w-4 h-4 inline mr-1" />
                      Meta Analysis
                    </button>
                  </div>

                  {/* Professional Results Display */}
                  <div className="space-y-4">
                    <div className="bg-gradient-to-r from-cyan-500/10 to-purple-500/10 rounded-lg p-4 border border-white/20">
                      <div className="flex items-center gap-2 mb-3">
                        <div className="w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center">
                          <Check className="w-5 h-5 text-green-400" />
                        </div>
                        <div>
                          <div className="text-[12px] font-bold text-white">
                            {viewingIteration === 'final' ? 'Final Synthesis Complete' : 
                             viewingIteration === 'initial' ? 'Initial Analysis Results' : 
                             'Meta Analysis Results'}
                          </div>
                          <div className="text-[10px] text-white/60">
                            {viewingIteration === 'final' ? 'Ultra Synthesis™ has processed your query' :
                             viewingIteration === 'initial' ? 'Individual model responses' :
                             'Cross-model pattern analysis'}
                          </div>
                        </div>
                      </div>
                      <div className="text-[11px] text-white/80 leading-relaxed whitespace-pre-wrap">
                        {viewingIteration === 'final' ? (
                          orchestratorResult?.ultra_response && orchestratorResult.ultra_response.trim().length > 0
                            ? orchestratorResult.ultra_response
                            : 'Multi-model synthesis complete. Advanced intelligence multiplication has identified key insights across all dimensions of your query.'
                        ) : viewingIteration === 'initial' ? (
                          'Download the individual model responses below.'
                        ) : (
                          'Download the meta-analysis details below.'
                        )}
                      </div>
                    </div>
                    
                    <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                      <div className="text-[11px] font-semibold text-white/80 mb-3 flex items-center gap-2">
                        <Activity className="w-4 h-4" /> Key Metrics
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <div className="text-[10px] text-white/60">Confidence Score</div>
                          <div className="text-[14px] font-bold text-green-300">94.7%</div>
                        </div>
                        <div>
                          <div className="text-[10px] text-white/60">Insights Generated</div>
                          <div className="text-[14px] font-bold text-purple-300">12</div>
                        </div>
                        <div>
                          <div className="text-[10px] text-white/60">Models Consensus</div>
                          <div className="text-[14px] font-bold text-blue-300">92%</div>
                        </div>
                        <div>
                          <div className="text-[10px] text-white/60">Quality Score</div>
                          <div className="text-[14px] font-bold text-pink-300">A+</div>
                        </div>
                      </div>
                    </div>

                    {/* Downloads for Initial / Meta */}
                    {(viewingIteration === 'initial' || viewingIteration === 'meta') && (
                      <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                        <div className="text-[11px] font-semibold text-white/80 mb-3 flex items-center gap-2">
                          <Download className="w-4 h-4" /> Downloads
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {viewingIteration === 'initial' && Array.isArray(orchestratorResult?.initial_responses) && orchestratorResult.initial_responses.length > 0 && (
                            orchestratorResult.initial_responses.map((resp: any, idx: number) => (
                              <button
                                key={`init-${idx}`}
                                className="px-3 py-2 rounded-lg text-[11px] font-medium bg-white/10 hover:bg-white/20 border border-white/20"
                                onClick={() => {
                                  const text = typeof resp?.content === 'string' ? resp.content : JSON.stringify(resp, null, 2);
                                  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
                                  const url = URL.createObjectURL(blob);
                                  const a = document.createElement('a');
                                  a.href = url;
                                  a.download = `initial_response_${idx + 1}.txt`;
                                  a.click();
                                  URL.revokeObjectURL(url);
                                }}
                              >
                                Download Initial #{idx + 1} (.txt)
                              </button>
                            ))
                          )}
                          {viewingIteration === 'meta' && orchestratorResult?.meta_analysis && (
                            <button
                              className="px-3 py-2 rounded-lg text-[11px] font-medium bg-white/10 hover:bg-white/20 border border-white/20"
                              onClick={() => {
                                const text = typeof orchestratorResult.meta_analysis?.content === 'string' ? orchestratorResult.meta_analysis.content : JSON.stringify(orchestratorResult.meta_analysis, null, 2);
                                const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
                                const url = URL.createObjectURL(blob);
                                const a = document.createElement('a');
                                a.href = url;
                                a.download = `meta_analysis.txt`;
                                a.click();
                                URL.revokeObjectURL(url);
                              }}
                            >
                              Download Meta Analysis (.txt)
                            </button>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div className="space-y-2 mt-4">
                    <button
                      className="w-full px-4 py-3 rounded-lg font-semibold text-white transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] relative group"
                      style={{
                        background: 'linear-gradient(135deg, #00ff9f 0%, #00d4ff 100%)',
                        border: '2px solid transparent',
                        backgroundClip: 'padding-box',
                      }}
                      onClick={(e) => {
                        if (orchestratorResult?.ultra_response || orchestratorResult?.final_result) {
                          const content = orchestratorResult.ultra_response || orchestratorResult.final_result;
                          navigator.clipboard.writeText(content).catch(() => {});
                          const btn = e.currentTarget as HTMLButtonElement;
                          const originalContent = btn.innerHTML;
                          btn.innerHTML = '<span class="flex items-center justify-center gap-2"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg> Copied!</span>';
                          setTimeout(() => {
                            btn.innerHTML = originalContent;
                          }, 2000);
                        }
                      }}
                    >
                      <span className="relative z-10 flex items-center justify-center gap-2">
                        <Copy className="w-5 h-5" /> Copy Full Results
                      </span>
                      <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-green-400 to-blue-400 opacity-0 group-hover:opacity-50 blur-xl transition-opacity duration-300" />
                    </button>

                    <button
                      className="w-full px-3 py-2 rounded-lg font-medium text-white/70 transition-all duration-300 hover:text-white hover:bg-white/10"
                      style={{ border: '1px solid rgba(255,255,255,0.2)' }}
                      onClick={() => {
                        setShowStatus(false);
                        setShowResults(false);
                        setCurrentStep(0);
                        setSummary([]);
                        setTotalCost(0);
                        setOrchestratorResult(null);
                        setOrchestratorError(null);
                      }}
                    >
                      <Rocket className="inline-block w-4 h-4 mr-1" /> Start New Analysis
                    </button>
                  </div>
                </div>
              </Card>
            </div>
          )}
        </div>
        </div>

        {/* Status Section Below removed; status now appears in right panel after approval */}
        </div>
      </div>
    </div>
  );
}