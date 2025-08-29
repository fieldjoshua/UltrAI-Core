import { useEffect, useState } from 'react';

interface BridgeAnimationProps {
  state: 'idle' | 'processing' | 'complete';
}

export default function BridgeAnimation({ state }: BridgeAnimationProps) {
  const [cableAnimation, setCableAnimation] = useState(false);
  
  useEffect(() => {
    if (state === 'processing') {
      setCableAnimation(true);
    } else {
      setCableAnimation(false);
    }
  }, [state]);

  return (
    <div 
      className="pointer-events-none fixed inset-0"
      style={{
        zIndex: 2,
      }}
    >
      {/* Static bridge structure */}
      <img
        src="/overlays/bridge_lines.svg"
        alt=""
        className="absolute inset-0 w-full h-full"
        style={{
          objectFit: 'cover',
          objectPosition: 'bottom left',
          opacity: 0.2,
          filter: state === 'processing' ? 'brightness(1.2)' : 'brightness(0.8)',
          transition: 'filter 0.5s ease'
        }}
      />
      
      {/* Animated overlay */}
      <svg
        viewBox="0 0 3850.2 2068.65"
        className="absolute inset-0 w-full h-full"
        preserveAspectRatio="xMinYMax slice"
        style={{
          filter: state === 'processing' ? 'brightness(1.5)' : 'brightness(1)',
          transition: 'filter 0.5s ease'
        }}
      >
        <defs>
          {/* Gradient for cables */}
          <linearGradient id="cableGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#00ffff" stopOpacity="0" />
            <stop offset="50%" stopColor="#00ffff" stopOpacity="1" />
            <stop offset="100%" stopColor="#00ffff" stopOpacity="0" />
          </linearGradient>
          
          {/* Moon glow filter */}
          <filter id="moonGlow">
            <feGaussianBlur stdDeviation="10" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        
        {/* Animated vertical cables */}
        <g opacity={cableAnimation ? 1 : 0.3} style={{ transition: 'opacity 0.5s ease' }}>
          {/* Main bridge cables */}
          {[
            { d: "M469.77,1160.18c.29,5.68,2.14-226.97,1.82-221.33", delay: 0 },
            { d: "M399.74,1185.79c.29,5.68,2.14-226.97,1.82-221.33", delay: 0.2 },
            { d: "M358.82,1175.89c1.46-8.19,1.51-389.81,0-29.9", delay: 0.4 },
            { d: "M302.25,1133.67c.29,5.68-2.52-90.69-2.84-85.05", delay: 0.6 },
            { d: "M235.06,1125.44c.29,5.68-.63-50.45-.95-44.81", delay: 0.8 },
            { d: "M728.82,1189.86c1.46-18.4,1.5-876.02,0-67.2", delay: 1 },
            { d: "M670.43,1183.39c.29,12.77,2.14-510.07,1.82-497.39", delay: 1.2 },
          ].map((cable, i) => (
            <g key={i}>
              {/* Cable base */}
              <path
                d={cable.d}
                fill="none"
                stroke={state === 'processing' ? '#00ffff' : '#00ff00'}
                strokeWidth="2"
                opacity="0.5"
              />
              
              {/* Animated light traveling up cable */}
              {cableAnimation && (
                <path
                  d={cable.d}
                  fill="none"
                  stroke="url(#cableGradient)"
                  strokeWidth="4"
                  opacity="1"
                  style={{
                    strokeDasharray: '50 150',
                    strokeDashoffset: '200',
                    animation: `cableLight 3s ease-in-out infinite ${cable.delay}s`,
                    filter: 'drop-shadow(0 0 10px #00ffff)'
                  }}
                />
              )}
            </g>
          ))}
        </g>
        
        {/* Moon */}
        <circle 
          cx="400" 
          cy="400" 
          r="100"
          fill={state === 'complete' ? '#00ff9f' : '#ffffcc'}
          opacity="0.8"
          filter="url(#moonGlow)"
          style={{
            transform: `scale(${state === 'complete' ? 1.2 : 1})`,
            transformOrigin: '400px 400px',
            transition: 'transform 0.5s ease, fill 0.5s ease'
          }}
        />
        
        {/* Stars around moon when complete */}
        {state === 'complete' && (
          <g opacity="0.8">
            {[...Array(5)].map((_, i) => {
              const angle = (i * 72) * Math.PI / 180;
              const x = 400 + Math.cos(angle) * 150;
              const y = 400 + Math.sin(angle) * 150;
              return (
                <circle
                  key={i}
                  cx={x}
                  cy={y}
                  r="3"
                  fill="#00ff9f"
                  style={{
                    animation: `starTwinkle 1.5s ease-in-out infinite ${i * 0.3}s`
                  }}
                />
              );
            })}
          </g>
        )}
      </svg>
      
      {/* CSS animations */}
      <style jsx>{`
        @keyframes cableLight {
          0% {
            stroke-dashoffset: 200;
          }
          50% {
            stroke-dashoffset: -200;
          }
          100% {
            stroke-dashoffset: -400;
          }
        }
        
        @keyframes starTwinkle {
          0%, 100% {
            opacity: 0.3;
            transform: scale(1);
          }
          50% {
            opacity: 1;
            transform: scale(1.5);
          }
        }
      `}</style>
    </div>
  );
}