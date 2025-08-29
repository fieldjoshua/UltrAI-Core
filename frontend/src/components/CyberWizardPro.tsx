"use client";
import { useEffect, useState } from "react";
import { processWithFeatherOrchestration } from "../api/orchestrator";
import StatusUpdater from "./StatusUpdater";
import BridgeAnimation from "./BridgeAnimation";
import "../styles/cyberpunk-vars.css";

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

// Design system constants
const SPACING = {
  xs: '0.5rem',
  sm: '1rem',
  md: '1.5rem',
  lg: '2rem',
  xl: '3rem'
};

const FONTS = {
  mono: "'JetBrains Mono', 'Fira Code', monospace",
  sans: "'Inter', -apple-system, sans-serif"
};

const COLORS = {
  mint: '#00ff9f',
  blue: '#00b8ff',
  deepblue: '#001eff',
  purple: '#bd00ff',
  pink: '#d600ff',
  cyber: '#00ffff',
  text: {
    primary: 'rgba(255, 255, 255, 0.9)',
    secondary: 'rgba(255, 255, 255, 0.7)',
    muted: 'rgba(255, 255, 255, 0.5)'
  }
};

export default function CyberWizardPro() {
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

  // Load wizard steps
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

  // Load available models
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
            statusMap[String(m.name)] = 'ready';
          });
          setAvailableModelInfos(infoMap);
          setModelStatuses(statusMap);
        }
      } catch (e) {
        console.error("Failed to load available models", e);
        setAvailableModels([]);
      }
    };
    fetchAvailable();
  }, []);

  if (steps.length === 0) return <div>Loading…</div>;

  const step = steps[currentStep];
  const getStepColor = (color: string) => COLORS[color as keyof typeof COLORS] || COLORS.cyber;
  const currentColor = getStepColor(step.color);

  // Professional Panel Component
  const Panel = ({ children, className = "", style = {} }: any) => (
    <div
      className={`relative ${className}`}
      style={{
        background: 'rgba(0, 0, 0, 0.85)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        padding: SPACING.lg,
        fontFamily: FONTS.sans,
        ...style,
        clipPath: 'polygon(0 0, calc(100% - 16px) 0, 100% 16px, 100% 100%, 16px 100%, 0 calc(100% - 16px))',
        boxShadow: `
          0 4px 24px rgba(0, 0, 0, 0.5),
          inset 0 0 60px rgba(0, 0, 0, 0.3),
          0 0 0 1px ${currentColor}33
        `
      }}
    >
      {/* Corner accents */}
      <div className="absolute top-0 right-0 w-4 h-4" style={{ 
        borderTop: `1px solid ${currentColor}66`,
        borderRight: `1px solid ${currentColor}66`
      }} />
      <div className="absolute bottom-0 left-0 w-4 h-4" style={{ 
        borderBottom: `1px solid ${currentColor}66`,
        borderLeft: `1px solid ${currentColor}66`
      }} />
      {children}
    </div>
  );

  return (
    <div className="relative flex min-h-screen w-full text-white" style={{ 
      fontFamily: FONTS.sans,
      background: '#0a0a0f'
    }}>
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
      <div className="pointer-events-none fixed inset-0" style={{ zIndex: 3 }}>
        <img
          src="/overlays/billboard_lines.svg"
          alt=""
          className="absolute inset-0 w-full h-full"
          style={{
            objectFit: 'cover',
            objectPosition: 'bottom right',
            opacity: billboardState === 'processing' ? 0.4 : 0.2,
            filter: `brightness(${billboardState === 'processing' ? 1.8 : 1.2}) ${billboardState === 'processing' ? 'drop-shadow(0 0 20px #00ff00)' : ''}`,
            animation: billboardState === 'processing' ? 'billboardPulse 2s ease-in-out infinite' : 'none',
            transition: 'all 0.5s ease'
          }}
        />
      </div>
      
      {/* Bridge Animation - Lower Left Corner */}
      <BridgeAnimation state={billboardState} />
      
      {/* Boxes Template Overlay - for positioning reference */}
      <div className="fixed inset-0 pointer-events-none" style={{ zIndex: 5, opacity: 0.3 }}>
        <img src="/overlays/boxes_template.svg" className="w-full h-full" />
      </div>
      
      {/* Main Content - Positioned according to SVG template */}
      <div className="fixed inset-0 pointer-events-none" style={{ zIndex: 10 }}>
        {/* Calculate positions based on SVG viewBox (3800.17 x 2221.37) */}
        <div className="relative w-full h-full">
          
          {/* Yellow Strip - Vertical header (x:8.23, y:8.75, w:197.18, h:2189.3) */}
          <div 
            className="absolute pointer-events-auto"
            style={{
              left: '0.2%',
              top: '0.4%',
              width: '5.2%',
              height: '98.5%'
            }}
          >
            <Panel style={{ height: '100%', padding: SPACING.sm, writingMode: 'vertical-rl' }}>
              <h1 style={{
                fontFamily: FONTS.mono,
                fontSize: '24px',
                fontWeight: 800,
                color: COLORS.cyber,
                textOrientation: 'mixed',
                letterSpacing: '0.3em'
              }}>
                ULTRAI
              </h1>
            </Panel>
          </div>
          
          {/* Main Wizard Panel - Pink box (x:1203.54, y:906.22, w:1697.52, h:605.38) */}
          <div 
            className="absolute pointer-events-auto"
            style={{
              left: '31.7%',
              top: '40.8%',
              width: '44.7%',
              height: '27.2%'
            }}
          >
            <Panel style={{ height: '100%' }}>
                  {/* Step Progress Bar */}
                  <div className="flex items-center justify-between mb-6">
                    {steps.map((s, i) => {
                      const isActive = i === currentStep;
                      const isDone = i < currentStep;
                      const stepColor = getStepColor(s.color);
                      return (
                        <div key={i} className="flex items-center flex-1">
                          <button 
                            onClick={() => { setCurrentStep(i); setStepFadeKey(k => k+1); }} 
                            className="group relative w-12 h-12 transition-all duration-300 hover:scale-110"
                            style={{
                              background: isActive ? `${stepColor}20` : 'transparent',
                              border: `1px solid ${isActive ? stepColor : isDone ? `${stepColor}66` : 'rgba(255,255,255,0.2)'}`,
                              fontFamily: FONTS.mono,
                              clipPath: 'polygon(25% 0%, 100% 0%, 75% 100%, 0% 100%)'
                            }}
                          >
                            <span style={{ 
                              fontSize: '14px',
                              fontWeight: 600,
                              color: isActive || isDone ? stepColor : COLORS.text.muted 
                            }}>
                              {i + 1}
                            </span>
                          </button>
                          {i < steps.length - 1 && (
                            <div className="flex-1 h-px mx-3" style={{ 
                              background: i < currentStep ? 
                                `linear-gradient(to right, ${stepColor}66, ${getStepColor(steps[i+1].color)}66)` : 
                                'rgba(255,255,255,0.1)'
                            }} />
                          )}
                        </div>
                      );
                    })}
                  </div>
                  
                  {/* Step Title */}
                  <h2 className="text-center mb-6" style={{ 
                    fontFamily: FONTS.mono,
                    fontSize: '18px',
                    fontWeight: 600,
                    color: currentColor,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    {step.title}
                  </h2>
                  
                  {/* Step Narrative */}
                  {step.narrative && (
                    <p className="text-center mb-6" style={{ 
                      fontSize: '14px',
                      color: COLORS.text.secondary,
                      lineHeight: '1.6'
                    }}>
                      {step.narrative}
                    </p>
                  )}
                  
                  {/* Content Area */}
                  <div className="flex-1 overflow-auto" key={stepFadeKey} style={{ paddingTop: SPACING.sm }}>
                    {/* Intro Step */}
                    {step.type === "intro" && (
                      <div className="text-center space-y-6">
                        <div>
                          <div className="text-2xl font-bold mb-2" style={{ color: currentColor }}>
                            Welcome to the Future
                          </div>
                          <div className="w-24 h-px mx-auto" style={{ background: currentColor }}></div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 max-w-2xl mx-auto">
                          <div style={{ 
                            background: 'rgba(0,255,159,0.05)',
                            border: '1px solid rgba(0,255,159,0.2)',
                            padding: SPACING.md
                          }}>
                            <div style={{ color: COLORS.mint, fontSize: '18px' }}>✨</div>
                            <div style={{ color: COLORS.mint, fontWeight: 600, marginBottom: '8px' }}>Why UltrAI?</div>
                            <div style={{ fontSize: '12px', color: COLORS.text.secondary }}>
                              Multiple LLMs working together. Better results, fewer blind spots.
                            </div>
                          </div>
                          <div style={{ 
                            background: 'rgba(0,184,255,0.05)',
                            border: '1px solid rgba(0,184,255,0.2)',
                            padding: SPACING.md
                          }}>
                            <div style={{ color: COLORS.blue, fontSize: '18px' }}>🚀</div>
                            <div style={{ color: COLORS.blue, fontWeight: 600, marginBottom: '8px' }}>How it works</div>
                            <div style={{ fontSize: '12px', color: COLORS.text.secondary }}>
                              Select goals, enter query, choose models. We handle the rest.
                            </div>
                          </div>
                        </div>
                        
                        <button 
                          className="px-8 py-4"
                          style={{
                            background: `${currentColor}15`,
                            border: `1px solid ${currentColor}`,
                            color: COLORS.text.primary,
                            fontFamily: FONTS.mono,
                            fontSize: '16px',
                            fontWeight: 600,
                            cursor: 'pointer',
                            transition: 'all 0.3s'
                          }}
                          onClick={() => { setCurrentStep(1); setStepFadeKey(k => k+1); }}
                        >
                          START ULTRAI!
                        </button>
                      </div>
                    )}
                    
                    {/* Other step types */}
                    {step.type !== "intro" && (
                      <div className="text-center" style={{ padding: SPACING.xl, color: COLORS.text.muted }}>
                        [Step Content: {step.type}]
                      </div>
                    )}
                  </div>
                </Panel>
              </div>
              
              {/* Receipt Panel */}
              <div className="col-span-4">
                <Panel style={{ 
                  minHeight: '500px',
                  position: 'sticky',
                  top: '0'
                }}>
                  <h3 className="text-center mb-6" style={{
                    fontFamily: FONTS.mono,
                    fontSize: '16px',
                    fontWeight: 700,
                    color: COLORS.pink,
                    textTransform: 'uppercase',
                    letterSpacing: '0.1em'
                  }}>
                    ITEMIZED SUMMARY
                  </h3>
                  
                  {/* Receipt Items */}
                  <div className="space-y-2 mb-6" style={{ fontFamily: FONTS.mono, fontSize: '12px' }}>
                    {summary.map((item, i) => (
                      <div key={i} className="flex items-center justify-between" style={{ color: getStepColor(item.color) }}>
                        <span>{item.label}</span>
                        <span>${item.cost.toFixed(2)}</span>
                      </div>
                ))}
              </div>
              
              {/* Total - Fixed at bottom */}
              <div className="absolute bottom-0 left-0 right-0 p-4 border-t" style={{ 
                borderColor: 'rgba(255,255,255,0.1)',
                background: 'rgba(0,0,0,0.5)'
              }}>
                <div className="flex items-center justify-between" style={{
                  fontFamily: FONTS.mono,
                  fontSize: '16px',
                  fontWeight: 700,
                  color: COLORS.accent
                }}>
                  <span>TOTAL:</span>
                  <span>${totalCost.toFixed(2)}</span>
                </div>
              </div>
            </Panel>
          </div>
          
          {/* Status/Control Panel - Orange box (x:1207.15, y:1593.56, w:1716.74, h:504.25) */}
          <div 
            className="absolute pointer-events-auto"
            style={{
              left: '31.8%',
              top: '71.7%',
              width: '45.2%',
              height: '22.7%'
            }}
          >
            <Panel style={{ height: '100%' }}>
              {currentStep === steps.length - 1 && !showStatus ? (
                <div className="h-full flex items-center justify-center">
                  <button
                    className="px-12 py-6 transition-all duration-300 hover:scale-105 active:scale-95"
                    style={{ 
                      border: `2px solid ${COLORS.accent}`,
                      background: `${COLORS.accent}15`,
                      color: COLORS.text.primary,
                      fontFamily: FONTS.mono,
                      fontSize: '18px',
                      fontWeight: 600,
                      letterSpacing: '0.05em',
                      clipPath: 'polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 20px 100%, 0 calc(100% - 20px))',
                      boxShadow: `0 0 30px ${COLORS.accent}40`
                    }}
                    onClick={() => setShowStatus(true)}
                  >
                    🚀 COMMENCE ULTRA SYNTHESIS™
                  </button>
                </div>
              ) : showStatus ? (
                <div className="h-full p-6">
                  <StatusUpdater />
                  {/* Status messages */}
                  <div className="mt-4" style={{ fontFamily: FONTS.mono, fontSize: '12px' }}>
                    {isRunning && (
                      <div className="text-blue-400">
                        <span className="animate-spin inline-block mr-2">⚡</span>
                        Running Ultra Synthesis™ Pipeline...
                      </div>
                    )}
                    {orchestratorError && (
                      <div className="text-red-400 mt-2">
                        Error: {orchestratorError}
                      </div>
                    )}
                    {orchestratorResult && (
                      <div className="text-green-400 mt-2">
                        ✅ Synthesis Complete!
                      </div>
                    )}
                  </div>
                </div>
              ) : null}
            </Panel>
          </div>
          
        </div>
      </div>
    </div>
  );
}