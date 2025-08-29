import { useEffect, useState } from 'react';

interface AnimatedBillboardProps {
  state: 'idle' | 'processing' | 'complete';
  message: string;
  currentStep: number;
  totalSteps: number;
}

export default function AnimatedBillboard({ 
  state, 
  message, 
  currentStep, 
  totalSteps 
}: AnimatedBillboardProps) {
  const [glitchActive, setGlitchActive] = useState(false);
  const [neonFlash, setNeonFlash] = useState(false);

  useEffect(() => {
    if (state === 'processing') {
      const glitchInterval = setInterval(() => {
        setGlitchActive(true);
        setTimeout(() => setGlitchActive(false), 150);
      }, 3000);
      return () => clearInterval(glitchInterval);
    }
  }, [state]);

  useEffect(() => {
    if (state === 'complete') {
      setNeonFlash(true);
      setTimeout(() => setNeonFlash(false), 1000);
    }
  }, [state]);

  return (
    <div className="fixed top-0 left-0 w-full z-50">
      {/* Main billboard container */}
      <div 
        className="relative h-[120px] overflow-hidden"
        style={{
          background: 'linear-gradient(to bottom, rgba(0,0,0,0.95), rgba(0,0,0,0.85))',
          borderBottom: `2px solid ${state === 'processing' ? '#00ffff' : state === 'complete' ? '#00ff9f' : '#ff00de'}`,
          boxShadow: `0 0 ${state === 'processing' ? '40px' : '20px'} ${
            state === 'processing' ? '#00ffff' : 
            state === 'complete' ? '#00ff9f' : '#ff00de'
          }, inset 0 -20px 40px -20px rgba(0,0,0,0.8)`,
          transition: 'all 0.5s ease'
        }}
      >
        {/* Background grid pattern - subtle */}
        <div 
          className="absolute inset-0"
          style={{
            backgroundImage: `
              linear-gradient(to right, rgba(255,0,222,0.05) 1px, transparent 1px),
              linear-gradient(to bottom, rgba(255,0,222,0.05) 1px, transparent 1px)
            `,
            backgroundSize: '40px 40px',
            animation: state === 'processing' ? 'backgroundShift 20s linear infinite' : 'none'
          }}
        />
        
        {/* Additional lighting effect */}
        <div 
          className="absolute inset-0"
          style={{
            background: state === 'processing' ? 
              'radial-gradient(ellipse at bottom right, rgba(0,255,255,0.15) 0%, transparent 70%)' : 
              'radial-gradient(ellipse at bottom right, rgba(255,0,222,0.1) 0%, transparent 70%)',
            transition: 'all 1s ease'
          }}
        />

        {/* Building and Billboard Lines - positioned in lower right */}
        <img
          src="/overlays/billboard_lines.svg"
          alt=""
          className="absolute"
          style={{
            bottom: 0,
            right: 0,
            width: '70%',
            height: 'auto',
            maxHeight: '100%',
            opacity: state === 'processing' ? 0.3 : 0.2,
            filter: state === 'processing' ? 'brightness(1.8) hue-rotate(180deg)' : 'brightness(1.2)',
            mixBlendMode: 'screen',
            transition: 'all 0.5s ease'
          }}
        />

        {/* Main content */}
        <div className="relative h-full flex flex-col items-center justify-center">
          {/* ULTRA AI Logo */}
          <h1 
            className={`text-5xl font-black tracking-wider ${glitchActive ? 'animate-glitch' : ''} ${neonFlash ? 'animate-neonFlash' : ''}`}
            style={{
              background: 'linear-gradient(to right, #ff00de, #00ffff, #00ff9f)',
              WebkitBackgroundClip: 'text',
              backgroundClip: 'text',
              color: 'transparent',
              textShadow: state === 'processing' ? 
                '0 0 30px rgba(0, 255, 255, 0.8)' : 
                '0 0 20px rgba(255, 0, 222, 0.8)',
              transform: glitchActive ? 'translate(-2px, 2px)' : 'none',
              transition: 'transform 0.1s ease'
            }}
          >
            ULTRA AI
          </h1>

          {/* Status message */}
          {message && (
            <p 
              className="text-sm mt-1 font-mono"
              style={{
                color: state === 'processing' ? '#00ffff' : 
                       state === 'complete' ? '#00ff9f' : '#fff',
                textShadow: `0 0 10px currentColor`,
                animation: state === 'processing' ? 'pulse 1.5s infinite' : 'none'
              }}
            >
              {message}
            </p>
          )}

          {/* Progress indicator */}
          {state === 'processing' && currentStep > 0 && (
            <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2">
              <div className="flex items-center space-x-2">
                {Array.from({ length: totalSteps }, (_, i) => (
                  <div
                    key={i}
                    className="w-2 h-2 rounded-full transition-all duration-300"
                    style={{
                      backgroundColor: i < currentStep ? '#00ffff' : '#333',
                      boxShadow: i < currentStep ? '0 0 10px #00ffff' : 'none'
                    }}
                  />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Scanning line effect */}
        {state === 'processing' && (
          <div 
            className="absolute left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-cyan-400 to-transparent"
            style={{
              top: '50%',
              animation: 'scan 2s linear infinite',
              boxShadow: '0 0 10px #00ffff'
            }}
          />
        )}

        {/* Corner decorations with animated glow */}
        <div className="absolute top-2 left-2 w-8 h-8 border-l-2 border-t-2" 
          style={{ 
            borderColor: state === 'processing' ? '#00ffff' : '#ff00de',
            boxShadow: state === 'processing' ? '0 0 10px #00ffff' : '0 0 5px #ff00de',
            transition: 'all 0.5s ease'
          }} 
        />
        <div className="absolute top-2 right-2 w-8 h-8 border-r-2 border-t-2" 
          style={{ 
            borderColor: state === 'processing' ? '#00ffff' : '#ff00de',
            boxShadow: state === 'processing' ? '0 0 10px #00ffff' : '0 0 5px #ff00de',
            transition: 'all 0.5s ease'
          }} 
        />
        <div className="absolute bottom-2 left-2 w-8 h-8 border-l-2 border-b-2" 
          style={{ 
            borderColor: state === 'processing' ? '#00ffff' : '#ff00de',
            boxShadow: state === 'processing' ? '0 0 10px #00ffff' : '0 0 5px #ff00de',
            transition: 'all 0.5s ease'
          }} 
        />
        <div className="absolute bottom-2 right-2 w-8 h-8 border-r-2 border-b-2" 
          style={{ 
            borderColor: state === 'processing' ? '#00ffff' : '#ff00de',
            boxShadow: state === 'processing' ? '0 0 10px #00ffff' : '0 0 5px #ff00de',
            transition: 'all 0.5s ease'
          }} 
        />
      </div>

      {/* Add custom animations */}
      <style jsx>{`
        @keyframes backgroundShift {
          0% { background-position: 0 0; }
          100% { background-position: 40px 40px; }
        }
        
        @keyframes scan {
          0% { transform: translateY(-60px); opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { transform: translateY(60px); opacity: 0; }
        }
        
        @keyframes glitch {
          0% { transform: translate(0); }
          20% { transform: translate(-2px, 2px); }
          40% { transform: translate(-2px, -2px); }
          60% { transform: translate(2px, 2px); }
          80% { transform: translate(2px, -2px); }
          100% { transform: translate(0); }
        }
        
        @keyframes neonFlash {
          0%, 100% { filter: brightness(1); }
          50% { filter: brightness(1.5); }
        }
        
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }
      `}</style>
    </div>
  );
}