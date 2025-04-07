import React, { useEffect, useState } from 'react';
import './AnimatedLogoV3.css';

interface AnimatedLogoProps {
  isProcessing?: boolean;
  size?: 'small' | 'medium' | 'large';
  theme?: 'light' | 'dark';
  color?: 'orange' | 'blue' | 'purple' | 'rainbow';
}

const AnimatedLogoV3: React.FC<AnimatedLogoProps> = ({ 
  isProcessing = false, 
  size = 'medium',
  theme = 'dark',
  color = 'orange'
}) => {
  const [intensity, setIntensity] = useState(0);
  const [angle, setAngle] = useState(0);

  // Create pulsing effect when processing
  useEffect(() => {
    if (!isProcessing) {
      setIntensity(0);
      return;
    }

    let interval: ReturnType<typeof setInterval>;
    let direction = 1;
    let currentIntensity = 0;

    interval = setInterval(() => {
      currentIntensity += 0.05 * direction;
      
      if (currentIntensity >= 1) {
        currentIntensity = 1;
        direction = -1;
      } else if (currentIntensity <= 0.2) {
        currentIntensity = 0.2;
        direction = 1;
      }
      
      setIntensity(currentIntensity);
    }, 50);

    return () => clearInterval(interval);
  }, [isProcessing]);

  // Create subtle rotation effect for wireframe
  useEffect(() => {
    if (!isProcessing) {
      return;
    }

    const interval = setInterval(() => {
      setAngle(prev => (prev + 0.1) % 360);
    }, 50);

    return () => clearInterval(interval);
  }, [isProcessing]);

  const logoClasses = [
    'ultra-logo-v3',
    `ultra-logo-v3--${size}`,
    `ultra-logo-v3--${theme}`,
    `ultra-logo-v3--${color}`,
    isProcessing ? 'ultra-logo-v3--processing' : ''
  ].filter(Boolean).join(' ');

  return (
    <div 
      className={logoClasses}
      style={{ 
        '--intensity': intensity,
        '--angle': `${angle}deg`,
      } as React.CSSProperties}
    >
      {/* Wireframe background */}
      <div className="ultra-logo-v3__wireframe-container">
        <div className="ultra-logo-v3__wireframe ultra-logo-v3__wireframe--outer">
          {/* Generate outer wireframe lines */}
          {Array.from({ length: 16 }).map((_, i) => (
            <div 
              key={`outer-${i}`}
              className="ultra-logo-v3__wireframe-line" 
              style={{ transform: `rotate(${i * 22.5}deg)` }}
            />
          ))}
        </div>
        <div className="ultra-logo-v3__wireframe ultra-logo-v3__wireframe--inner">
          {/* Generate inner wireframe lines */}
          {Array.from({ length: 12 }).map((_, i) => (
            <div 
              key={`inner-${i}`}
              className="ultra-logo-v3__wireframe-line" 
              style={{ transform: `rotate(${i * 30}deg)` }}
            />
          ))}
        </div>
        <div className="ultra-logo-v3__corner-glow ultra-logo-v3__corner-glow--tl"></div>
        <div className="ultra-logo-v3__corner-glow ultra-logo-v3__corner-glow--tr"></div>
        <div className="ultra-logo-v3__corner-glow ultra-logo-v3__corner-glow--bl"></div>
        <div className="ultra-logo-v3__corner-glow ultra-logo-v3__corner-glow--br"></div>
      </div>

      {/* Main logo container */}
      <div className="ultra-logo-v3__container">
        {/* Black circular background */}
        <div className="ultra-logo-v3__circle">
          {/* LU Symbol */}
          <div className="ultra-logo-v3__symbol">
            {/* Left part (L shape) */}
            <svg viewBox="0 0 100 100" className="ultra-logo-v3__l-shape">
              <polygon points="20,20 40,20 40,60 80,60 80,80 20,80" />
            </svg>
            
            {/* Right part (Angled shape) */}
            <svg viewBox="0 0 100 100" className="ultra-logo-v3__angled-shape">
              <polygon points="50,20 80,50 50,80 35,65 50,50 35,35" fill="#aaa" stroke="#888" strokeWidth="1"/>
            </svg>
          </div>
        </div>
      </div>
      
      {/* Processing glow effect */}
      {isProcessing && (
        <div className="ultra-logo-v3__glow" style={{ opacity: intensity * 0.6 }} />
      )}
    </div>
  );
};

export default AnimatedLogoV3; 