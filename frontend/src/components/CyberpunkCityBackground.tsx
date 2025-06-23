import React, { useState, useEffect, useMemo, CSSProperties } from 'react';
import './CyberpunkCityBackground.css';

// SVG Assets as React Components
import BridgeStructure from '../assets/cyberpunk/bridge-structure.svg?react';
import PurpleBuilding from '../assets/cyberpunk/purple-building.svg?react';
import CircuitBuilding from '../assets/cyberpunk/circuit-building.svg?react';

interface MousePosition {
  x: number;
  y: number;
}

interface CyberpunkBackgroundProps {
  intensity?: 'minimal' | 'medium' | 'full';
  interactive?: boolean;
  performanceMode?: 'high' | 'balanced' | 'battery';
  children?: React.ReactNode;
}

interface CyberpunkLayerConfig {
  asset: React.ComponentType<any>;
  position: { x: string; y: string };
  scale: number;
  animations: string[];
  interactivity: boolean;
  parallaxSpeed: number;
}

const layerConfigs: Record<string, CyberpunkLayerConfig> = {
  background: {
    asset: PurpleBuilding,
    position: { x: '60%', y: '20%' },
    scale: 0.6,
    animations: ['building-pulse', 'window-flicker'],
    interactivity: true,
    parallaxSpeed: 0.1
  },
  midground: {
    asset: CircuitBuilding,
    position: { x: '20%', y: '30%' },
    scale: 0.5,
    animations: ['circuit-flow', 'data-stream'],
    interactivity: true,
    parallaxSpeed: 0.3
  },
  foreground: {
    asset: BridgeStructure,
    position: { x: '-10%', y: '40%' },
    scale: 0.4,
    animations: ['connection-pulse', 'structure-glow'],
    interactivity: false,
    parallaxSpeed: 0.5
  }
};

// Hook for parallax layers
const useParallaxLayers = () => {
  const [scrollY, setScrollY] = useState(0);
  const [mousePos, setMousePos] = useState<MousePosition>({ x: 0, y: 0 });

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({
        x: (e.clientX / window.innerWidth) - 0.5,
        y: (e.clientY / window.innerHeight) - 0.5
      });
    };

    window.addEventListener('scroll', handleScroll);
    window.addEventListener('mousemove', handleMouseMove);
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  return { scrollY, mousePos };
};

// Hook for reduced motion accessibility
const useReducedMotion = (): boolean => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = () => setPrefersReducedMotion(mediaQuery.matches);
    mediaQuery.addEventListener('change', handleChange);
    
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return prefersReducedMotion;
};

// Interactive glow effects component
const InteractiveGlowEffects: React.FC<{ mousePos: MousePosition }> = ({ mousePos }) => {
  const glowIntensity = useMemo(() => {
    return Math.sqrt(mousePos.x * mousePos.x + mousePos.y * mousePos.y) * 2;
  }, [mousePos]);

  return (
    <div
      className="interactive-glow"
      style={{
        '--mouse-x': `${mousePos.x * 100}px`,
        '--mouse-y': `${mousePos.y * 100}px`,
        '--glow-intensity': glowIntensity
      } as CSSProperties}
    >
      <div className="radial-glow" />
      <div className="spotlight-effect" />
    </div>
  );
};

// Data stream particles component
const DataStreamParticles: React.FC<{ intensity: string }> = ({ intensity }) => {
  const particleCount = useMemo(() => ({
    minimal: 20,
    medium: 50,
    full: 100
  }[intensity] || 50), [intensity]);

  return (
    <div className="data-stream-container">
      {Array.from({ length: particleCount }).map((_, i) => (
        <div
          key={i}
          className="data-particle"
          style={{
            '--delay': `${i * 0.3}s`,
            '--duration': `${3 + Math.random() * 2}s`,
            '--start-x': `${Math.random() * 100}%`,
            '--start-y': `${Math.random() * 100}%`
          } as CSSProperties}
        />
      ))}
    </div>
  );
};

// Static background for reduced motion
const StaticCyberpunkBackground: React.FC = () => (
  <div className="cyberpunk-city-background static">
    <div className="cyberpunk-layer background static">
      <PurpleBuilding className="cyberpunk-background static" />
    </div>
    <div className="cyberpunk-layer midground static">
      <CircuitBuilding className="cyberpunk-midground static" />
    </div>
    <div className="cyberpunk-layer foreground static">
      <BridgeStructure className="cyberpunk-foreground static" />
    </div>
  </div>
);

// Main component
export const CyberpunkCityBackground: React.FC<CyberpunkBackgroundProps> = ({
  intensity = 'medium',
  interactive = true,
  performanceMode = 'balanced',
  children
}) => {
  const { scrollY, mousePos } = useParallaxLayers();
  const reducedMotion = useReducedMotion();
  const [isVisible, setIsVisible] = useState(true);

  // Calculate transforms for each layer
  const layerTransforms = useMemo(() => ({
    background: {
      transform: `translate3d(${mousePos.x * 10}px, ${mousePos.y * 8 + scrollY * layerConfigs.background.parallaxSpeed}px, 0) scale(${layerConfigs.background.scale})`
    },
    midground: {
      transform: `translate3d(${mousePos.x * 20}px, ${mousePos.y * 15 + scrollY * layerConfigs.midground.parallaxSpeed}px, 0) scale(${layerConfigs.midground.scale})`
    },
    foreground: {
      transform: `translate3d(${mousePos.x * 30}px, ${mousePos.y * 25 + scrollY * layerConfigs.foreground.parallaxSpeed}px, 0) scale(${layerConfigs.foreground.scale})`
    }
  }), [mousePos, scrollY]);

  // Use static background for reduced motion preference
  if (reducedMotion) {
    return (
      <>
        <StaticCyberpunkBackground />
        {children && <div className="content-overlay">{children}</div>}
      </>
    );
  }

  return (
    <>
      <div className={`cyberpunk-city-background ${intensity} ${performanceMode}`}>
        {Object.entries(layerConfigs).map(([layerName, config]) => (
          <div
            key={layerName}
            className={`cyberpunk-layer ${layerName}`}
            style={layerTransforms[layerName as keyof typeof layerTransforms]}
          >
            <config.asset className={`cyberpunk-${layerName}`} />
          </div>
        ))}

        {interactive && (
          <>
            <InteractiveGlowEffects mousePos={mousePos} />
            <DataStreamParticles intensity={intensity} />
          </>
        )}
      </div>
      
      {children && <div className="content-overlay">{children}</div>}
    </>
  );
};

export default CyberpunkCityBackground;