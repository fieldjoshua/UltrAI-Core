"use client";
import { useEffect, useState } from "react";
import { processWithFeatherOrchestration } from "../api/orchestrator";
import StatusUpdater from "./StatusUpdater";
import BridgeAnimation from "./BridgeAnimation";

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
  const [availableModels, setAvailableModels] = useState<string[] | null>(null);
  const [availableModelInfos, setAvailableModelInfos] = useState<Record<string, { provider: string; cost_per_1k_tokens: number }>>({});
  const [modelSelectionMode, setModelSelectionMode] = useState<'auto' | 'manual'>('auto');
  const [autoPreference, setAutoPreference] = useState<'cost' | 'premium' | 'speed'>('premium');
  const [selectedAddons, setSelectedAddons] = useState<string[]>([]);
  const [showStatus, setShowStatus] = useState<boolean>(false);
  const [stepFadeKey, setStepFadeKey] = useState(0);
  const [userQuery, setUserQuery] = useState<string>("");
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [orchestratorResult, setOrchestratorResult] = useState<any>(null);
  const [orchestratorError, setOrchestratorError] = useState<string | null>(null);
  const [isOptimizing, setIsOptimizing] = useState<boolean>(false);
  const [optimizationStep, setOptimizationStep] = useState<number>(0);
  const [modelStatuses, setModelStatuses] = useState<Record<string, 'checking' | 'ready' | 'error'>>({});
  const [billboardState, setBillboardState] = useState<'idle' | 'processing' | 'complete'>('idle');
  const [billboardMessage, setBillboardMessage] = useState<string>('');

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
        setBillboardState('processing');
        setBillboardMessage('Initializing Ultra Synthesis™ Pipeline...');
        const models = selectedModels.length > 0 ? selectedModels : null;
        const res = await processWithFeatherOrchestration({
          prompt: userQuery || "",
          models,
          pattern: "comparative",
          ultraModel: null,
          outputFormat: "plain",
        });
        setOrchestratorResult(res);
        console.log("Ultra Synthesis result", res);
        setBillboardState('complete');
        setBillboardMessage('Ultra Synthesis™ Complete!');
      } catch (e: any) {
        console.error("Ultra Synthesis failed", e);
        setOrchestratorError(e?.message || String(e));
        setBillboardState('idle');
        setBillboardMessage('');
      } finally {
        setIsRunning(false);
      }
    })();
  }, [showStatus]);

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

  const monoStack = 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace';

  // Step 0: Intro — render with background and billboard
  if (currentStep === 0 && step.type === 'intro') {
    return (
      <div className="no-anim relative flex min-h-screen w-full items-start justify-center p-0 text-white font-cyber text-sm overflow-hidden">
        {/* Background with billboard */}
        <div className="absolute inset-0">
          <div
            className="absolute inset-0"
            style={{
              backgroundImage: "url('/cityscape-background.jpeg'), url('/ultrai-bg.jpg')",
              backgroundSize: 'cover',
              backgroundPosition: 'center',
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/80" />
        </div>

        {/* Hero content below billboard */}
        <div className="relative z-10 w-full mx-auto max-w-5xl px-8" style={{ marginTop: '35vh' }}>

          {/* Main card */}
          <div
            className="relative p-8 rounded-3xl overflow-hidden"
            style={{ 
              background: 'rgba(0, 0, 0, 0.7)',
              backdropFilter: 'blur(20px)',
              border: '2px solid rgba(0,255,159,0.3)',
              boxShadow: '0 0 80px rgba(0,255,159,0.2), inset 0 0 60px rgba(0,255,159,0.05)'
            }}
          >

            <div className="relative space-y-8">
              {/* Feature pills */}
              <div className="flex flex-wrap gap-3 justify-center">
                <span className="px-6 py-2 rounded-full text-sm font-semibold bg-mint-400/20 text-mint-400 border border-mint-400/50 backdrop-blur">
                  🚀 Multi-Model Orchestration
                </span>
                <span className="px-6 py-2 rounded-full text-sm font-semibold bg-blue-400/20 text-blue-400 border border-blue-400/50 backdrop-blur">
                  ⚡ Real-time Synthesis
                </span>
                <span className="px-6 py-2 rounded-full text-sm font-semibold bg-purple-400/20 text-purple-400 border border-purple-400/50 backdrop-blur">
                  🎯 Intelligent Optimization
                </span>
                <span className="px-6 py-2 rounded-full text-sm font-semibold bg-pink-400/20 text-pink-400 border border-pink-400/50 backdrop-blur">
                  💎 Premium Results
                </span>
              </div>

              {/* Main narrative */}
              <div className="max-w-3xl mx-auto">
                <p className="text-lg leading-relaxed text-center text-white/90">
                  Welcome to <span className="font-bold text-mint-400">UltrAI</span> where the intelligence of multiple LLMs is multiplied. 
                  We orchestrate a sophisticated ensemble of leading AI models, each contributing their unique strengths 
                  to deliver <span className="font-bold text-blue-400">unprecedented quality</span> and <span className="font-bold text-purple-400">comprehensive insights</span>.
                </p>
                <p className="text-md text-center text-white/70 mt-4">
                  Pay-as-you-go • No commitments • Enterprise-grade results
                </p>
              </div>

              {/* CTA Button */}
              <div className="text-center">
                <button 
                  className="group relative px-12 py-5 text-xl font-bold rounded-2xl"
                  style={{
                    background: 'linear-gradient(135deg, rgba(0,255,159,0.2) 0%, rgba(0,255,159,0.3) 100%)',
                    border: '2px solid #00ff9f',
                    boxShadow: '0 0 40px rgba(0,255,159,0.4), inset 0 0 20px rgba(0,255,159,0.2)'
                  }}
                  onClick={() => { setCurrentStep(1); setStepFadeKey(k => k + 1); }}
                >
                  <span className="relative z-10 flex items-center gap-3">
                    <span>Enter Ultra Synthesis™</span>
                    <span>→</span>
                  </span>
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-mint-400/20 to-mint-400/30" />
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
    );
  }

  const chooseAutoModels = (pref: 'cost'|'premium'|'speed', names: string[] | null): string[] => {
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
  };

  const optimizeSearch = () => {
    setIsOptimizing(true);
    setOptimizationStep(0);
    setBillboardState('processing');
    setBillboardMessage('AI Optimization in Progress...');
    
    // Step through optimization phases
    const runOptimization = async () => {
      // Step 1: Analyze query
      setOptimizationStep(1);
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // Clear previous selections except any manually selected goals
      const existingGoals = [...selectedGoals];
      setSummary([]);
      setTotalCost(0);
      setSelectedInputs([]);
      setSelectedModels([]);
      setSelectedAddons([]);
      
      // Base cost for query entry
      addSelection("Query Entry", 0, "blue");
    
    // Analyze query to determine relevant goals
    const query = userQuery.toLowerCase();
    const goalMap: Record<string, string[]> = {
      "Document Analysis": ["analyze", "document", "pdf", "report", "review", "examine", "read"],
      "Deep Research": ["research", "investigate", "study", "explore", "find", "discover", "learn"],
      "Academic Research & Citations": ["academic", "paper", "citation", "journal", "thesis", "scholarly", "peer-reviewed"],
      "Writing & Editing Assistance": ["write", "edit", "draft", "compose", "rewrite", "proofread", "improve"],
      "Brainstorming & Ideation": ["idea", "brainstorm", "creative", "suggest", "concept", "innovate", "think"],
      "Code Creation / Debugging": ["code", "debug", "program", "script", "function", "bug", "error", "python", "javascript", "java"],
      "Data Analysis & Visualization": ["data", "analyze", "chart", "graph", "statistics", "metrics", "visualization"],
      "Media Generation (Image/Video/Text)": ["image", "video", "generate", "create", "design", "visual", "artwork"],
      "Personal Organization": ["organize", "plan", "schedule", "todo", "list", "manage", "track"],
      "Internet Search": ["search", "find", "lookup", "google", "web", "online", "internet"],
      "Event Planning": ["event", "meeting", "conference", "party", "wedding", "gathering", "occasion"],
      "Travel Planning": ["travel", "trip", "vacation", "flight", "hotel", "itinerary", "destination"],
      "News Gathering": ["news", "current", "latest", "today", "happening", "events", "updates"],
      "Social Media Post Creation": ["social", "post", "twitter", "linkedin", "facebook", "instagram", "content"],
      "Customer Support Drafts": ["support", "customer", "help", "service", "response", "reply", "answer"]
    };
    
    // Select relevant goals based on query keywords
    const autoSelectedGoals: string[] = [];
    Object.entries(goalMap).forEach(([goal, keywords]) => {
      if (keywords.some(keyword => query.includes(keyword))) {
        autoSelectedGoals.push(goal);
      }
    });
    
    // If no specific goals matched, select general ones based on query structure
    if (autoSelectedGoals.length === 0) {
      if (query.includes("?") || query.includes("how") || query.includes("what") || query.includes("why")) {
        autoSelectedGoals.push("Deep Research");
      }
      if (query.length > 100 || query.includes("help me") || query.includes("create") || query.includes("make")) {
        autoSelectedGoals.push("Writing & Editing Assistance");
      }
      // If still no matches, use defaults
      if (autoSelectedGoals.length === 0) {
        autoSelectedGoals.push("Deep Research", "Writing & Editing Assistance");
      }
    }
    
    // Combine existing manual selections with auto-selected goals
    const allGoals = [...new Set([...existingGoals, ...autoSelectedGoals])];
    setSelectedGoals(allGoals);
    
    // Step 2: Select goals
    setOptimizationStep(2);
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // Add all goals to the receipt
    allGoals.forEach(goal => {
      addSelection(goal, 0, "mint");
    });
    
    // Always select UltrAI Intelligence Multiplier
    addSelection("UltrAI Intelligence Multiplier", 0.08, "purple");
    
    // Step 3: Choose models
    setOptimizationStep(3);
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // Auto-select models based on query complexity and content
    let modelPreference: 'cost' | 'premium' | 'speed' = 'premium';
    
    // Check for specific indicators
    if (query.length < 50 || query.includes("quick") || query.includes("simple") || query.includes("fast")) {
      modelPreference = 'speed';
    } else if (query.includes("budget") || query.includes("cheap") || query.includes("economical")) {
      modelPreference = 'cost';
    } else if (query.includes("comprehensive") || query.includes("detailed") || query.includes("thorough") || 
               allGoals.includes("Academic Research & Citations") || allGoals.includes("Code Creation / Debugging")) {
      modelPreference = 'premium';
    }
    
    const autoModels = chooseAutoModels(modelPreference, availableModels);
    setSelectedModels(autoModels);
    const modelsCost = autoModels.reduce((sum, n) => sum + (availableModelInfos[n]?.cost_per_1k_tokens || 0), 0) * 0.1; // Estimate 0.1 for 1k tokens usage
    addSelection(`Auto (${modelPreference}): ${autoModels.join(', ')}`, modelsCost, "deepblue");
    
    // Select formatting options based on query and selected goals
    const formatOptions: string[] = [];
    
    if (query.includes("pdf") || query.includes("document") || allGoals.includes("Document Analysis")) {
      formatOptions.push("PDF / Word / Markdown / Plain Text");
      addSelection("PDF / Word / Markdown / Plain Text", 0.02, "pink");
    }
    
    if (query.includes("data") || query.includes("csv") || query.includes("json") || allGoals.includes("Data Analysis & Visualization")) {
      formatOptions.push("JSON / CSV Export");
      addSelection("JSON / CSV Export", 0.02, "pink");
    }
    
    if (query.includes("summary") || query.includes("summarize") || query.includes("brief")) {
      formatOptions.push("Summarize / Expand");
      addSelection("Summarize / Expand", 0.06, "pink");
    }
    
    if (allGoals.includes("Academic Research & Citations")) {
      formatOptions.push("Fact-check Confidence Report");
      addSelection("Fact-check Confidence Report", 0.05, "pink");
    }
    
    if (query.includes("private") || query.includes("confidential") || query.includes("secure")) {
      formatOptions.push("Data Privacy Mode (strip PII)");
      addSelection("Data Privacy Mode (strip PII)", 0.04, "pink");
    }
    
    // If no specific format selected, add a default based on goals
    if (formatOptions.length === 0) {
      addSelection("PDF / Word / Markdown / Plain Text", 0.02, "pink");
    }
    
      // Step 4: Select formatting
      setOptimizationStep(4);
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // Move to the last step
      setCurrentStep(steps.length - 1);
      setStepFadeKey(k => k + 1);
      setIsOptimizing(false);
      setOptimizationStep(0);
      setBillboardState('idle');
      setBillboardMessage('');
    };
    
    runOptimization();
  };


  return (
    <div className="relative flex flex-col min-h-screen w-full text-white font-cyber text-sm">
      {/* Background layer */}
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          backgroundImage: "url('/cityscape-background.jpeg'), url('/ultrai-bg.jpg')",
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          zIndex: 0
        }}
      />
      
      {/* Animated Billboard Lines - Lower Right Corner */}
      <div 
        className="pointer-events-none fixed inset-0"
        style={{ zIndex: 3 }}
      >
        <img
          src="/overlays/billboard_lines.svg"
          alt=""
          className="absolute inset-0 w-full h-full"
          style={{
            objectFit: 'cover',
            objectPosition: 'bottom right',
            opacity: 0.22,
            filter: 'brightness(1.2)'
          }}
        />
      </div>
      
      {/* Bridge Animation - Lower Left Corner */}
      {/* Bridge animation disabled for professional static look */}
      
      {/* Optimization Status Boxes */}
      {isOptimizing && (
        <div className="absolute w-full" style={{ top: '10vh', zIndex: 5 }}>
          <div className="max-w-4xl mx-auto px-8">
            <div className="glass-strong p-4 rounded-xl" style={{ 
              background: 'rgba(0, 0, 0, 0.75)', 
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.1)'
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

      {/* Model Status Panel - Top Right */}
      {availableModels && availableModels.length > 0 && (
        <div className="absolute right-4 z-20" style={{ top: '20px' }}>
          <div className="glass p-3 rounded-lg" style={{ background: 'rgba(0, 0, 0, 0.7)', backdropFilter: 'blur(10px)' }}>
            <div className="text-[11px] font-bold mb-2 text-white/80">AI Models Status</div>
            <div className="space-y-1">
              {Object.entries(modelStatuses).slice(0, 5).map(([model, status]) => (
                <div key={model} className="flex items-center gap-2 text-[10px]">
                  <div className={`w-2 h-2 rounded-full ${status === 'ready' ? 'bg-green-400' : status === 'checking' ? 'bg-yellow-400 animate-pulse' : 'bg-red-400'}`} />
                  <span className="text-white/70">{model.split('-')[0]}</span>
                </div>
              ))}
              {Object.keys(modelStatuses).length > 5 && (
                <div className="text-[9px] text-white/50 mt-1">+{Object.keys(modelStatuses).length - 5} more ready</div>
              )}
            </div>
            <div className="mt-2 pt-2 border-t border-white/10">
              <div className="flex items-center gap-2 text-[10px] text-green-400">
                <div className="w-2 h-2 rounded-full bg-green-400" />
                <span>{Object.values(modelStatuses).filter(s => s === 'ready').length} models ready</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content - Below Billboard */}
      <div className="relative z-10 w-full">
        <div className="flex items-center justify-center min-h-screen py-20">
          <div className="w-full max-w-6xl px-8">
            <div className="grid grid-cols-12 gap-8">
              
              {/* Wizard Panel (left) */}
              <div className="col-span-8">
                <div
                  className={`relative p-8 rounded-2xl transition-all duration-300 overflow-hidden`}
                  style={{
                    background: 'rgba(0, 0, 0, 0.85)',
                    backdropFilter: 'blur(20px)',
                    border: `1px solid rgba(255, 255, 255, 0.1)`,
                    minHeight: '450px',
                    boxShadow: `
                      0 4px 24px rgba(0, 0, 0, 0.5),
                      0 0 60px ${colorHex}10,
                      0 0 0 1px ${colorHex}33
                    `,
                    clipPath: 'polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 20px 100%, 0 calc(100% - 20px))'
                  }}
                >
              <div className="flex flex-col h-full">
              {/* Step markers (centered) */}
              <div className="w-full mb-4">
                <div className="flex items-center justify-center">
                  {steps.map((s, i) => {
                    const isActive = i === currentStep;
                    const isDone = i < currentStep;
                    const dotHex = mapColorHex(s.color);
                    return (
                      <div key={i} className="flex items-center">
                        <div 
                          onClick={() => { setCurrentStep(i); setStepFadeKey(k => k+1); }} 
                          className="relative cursor-pointer group"
                        >
                          <div 
                            className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 ${
                              isActive ? 'scale-110' : 'hover:scale-105'
                            }`}
                            style={{ 
                              backgroundColor: isActive ? `${dotHex}20` : isDone ? `${dotHex}15` : 'rgba(255,255,255,0.05)',
                              border: `2px solid ${isActive ? dotHex : isDone ? dotHex : 'rgba(255,255,255,0.2)'}`,
                              boxShadow: isActive ? `0 0 0 4px ${dotHex}20, 0 0 20px ${dotHex}40` : 'none'
                            }}
                          >
                            <span className="text-[10px] font-bold" style={{ color: isActive || isDone ? dotHex : 'rgba(255,255,255,0.5)' }}>
                              {i + 1}
                            </span>
                          </div>
                          {/* Tooltip */}
                          <div className="absolute -bottom-6 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
                            <div className="text-[9px] whitespace-nowrap bg-black/80 px-2 py-1 rounded" style={{ color: dotHex }}>
                              {s.title.split('. ')[1]}
                            </div>
                          </div>
                        </div>
                        {i < steps.length - 1 && (
                          <div 
                            className="w-12 h-0.5 mx-2 transition-all duration-300" 
                            style={{ 
                              backgroundColor: i < currentStep ? dotHex : 'rgba(255,255,255,0.2)',
                              boxShadow: i < currentStep ? `0 0 10px ${dotHex}50` : 'none'
                            }} 
                          />
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              <h2 className={`text-white ${step.color === 'mint' ? 'text-shadow-neon-mint' : step.color === 'blue' ? 'text-shadow-neon-blue' : step.color === 'deepblue' ? 'text-shadow-neon-deep' : step.color === 'purple' ? 'text-shadow-neon-purple' : 'text-shadow-neon-pink'} text-base mb-2 text-center uppercase tracking-wide`} style={{ borderBottom: `1px solid ${colorHex}`, paddingBottom: 4 }}>{step.title}</h2>
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
                className={`relative space-y-2 mb-2 animate-fade-in flex-1 overflow-auto ${showStatus ? 'opacity-50' : ''}`}
                style={{ paddingRight: 4, pointerEvents: showStatus ? 'none' : 'auto' }}
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
                      <button className="btn-neon text-lg font-extrabold" onClick={() => { setCurrentStep(1); setStepFadeKey(k => k + 1); }}>
                        Start UltrAI!
                      </button>
                    </div>
                  </>
                )}

                {step.type === "textarea" && (<>
                  <textarea 
                    className="w-full h-20 glass p-3 text-white text-sm rounded-lg transition-all duration-200 hover:border-blue-400 focus:border-blue-400 focus:outline-none" 
                    style={{
                      background: 'rgba(0, 0, 0, 0.3)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      resize: 'none'
                    }}
                    placeholder={selectedGoals.length > 0 ? 
                      `Tell us about your ${selectedGoals[0].toLowerCase()} needs...` : 
                      "Type your query…"
                    } 
                    value={userQuery} 
                    onChange={(e) => setUserQuery(e.target.value)} 
                    onBlur={() => { if (userQuery.trim()) addSelection("Query Entry", step.baseCost, step.color); }}
                  />
                  
                  {/* Add "Allow UltrAI to optimize my search" button after query input */}
                  {userQuery && userQuery.trim().length > 0 && (
                    <div className="mt-3">
                      <button
                        className="w-full px-4 py-3 rounded-lg text-center font-semibold transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
                        style={{ 
                          border: '2px solid #00ff9f', 
                          color: '#00ff9f', 
                          background: 'linear-gradient(135deg, rgba(0,255,159,0.1) 0%, rgba(0,255,159,0.15) 100%)',
                          boxShadow: '0 0 20px rgba(0,255,159,0.2), inset 0 0 20px rgba(0,255,159,0.05)'
                        }}
                        onClick={() => optimizeSearch()}
                        disabled={isOptimizing}
                      >
                        {isOptimizing ? (
                          <span className="flex items-center justify-center gap-2">
                            <span className="inline-block animate-spin">⚡</span>
                            <span>AI is optimizing your search...</span>
                          </span>
                        ) : (
                          <span className="flex items-center justify-center gap-2">
                            <span>🚀</span>
                            <span>Let AI optimize my search automatically</span>
                          </span>
                        )}
                      </button>
                      <p className="text-[10px] text-center mt-1 opacity-60">
                        AI will analyze your query and select the best options for you
                      </p>
                    </div>
                  )}
                  
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
                </>)}

                {step.type === "radio" && step.options && (
                  <div className="grid grid-cols-2 gap-2">
                    {step.options.map(o => (
                      <label key={o.label} className="flex items-center text-[11px] leading-tight truncate opacity-95 hover:opacity-100">
                        <input type="radio" name={`radio-${currentStep}`} onChange={() => addSelection(o.label, o.cost, step.color)} />{" "}
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
                    <div className="space-y-2">
                      {/* Auto/Manual grouped boxes */}
                      <div className="grid grid-cols-2 gap-2">
                        <div className="glass p-2 rounded-xl border border-white/20">
                          <div className="text-[11px] uppercase tracking-wider mb-1 opacity-80">Auto selection</div>
                        <button
                          className="px-2 py-1 text-[11px] rounded border border-white/30 hover:border-white/60"
                          onClick={() => {
                            setModelSelectionMode('auto');
                            setAutoPreference('cost');
                            const picks = chooseAutoModels('cost', availableModels);
                            setSelectedModels(picks);
                            const est = picks.reduce((sum, n) => sum + (availableModelInfos[n]?.cost_per_1k_tokens || 0), 0);
                            addSelection(`Auto (Cost-Saving): ${picks.join(', ')}`, est, step.color);
                          }}
                        >Auto: Cost-Saving</button>
                        <button
                          className="px-2 py-1 text-[11px] rounded border border-white/30 hover:border-white/60"
                          onClick={() => {
                            setModelSelectionMode('auto');
                            setAutoPreference('premium');
                            const picks = chooseAutoModels('premium', availableModels);
                            setSelectedModels(picks);
                            const est = picks.reduce((sum, n) => sum + (availableModelInfos[n]?.cost_per_1k_tokens || 0), 0);
                            addSelection(`Auto (Premium): ${picks.join(', ')}`, est, step.color);
                          }}
                        >Auto: Premium Quality</button>
                        <button
                          className="px-2 py-1 text-[11px] rounded border border-white/30 hover:border-white/60"
                          onClick={() => {
                            setModelSelectionMode('auto');
                            setAutoPreference('speed');
                            const picks = chooseAutoModels('speed', availableModels);
                            setSelectedModels(picks);
                            const est = picks.reduce((sum, n) => sum + (availableModelInfos[n]?.cost_per_1k_tokens || 0), 0);
                            addSelection(`Auto (Speed): ${picks.join(', ')}`, est, step.color);
                          }}
                        >Auto: Speed</button>
                        </div>
                        <div className="glass p-2 rounded-xl border border-white/20">
                          <div className="text-[11px] uppercase tracking-wider mb-1 opacity-80">Manual selection</div>
                        <button
                          className="px-2 py-1 text-[11px] rounded border border-white/30 hover:border-white/60"
                          onClick={() => setModelSelectionMode('manual')}
                        >Open manual list</button>
                        {modelSelectionMode === 'manual' && (
                          <div className={'grid grid-cols-2 gap-1 mt-2'}>
                            {(availableModels || []).map(name => (
                              <label key={name} className="flex items-center text-[11px] leading-tight truncate opacity-95 hover:opacity-100">
                                <input type="checkbox" onChange={() => handleModelToggle(name)} checked={selectedModels.includes(name)} />{" "}
                                <span className="align-middle truncate tracking-wide text-white">{name} {availableModelInfos[name] ? `( $${availableModelInfos[name].cost_per_1k_tokens}/1k )` : ''}</span>
                              </label>
                            ))}
                            {availableModels && availableModels.length === 0 && (
                              <div className="text-[11px] opacity-80">No models available. Add API keys to enable models.</div>
                            )}
                          </div>
                        )}
                        </div>
                      </div>

                      {modelSelectionMode !== 'manual' && (
                        <div className="text-[11px] opacity-80 mt-2">Selected (Auto - {autoPreference}): {selectedModels.join(', ') || 'None yet'}</div>
                      )}
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 gap-2">
                      {step.options.map(o => (
                        <label key={o.label} className="flex items-center text-[11px] leading-tight truncate opacity-95 hover:opacity-100">
                          <input type="checkbox" onChange={e => e.target.checked ? addSelection(o.label, o.cost, step.color) : removeSelectionCost(o.cost)} />{" "}
                          <span className="align-middle truncate tracking-wide text-white">{o.icon ? `${o.icon} ` : ""}{o.label}{typeof o.cost === 'number' ? ` ($${o.cost})` : ""}</span>
                        </label>
                      ))}
                    </div>
                  )
                )}

                {step.type === "groupbox" && step.options && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {step.options.map(o => {
                      const comingSoon = (o.label || '').toLowerCase().includes('coming soon');
                      return (
                        <div
                          key={o.label}
                          className={`glass border-2 rounded-xl p-2 animate-border-hum ${comingSoon ? 'opacity-30 pointer-events-none' : ''}`}
                          style={{ borderColor: comingSoon ? 'rgba(255,255,255,0.2)' : colorHex }}
                        >
                          <div className="text-center font-bold text-[13px] mb-1 text-white">{o.icon ? `${o.icon} ` : ''}{o.label}</div>
                          {o.description && <div className="text-[11px] text-white/80 text-center leading-snug">{o.description}</div>}
                          {typeof o.cost === 'number' && <div className="text-[11px] text-center mt-1 text-pink-400">+${o.cost.toFixed(2)}</div>}
                        </div>
                      );
                    })}
                  </div>
                )}

              </div>

              {/* Action buttons (sticky footer inside panel) */}
              <div className="mt-auto sticky bottom-0 pt-1" style={{ background: 'linear-gradient(to top, rgba(0,0,0,0.35), rgba(0,0,0,0))' }}>
                {(step.type === 'checkbox' || step.type === 'textarea' || step.type === 'radio') && currentStep !== 4 && currentStep !== 0 && (
                  <button
                    className="w-full mt-1 px-3 py-2 rounded text-center font-semibold shadow-neon-mint animate-border-hum"
                    style={{ border: '2px solid #00ff9f', color: '#00ff9f', background: 'rgba(0,255,159,0.08)' }}
                    onClick={() => addSelection("Auto: Let UltrAI Optimize My Query", 0, step.color)}
                  >
                    Auto: Let UltrAI Optimize My Query
                  </button>
                )}

                <button
                  className="w-full mt-2 px-3 py-2 rounded text-center font-semibold animate-border-hum"
                  style={{ border: `2px solid ${colorHex}`, color: colorHex, background: mapColorRGBA(step.color, 0.06) }}
                  onClick={() => {
                    if (currentStep === steps.length - 1) {
                      setShowStatus(true);
                    } else {
                      setCurrentStep(Math.min(currentStep + 1, steps.length - 1));
                      setStepFadeKey(k => k + 1);
                    }
                  }}
                >
                  {currentStep===steps.length-1 ? "Finish" : "Submit"}
                </button>
              </div>
              </div>
            </div>
          </div>

          {/* Receipt Panel (right) */}
          <div className="col-span-4">
            <div 
              className="relative p-6 rounded-2xl"
              style={{ 
                fontFamily: monoStack, 
                background: 'rgba(0, 0, 0, 0.85)',
                backdropFilter: 'blur(20px)',
                border: `1px solid rgba(255, 255, 255, 0.1)`,
                minHeight: '450px',
                boxShadow: `
                  0 4px 24px rgba(0, 0, 0, 0.5),
                  0 0 40px ${receiptColor}10,
                  0 0 0 1px ${receiptColor}33
                `,
                clipPath: 'polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 20px 100%, 0 calc(100% - 20px))'
              }}>
            <div className="text-center mb-2">
              <div className="text-[14px] font-extrabold tracking-[0.35em] text-white text-shadow-neon-blue">ULTRAI</div>
              <div className="text-[10px] text-white/70">— ITEMIZED RECEIPT —</div>
            </div>
            <div className="space-y-2">
              {['mint','blue','deepblue','purple','pink'].map(groupColor => {
                const items = summary.filter(s => s.color === groupColor);
                if (items.length === 0) return null;
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
            <div className="mt-3 font-bold text-pink-400 text-lg text-center">{`Total: $${totalCost.toFixed(2)}`}</div>
            </div>
          </div>
          
        </div>

        {/* Status Section Below */}
        <div className="grid grid-cols-12 gap-8 mt-8">
          <div className="col-start-4 col-span-5">
            {currentStep===steps.length-1 && !showStatus && (
              <div className="animate-fade-in">
                <button
                  className="w-full px-6 py-4 rounded-xl text-center font-bold transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
                  style={{ 
                    border: '3px solid #00ff9f', 
                    color: '#fff', 
                    background: 'linear-gradient(135deg, rgba(0,255,159,0.2) 0%, rgba(0,255,159,0.3) 100%)', 
                    fontSize: '16px',
                    boxShadow: '0 0 30px rgba(0,255,159,0.4), inset 0 0 30px rgba(0,255,159,0.1)'
                  }}
                  onClick={() => setShowStatus(true)}
                >
                  🚀 Commence Ultra Synthesis™
                </button>
              </div>
            )}
            {showStatus && (
              <div className="glass-strong p-4 rounded-xl border-2 animate-border-hum" style={{ 
                borderColor: colorHex, 
                background: 'rgba(0, 0, 0, 0.8)',
                backdropFilter: 'blur(20px)',
                boxShadow: `0 0 0 2px rgba(255,255,255,0.08) inset, 0 0 14px ${colorHex}` 
              }}>
                <StatusUpdater />
                {isRunning && (
                  <div className="flex items-center gap-2 text-[12px] text-blue-400 mt-3">
                    <span className="animate-spin">⚡</span>
                    <span>Running Ultra Synthesis™ Pipeline...</span>
                  </div>
                )}
                {!isRunning && orchestratorError && (
                  <div className="mt-3 p-2 bg-red-900/20 border border-red-500/50 rounded text-[11px] text-red-400">
                    <strong>Error:</strong> {orchestratorError}
                  </div>
                )}
                {!isRunning && orchestratorResult && (
                  <div className="mt-3 p-3 bg-green-900/20 border border-green-500/50 rounded">
                    <div className="text-[12px] font-bold text-green-400 mb-2">✅ Ultra Synthesis™ Complete!</div>
                    <div className="space-y-1 text-[11px]">
                      <div className="text-white/80">
                        <strong>Models used:</strong> {Array.isArray(orchestratorResult.models_used) ? orchestratorResult.models_used.join(', ') : 'Multiple'}
                      </div>
                      <div className="text-white/80">
                        <strong>Processing time:</strong> {orchestratorResult.processing_time?.toFixed?.(2) || orchestratorResult.processing_time}s
                      </div>
                      <div className="text-white/80">
                        <strong>Analysis pattern:</strong> {orchestratorResult.pattern_used || 'Comparative'}
                      </div>
                    </div>
                    {orchestratorResult.ultra_response && (
                      <div className="mt-3 pt-3 border-t border-white/10">
                        <div className="text-[11px] font-bold text-white/90 mb-1">Result Preview:</div>
                        <div className="text-[10px] text-white/70 line-clamp-3">
                          {orchestratorResult.ultra_response.substring(0, 200)}...
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
        </div>
        </div>
      </div>
    </div>
  );
}