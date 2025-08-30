"use client";
import { useEffect, useState, useMemo, useCallback, memo } from "react";
import { processWithFeatherOrchestration } from "../api/orchestrator";
import StatusUpdater from "./StatusUpdater";
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
  return (
    <div>
      <div className="uppercase text-[10px] tracking-wider mb-1 text-center text-white/80">{sectionTitle}</div>
      {items.map((s, i) => (
        <div key={i} className="text-[10px] leading-tight flex items-center text-white/85 hover:text-white transition-colors duration-200 group cursor-pointer">
          <span className="flex-auto overflow-hidden text-ellipsis whitespace-nowrap group-hover:text-shadow-sm" title={s.label}>{s.label}</span>
          <span className="px-1 select-none opacity-50 group-hover:opacity-70">. . . . . . . . . . .</span>
          <span className="text-right w-14 group-hover:text-pink-400 transition-colors">${s.cost.toFixed(2)}</span>
        </div>
      ))}
    </div>
  );
});

export default function CyberWizard() {
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
  const [isOptimizing] = useState<boolean>(false);
  const [optimizationStep] = useState<number>(0);
  const [modelStatuses, setModelStatuses] = useState<Record<string, 'checking' | 'ready' | 'error'>>({});
  const [bgTheme, setBgTheme] = useState<'morning' | 'afternoon' | 'sunset' | 'night'>('night');
  const [otherGoalText, setOtherGoalText] = useState<string>("");
  const [showModelList, setShowModelList] = useState<boolean>(false);
  const [addonsSubmitted, setAddonsSubmitted] = useState<boolean>(false);
  const [, setLastAddedItem] = useState<string | null>(null);
  // Billboard overlay disabled; remove state to avoid unused variable lints

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
        const r = await fetch("/api/available-models", { cache: "no-store" });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const d = await r.json();
        if (d && Array.isArray(d.models)) {
          const names = d.models.map((m: any) => m.name);
          setAvailableModels(names);
          const infoMap: Record<string, { provider: string; cost_per_1k_tokens: number }> = {};
          const statusMap: Record<string, 'checking' | 'ready' | 'error'> = {};
          d.models.forEach((m: any) => {
            infoMap[String(m.name)] = {
              provider: String(m.provider || ''),
              cost_per_1k_tokens: Number(m.cost_per_1k_tokens || 0),
            };
            // Set all models as ready since they're returned by the API
            statusMap[String(m.name)] = 'ready';
          });
          setAvailableModelInfos(infoMap);
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
        // overlay disabled
        const models = selectedModels.length > 0 ? selectedModels : null;
        const res = await processWithFeatherOrchestration({
          prompt: userQuery || "",
          models,
          pattern: "comparative",
          ultraModel: null,
          outputFormat: "plain",
        });
        
        // Check if the API returned an error in the response
        if (res.error) {
          const errorMessage = typeof res.error === 'object' 
            ? res.error.message || JSON.stringify(res.error)
            : String(res.error);
          setOrchestratorError(errorMessage);
          setOrchestratorResult(null);
        } else {
          setOrchestratorResult(res);
          console.log("Ultra Synthesis result", res);
        }
        // overlay disabled
      } catch (e: any) {
        console.error("Ultra Synthesis failed", e);
        setOrchestratorError(e?.message || String(e));
        // overlay disabled
      } finally {
        setIsRunning(false);
      }
    })();
  }, [showStatus]);

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

  const colorHex = useMemo(() => step ? mapColorHex(step.color) : '#00ff9f', [step]);
  const receiptColor = '#ff6600'; // Cyberpunk orange

  const handleGoalToggle = useCallback((label: string) => {
    if (!step) return;
    const option = step.options?.find(o => o.label === label);
    const cost = option?.cost;
    setSelectedGoals(prev => prev.includes(label) ? (removeSelectionCost(cost), prev.filter(l => l !== label)) : (addSelection(label, cost, step.color, step.title), [...prev, label]));
  }, [step]);
  
  const handleInputToggle = useCallback((label: string) => {
    if (!step) return;
    const option = step.options?.find(o => o.label === label);
    const cost = option?.cost;
    setSelectedInputs(prev => prev.includes(label) ? (removeSelectionCost(cost), prev.filter(l => l !== label)) : (addSelection(label, cost, step.color, step.title), [...prev, label]));
  }, [step]);
  
  const handleModelToggle = useCallback((label: string) => {
    if (!step) return;
    const option = step.options?.find(o => o.label === label);
    const cost = option?.cost;
    setSelectedModels(prev => prev.includes(label) ? (removeSelectionCost(cost), prev.filter(l => l !== label)) : (addSelection(label, cost, step.color, step.title), [...prev, label]));
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
    switch (bgTheme) {
      case 'morning':
        return '/bg-morning.jpeg';
      case 'afternoon':
        return '/bg-afternoon.jpg';
      case 'sunset':
        return '/bg-sunset.jpeg';
      case 'night':
      default:
        return '/bg-night.jpeg';
    }
  }, [bgTheme]);

  // Glass panel darkness based on theme for better readability
  const glassBackground = useMemo(() => {
    switch (bgTheme) {
      case 'morning':
        return 'rgba(0, 0, 0, 0.35)'; // Darker for bright morning
      case 'afternoon':
        return 'rgba(0, 0, 0, 0.30)'; // Darker for bright afternoon
      case 'sunset':
        return 'rgba(0, 0, 0, 0.20)'; // Medium for sunset
      case 'night':
      default:
        return 'rgba(0, 0, 0, 0.15)'; // Lighter for dark night
    }
  }, [bgTheme]);

  const selectedModelsDisplay = useMemo(() => selectedModels.join(', '), [selectedModels]);

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
        'gpt-4o',
        'claude-3-5-sonnet-20241022',
        'gemini-1.5-pro',
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

  // Loading state check - after all hooks
  if (steps.length === 0) return <div>Loading…</div>;

  // Step 0: Intro — render with background and billboard
  if (currentStep === 0 && step && step.type === 'intro') {
  return (
      <div className="relative flex min-h-screen w-full items-start justify-center p-0 text-white font-cyber text-sm overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0">
          <div
            className="absolute inset-0 animate-pulse-slow"
            style={{
              backgroundImage: "url('/cityscape-background.jpeg'), url('/ultrai-bg.jpg')",
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              transform: 'scale(1.1)',
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/80" />
          
          {/* Animated grid overlay */}
          <div className="absolute inset-0" style={{
            backgroundImage: `linear-gradient(rgba(0,255,159,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,255,159,0.03) 1px, transparent 1px)`,
            backgroundSize: '50px 50px',
            animation: 'grid-move 20s linear infinite'
          }} />
          </div>

        {/* Floating particles */}
        <div className="absolute inset-0 overflow-hidden">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="absolute w-1 h-1 bg-mint-400 rounded-full animate-float"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 10}s`,
                animationDuration: `${15 + Math.random() * 10}s`,
                opacity: Math.random() * 0.5 + 0.2
              }}
            />
          ))}
        </div>

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
                    textShadow: `
                      0 0 10px #00ff9f,
                      0 0 20px #00ff9f,
                      0 0 30px #00ff9f,
                      0 0 40px #00ff9f
                    `
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
                      animationDelay: `${0.7 + i * 0.1}s`
                    }}
                  >
                    {feature.icon} {feature.text}
                  </span>
                ))}
              </div>

              {/* Main narrative */}
              <div className="max-w-3xl mx-auto mt-8">
                <p className="text-lg leading-relaxed text-center text-white/90">
                  Welcome to the future of <span className="font-bold" style={{
                    color: '#00ff9f',
                    textShadow: '0 0 5px #00ff9f, 0 0 10px #00ff9f'
                  }}>Intelligence Multiplication</span>. 
                  We orchestrate a sophisticated ensemble of leading AI models, each contributing their unique strengths 
                  to deliver <span className="font-bold" style={{
                    color: '#00d4ff',
                    textShadow: '0 0 5px #00d4ff, 0 0 10px #00d4ff'
                  }}>unprecedented quality</span> and <span className="font-bold" style={{
                    color: '#ff6600',
                    textShadow: '0 0 5px #ff6600, 0 0 10px #ff6600'
                  }}>comprehensive insights</span>.
                </p>
                <div className="flex justify-center gap-6 text-sm mt-6">
                  <span className="text-white/80" style={{
                    textShadow: '0 0 5px rgba(255,255,255,0.3)'
                  }}>Pay-as-you-go</span>
                  <span className="text-white/50">•</span>
                  <span className="text-white/80" style={{
                    textShadow: '0 0 5px rgba(255,255,255,0.3)'
                  }}>No commitments</span>
                  <span className="text-white/50">•</span>
                  <span className="text-white/80" style={{
                    textShadow: '0 0 5px rgba(255,255,255,0.3)'
                  }}>Enterprise-grade</span>
                </div>
              </div>

              {/* CTA Button */}
              <div className="text-center">
                <button 
                  className="group relative px-12 py-5 text-xl font-bold rounded-2xl overflow-hidden animate-pulse-glow hover:scale-105 transition-all duration-300"
                  style={{
                    background: 'linear-gradient(135deg, rgba(0,255,159,0.2) 0%, rgba(0,255,159,0.3) 100%)',
                    border: '2px solid #00ff9f',
                    boxShadow: '0 0 40px rgba(0,255,159,0.4), inset 0 0 20px rgba(0,255,159,0.2)',
                    animation: 'pulse-glow 2s ease-in-out infinite'
                  }}
                  onClick={() => { setCurrentStep(1); setStepFadeKey(k => k + 1); }}
                >
                  <span className="relative z-10 flex items-center gap-3">
                    <span>Enter UltrAI</span>
                    <span className="animate-slide-right">→</span>
                  </span>
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-mint-400/0 via-mint-400/30 to-mint-400/0 animate-shimmer" />
                </button>
              </div>

              {/* Trust indicators */}
              <div className="flex justify-center gap-8 text-sm text-white/60">
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
    <div className="relative flex flex-col min-h-screen w-full text-white font-cyber text-sm">
      {/* Background layer - full screen with theme */}
      <div
        className="pointer-events-none fixed inset-0"
        style={{
          backgroundImage: `url('${themeBgUrl}')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundAttachment: 'fixed',
          zIndex: 0
        }}
      />
      {/* Theme overlay tint */}
      <div className="pointer-events-none fixed inset-0" style={themeOverlayStyle} />
      
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
      <div className="relative z-10 w-full">
        <div className="flex items-center justify-center" style={{ minHeight: '100vh', paddingTop: '37.5vh' }}>
          <div className="w-full max-w-7xl px-8">
            <div className="grid grid-cols-12 gap-4">

          {/* Left Panel: System Status */}
              <div className="col-span-2">
                {/* Model Status Box */}
                <div 
                  className="glass-panel glass-grain relative p-4 rounded-2xl transition-smooth"
                  style={{ 
                    background: glassBackground,
                    backdropFilter: 'blur(40px)',
                    WebkitBackdropFilter: 'blur(40px)',
                    border: `2px solid ${colorHex}60`,
                    boxShadow: `
                      0 8px 32px rgba(0, 0, 0, 0.3),
                      0 0 20px ${colorHex}20,
                      inset 0 0 40px rgba(255, 255, 255, 0.02)
                    `,
                    clipPath: 'polygon(0 0, calc(100% - 15px) 0, 100% 15px, 100% 100%, 15px 100%, 0 calc(100% - 15px))'
                  }}
                >
                  <h3 className="text-xs font-bold text-white mb-3 uppercase tracking-wider opacity-80">System Status</h3>
                  
                  {/* Model Status */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <span style={{ color: colorHex }}>🤖</span>
                      <div className="text-[10px] font-semibold text-white">Models</div>
                    </div>
                    <div className="text-[14px] font-bold" style={{ color: colorHex }}>
                      {availableModels ? `${availableModels.filter(m => modelStatuses[m] === 'ready').length}/${availableModels.length}` : '—'}
                    </div>
                  </div>
                  
                  {/* Latency */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <span style={{ color: colorHex }}>⚡</span>
                      <div className="text-[10px] font-semibold text-white">Latency</div>
                    </div>
                    <div className="text-[14px] font-bold" style={{ color: colorHex }}>
                      <span className="animate-pulse">~2.3s</span>
                    </div>
                  </div>
                  
                  {/* Status */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span style={{ color: colorHex }}>🔄</span>
                      <div className="text-[10px] font-semibold text-white">Status</div>
                    </div>
                    <div className="text-[14px] font-bold" style={{ color: colorHex }}>
                      {availableModels && availableModels.filter(m => modelStatuses[m] === 'ready').length >= 2 ? 'Online' : 'Offline'}
                    </div>
                  </div>
                </div>

                {/* Theme Selector Box */}
                <div 
                  className="glass-panel glass-grain relative p-4 rounded-2xl transition-smooth mt-4"
                  style={{ 
                    background: glassBackground,
                    backdropFilter: 'blur(40px)',
                    WebkitBackdropFilter: 'blur(40px)',
                    border: `2px solid ${colorHex}60`,
                    boxShadow: `
                      0 8px 32px rgba(0, 0, 0, 0.3),
                      0 0 20px ${colorHex}20,
                      inset 0 0 40px rgba(255, 255, 255, 0.02)
                    `,
                    clipPath: 'polygon(0 0, calc(100% - 15px) 0, 100% 15px, 100% 100%, 15px 100%, 0 calc(100% - 15px))'
                  }}
                >
                  <h3 className="text-xs font-bold text-white mb-3 uppercase tracking-wider opacity-80">Time Theme</h3>
                  <div className="grid grid-cols-2 gap-2">
                    {(['morning', 'afternoon', 'sunset', 'night'] as const).map(t => (
                      <button key={t} 
                        onClick={() => setBgTheme(t)} 
                        className="p-2 rounded text-center transition-smooth hover:scale-105"
                        style={{ 
                          background: bgTheme===t ? `${colorHex}20` : 'rgba(255,255,255,0.05)',
                          border: bgTheme===t ? `1px solid ${colorHex}60` : '1px solid rgba(255,255,255,0.15)',
                          color: bgTheme===t ? colorHex : 'rgba(255,255,255,0.7)',
                          fontSize: '11px',
                          fontWeight: bgTheme===t ? 'bold' : 'normal',
                          textTransform: 'capitalize'
                        }}
                      >
                        {t === 'morning' ? '🌅' : t === 'afternoon' ? '☀️' : t === 'sunset' ? '🌇' : '🌙'}<br/>
                        {t}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

          {/* Wizard Panel (center) */}
              <div className="col-span-7">
                <div
                  className={`glass-panel glass-grain relative p-8 rounded-2xl overflow-hidden transition-smooth will-change-transform ${
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
              {showStatus ? (
                // Show status updater content
                <>
                  <div className="text-center mb-4">
                    <div className="text-[16px] font-extrabold tracking-[0.35em] text-white">ULTRA SYNTHESIS™</div>
                    <div className="text-[10px] text-white/70">— PROCESSING STATUS —</div>
                  </div>
                  
                  <div className="flex-1 overflow-auto">
                    <StatusUpdater />
                    
                    {isRunning && (
                      <div className="mt-6 text-center">
                        <div className="inline-flex items-center gap-3 text-[14px] text-blue-400">
                          <span className="animate-spin">⚡</span>
                          <span>Running Ultra Synthesis™ Pipeline...</span>
                          <span className="animate-spin">⚡</span>
                        </div>
                        <div className="mt-3 text-[11px] text-white/60">
                          Processing with {selectedModels.length} models
                        </div>
                      </div>
                    )}
                    
                    {!isRunning && orchestratorError && (
                      <div className="mt-6 p-4 bg-red-900/20 border-2 border-red-500/50 rounded-xl">
                        <div className="text-[14px] font-bold text-red-400 mb-2">❌ Error Occurred</div>
                        <div className="text-[12px] text-red-300">{orchestratorError}</div>
                      </div>
                    )}
                    
                    {!isRunning && orchestratorResult && (
                      <div className="mt-6 p-6 bg-gradient-to-br from-green-900/20 to-emerald-900/20 border-2 border-green-500/50 rounded-xl relative overflow-hidden">
                        {/* Success glow effect */}
                        <div className="absolute inset-0 bg-gradient-to-r from-green-400/5 via-transparent to-emerald-400/5 animate-pulse pointer-events-none" />
                        
                        <div className="relative z-10">
                          <div className="text-center mb-6">
                            <div className="inline-block animate-bounce-subtle mb-2">
                              <span className="text-3xl drop-shadow-[0_0_20px_rgba(34,197,94,0.6)]">✅</span>
                            </div>
                            <div className="text-[18px] font-bold bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent">
                              Ultra Synthesis™ Complete!
                            </div>
                            <div className="text-[12px] text-white/70 mt-1">Your results are ready</div>
                          </div>
                          
                          {/* Processing stats in cards */}
                          <div className="grid grid-cols-3 gap-3 mb-6">
                            <div className="bg-white/5 rounded-lg p-3 text-center border border-white/10">
                              <div className="text-2xl mb-1">🤖</div>
                              <div className="text-[10px] font-semibold text-white/60 uppercase tracking-wider">Models Used</div>
                              <div className="text-[14px] font-bold text-green-300 mt-1">
                                {Array.isArray(orchestratorResult.models_used) ? orchestratorResult.models_used.length : '3'}
                              </div>
                            </div>
                            <div className="bg-white/5 rounded-lg p-3 text-center border border-white/10">
                              <div className="text-2xl mb-1">⚡</div>
                              <div className="text-[10px] font-semibold text-white/60 uppercase tracking-wider">Processing Time</div>
                              <div className="text-[14px] font-bold text-blue-300 mt-1">
                                {typeof orchestratorResult.processing_time === 'number' 
                                  ? orchestratorResult.processing_time.toFixed(2) 
                                  : '1.32'}s
                              </div>
                            </div>
                            <div className="bg-white/5 rounded-lg p-3 text-center border border-white/10">
                              <div className="text-2xl mb-1">🎯</div>
                              <div className="text-[10px] font-semibold text-white/60 uppercase tracking-wider">Pattern</div>
                              <div className="text-[14px] font-bold text-purple-300 mt-1">
                                {orchestratorResult.pattern_used || 'Ultra'}
                              </div>
                            </div>
                          </div>
                          
                          {/* Selected add-ons reminder */}
                          {summary.filter(item => item.section === "5. Add-ons & formatting").length > 0 && (
                            <div className="mb-4 p-3 bg-white/5 rounded-lg border border-white/10">
                              <div className="text-[11px] font-semibold text-white/60 mb-2">Selected Add-ons:</div>
                              <div className="flex flex-wrap gap-2">
                                {summary.filter(item => item.section === "5. Add-ons & formatting").map((addon, idx) => (
                                  <span key={idx} className="text-[10px] px-2 py-1 rounded-full bg-pink-500/20 text-pink-300 border border-pink-500/30">
                                    {addon.label}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          {/* Action buttons */}
                          <div className="space-y-2">
                            <button
                              className="w-full px-4 py-3 rounded-lg font-semibold text-white transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] relative group"
                              style={{
                                background: 'linear-gradient(135deg, #00ff9f 0%, #00d4ff 100%)',
                                border: '2px solid transparent',
                                backgroundClip: 'padding-box',
                              }}
                              onClick={() => {
                                // TODO: Navigate to results view
                                console.log('View results:', orchestratorResult);
                              }}
                            >
                              <span className="relative z-10">📄 View Full Results</span>
                              <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-green-400 to-blue-400 opacity-0 group-hover:opacity-50 blur-xl transition-opacity duration-300" />
                            </button>
                            
                            <button
                              className="w-full px-3 py-2 rounded-lg font-medium text-white/70 transition-all duration-300 hover:text-white hover:bg-white/10"
                              style={{
                                border: '1px solid rgba(255,255,255,0.2)'
                              }}
                              onClick={() => {
                                // Reset for new analysis
                                setShowStatus(false);
                                setCurrentStep(0);
                                setSummary([]);
                                setTotalCost(0);
                                setOrchestratorResult(null);
                                setOrchestratorError(null);
                              }}
                            >
                              🔄 Start New Analysis
                            </button>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </>
              ) : (
                // Show normal wizard content
                <>
                  {/* Step markers (centered) - exclude Step 0 (Intro) */}
              <div className="w-full mb-4">
                <div className="flex items-center justify-center">
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
                </div>
              </div>

              <h2 
                className={`${step.color === 'mint' ? 'text-shadow-neon-mint' : step.color === 'blue' ? 'text-shadow-neon-blue' : step.color === 'deepblue' ? 'text-shadow-neon-deep' : step.color === 'purple' ? 'text-shadow-neon-purple' : 'text-shadow-neon-pink'} text-base mb-2 text-center uppercase tracking-wide`} 
                style={{ 
                  color: colorHex,
                  borderBottom: `1px solid ${colorHex}`, 
                  paddingBottom: 4,
                  textShadow: `0 0 10px ${colorHex}60, 0 0 20px ${colorHex}40`
                }}
              >
                {step.title}
              </h2>
              {step.narrative && (
                <p className="text-[11px] text-white opacity-90 mb-2 text-center whitespace-pre-line">
                  {currentStep === 2 && selectedGoals.length > 0 
                    ? `Based on your selected goals (${selectedGoals.slice(0, 3).join(', ')}${selectedGoals.length > 3 ? '...' : ''}), tell us what you need.`
                    : step.narrative}
                </p>
              )}

              {/* Scrollable options area */}
              <div
                key={stepFadeKey}
                className={`relative space-y-2 overflow-auto ${showStatus ? 'opacity-50' : ''}`}
                style={{ 
                  paddingRight: 4, 
                  paddingBottom: '80px',
                  height: 'calc(100% - 140px)',
                  pointerEvents: showStatus ? 'none' : 'auto' 
                }}
              >
                {step.type === "intro" && (
                  <>
                    <div className="text-center space-y-4">
                      <div className="inline-block">
                        <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-[#ff00de] to-[#00ffff]">Welcome to the Future</div>
                        <div className="w-24 h-1 bg-gradient-to-r from-[#ff00de] to-[#00ffff] mx-auto mt-2"></div>
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
                    <div className="w-full mt-4 flex items-center justify-center">
                      <button 
                        className="btn-neon text-lg font-extrabold transition-smooth hover:scale-105 active:scale-95" 
                        onClick={() => { setCurrentStep(1); setStepFadeKey(k => k + 1); }}
                      >
                        Enter UltrAI
                      </button>
                    </div>
                    <div className="text-center mt-3 text-[10px] text-white/50 animate-pulse">
                      Press Enter or →
                    </div>
                  </>
                )}

                {step.type === "textarea" && (<>
                  <div className="relative">
                    <textarea 
                      className="w-full h-20 glass p-3 text-white text-sm rounded-lg transition-all duration-200 hover:border-blue-400 focus:border-blue-400 focus:outline-none" 
                      style={{
                        background: queryFocused ? glassBackground : glassBackground,
                        backdropFilter: 'blur(10px)',
                        border: `2px solid ${queryFocused ? colorHex : colorHex + '50'}`,
                        resize: 'none',
                        boxShadow: queryFocused ? `0 0 20px ${colorHex}30` : 'none'
                      }}
                      placeholder={selectedGoals.length > 0 ? 
                        `Tell us about your ${selectedGoals[0].toLowerCase()} needs...` : 
                        "Type your query…"
                      } 
                      value={userQuery} 
                      onChange={(e) => setUserQuery(e.target.value)}
                      onFocus={() => setQueryFocused(true)}
                      onBlur={() => { 
                        setQueryFocused(false);
                        if (userQuery.trim()) addSelection("Query Entry", step.baseCost, step.color, step.title); 
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
                      <div className="absolute -top-6 left-0 text-[10px] animate-fade-in" style={{ color: colorHex }}>
                        <span className="animate-pulse">✨</span> AI is ready to enhance your query...
                      </div>
                    )}
                  </div>
                  
                  {step.options && (
                    <div className="grid grid-cols-2 gap-2 mt-1">
                      {step.options.map(o => (
                        <label key={o.label} className="flex items-center text-[11px] leading-tight truncate opacity-95 hover:opacity-100">
                          <input type="checkbox" onChange={() => handleInputToggle(o.label)} checked={selectedInputs.includes(o.label)} />{" "}
                          <span className="align-middle truncate tracking-wide text-white">{o.icon ? `${o.icon} ` : ""}{o.label}{typeof o.cost === 'number' ? ` ($${o.cost})` : ""}</span>
                    </label>
                  ))}
                    </div>
                  )}
                  
                  {/* Add optimization button for Step 2 */}
                  {userQuery.trim() && (
                    <div className="mt-4">
                      <button
                        className="w-full px-4 py-3 rounded-lg font-semibold transition-smooth hover:scale-[1.02] active:scale-[0.98] glass-panel"
                        style={{
                          background: 'linear-gradient(135deg, rgba(0,255,159,0.1), rgba(0,184,255,0.1))',
                          border: '2px solid rgba(0,255,159,0.5)',
                          color: '#00ff9f',
                          backdropFilter: 'blur(20px)',
                          WebkitBackdropFilter: 'blur(20px)',
                          boxShadow: '0 4px 15px rgba(0,255,159,0.2)'
                        }}
                        onClick={optimizeQuery}
                      >
                        🚀 Allow UltrAI to optimize my query
                      </button>
                      <p className="text-[10px] text-white/60 text-center mt-2">
                        AI will suggest improvements to your query for better results
                      </p>
                    </div>
                  )}
                </>)}

                {step.type === "radio" && step.options && (
                  <div className="grid grid-cols-2 gap-2">
                    {step.options.map(o => (
                      <label key={o.label} className="flex items-center text-[11px] leading-tight truncate opacity-95 hover:opacity-100">
                        <input type="radio" name={`radio-${currentStep}`} onChange={() => addSelection(o.label, o.cost, step.color, step.title)} />{" "}
                        <span className="align-middle truncate tracking-wide text-white">{o.icon ? `${o.icon} ` : ""}{o.label}{typeof o.cost === 'number' ? ` ($${o.cost})` : ""}</span>
                  </label>
                ))}
                  </div>
                )}

                {step.type === "checkbox" && step.options && (
                  currentStep === 0 ? (
                    <div className="grid grid-cols-2 gap-2">
                      {step.options.slice(0, 12).map(o => (
                        <label key={o.label} className="flex items-center text-[11px] leading-tight truncate opacity-95 hover:opacity-100">
                          <input type="checkbox" onChange={() => handleGoalToggle(o.label)} checked={selectedGoals.includes(o.label)} />{" "}
                          <span className="align-middle truncate tracking-wide text-white">{o.icon ? `${o.icon} ` : ""}{o.label}</span>
                        </label>
                      ))}
                    </div>
                  ) : (step.title || '').includes('Model selection') ? (
                    <div className="space-y-4">
                      {/* Three horizontal boxes for model selection */}
                      <div className="grid grid-cols-3 gap-2">
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
                            <div className="text-xl mb-1 transition-transform group-hover:scale-110">🎯</div>
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
                            <div className="text-xl mb-1 transition-transform group-hover:scale-110">⚡</div>
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
                            <div className="text-xl mb-1 transition-transform group-hover:scale-110">💰</div>
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
                                  <input type="checkbox" className="mr-1 scale-75" onChange={() => handleModelToggle(name)} checked={selectedModels.includes(name)} />
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
                      <div className="space-y-3">
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
                            <input
                              type="text"
                              className="w-full px-4 py-3 rounded-xl text-sm text-white placeholder-white/50"
                              placeholder="Describe your custom goal..."
                              value={otherGoalText}
                              onChange={(e) => setOtherGoalText(e.target.value)}
                              style={{
                                background: 'rgba(255, 255, 255, 0.05)',
                                backdropFilter: 'blur(20px)',
                                border: `2px solid ${colorHex}50`
                              }}
                            />
                          </div>
                        )}
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
                    <div className="grid grid-cols-2 gap-2">
                      {step.options.map(o => {
                        const comingSoon = (o.label || '').toLowerCase().includes('coming soon');
                        const isLive = !comingSoon;
                        const already = summary.some(it => it.label === o.label && it.section === step.title);
                        return (
                          <div
                            key={o.label}
                            className={`glass-panel border-2 rounded-lg p-2 transition-smooth hover:scale-[1.02] ${comingSoon ? 'opacity-30 pointer-events-none' : ''} ${already ? 'glow-' + step.color : ''}`}
                            style={{ 
                              borderColor: isLive ? colorHex : colorHex + '40',
                              background: already ? mapColorRGBA(step.color, 0.1) : 'rgba(255, 255, 255, 0.05)'
                            }}
                          >
                            <div className="text-center mb-1">
                              <div className="font-bold text-[12px] text-white">{o.icon ? `${o.icon} ` : ''}{o.label}</div>
                      </div>
                            {o.description && <div className="text-[10px] text-white/80 text-center leading-tight">{o.description}</div>}
                            {typeof o.cost === 'number' && <div className="text-[10px] text-center mt-1 text-pink-400">+${o.cost.toFixed(2)}</div>}
                            {isLive && (
                              <div className="mt-1 flex justify-center">
                                <input type="radio" name="analysis-choice" checked={already} onChange={() => { if (!already) addSelection(o.label, o.cost, step.color, step.title); }} />
                  </div>
                            )}
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
                    {currentStep===steps.length-1 ? "Submit Add-ons" : "Submit"}
                  </button>
                </div>
              )}
              </>
              )}
              </div>
            </div>
          </div>

          {/* Right Panel: Receipt transforms into Status after approval */}
          <div className="col-span-3">
            <div 
              className="glass-panel glass-grain relative p-6 rounded-2xl transition-smooth ${showStatus ? 'animate-pulse-glow' : ''}"
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
                  <div className="text-center mb-2">
                    <div className="text-[14px] font-extrabold tracking-[0.35em] text-white">ULTRAI</div>
                    <div className="text-[10px] text-white/70">— ITEMIZED RECEIPT —</div>
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
                        🚀 Initialize UltrAI
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
              ) : (
                <>
                  <div className="text-center mb-2">
                    <div className="text-[14px] font-extrabold tracking-[0.35em] text-white">ULTRAI</div>
                    <div className="text-[10px] text-white/70">— PROCESSING —</div>
              </div>
                  <div className="text-center mt-8">
                    <div className="text-[12px] text-white/60">Ultra Synthesis™ in progress</div>
                    <div className="text-[10px] text-white/40 mt-2">Check the status in the main panel</div>
                  </div>
                </>
            )}
          </div>
        </div>
          
        </div>

        {/* Status Section Below removed; status now appears in right panel after approval */}
        </div>
        </div>
      </div>
    </div>
  );
}