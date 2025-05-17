import React, { useEffect, useState, useRef } from 'react';
import './AnimatedLogoV2.css';

interface AnimatedLogoProps {
  isProcessing?: boolean;
  size?: 'small' | 'medium' | 'large';
  theme?: 'light' | 'dark';
  color?: 'blue' | 'purple' | 'green' | 'rainbow';
}

const AnimatedLogoV2: React.FC<AnimatedLogoProps> = ({
  isProcessing = false,
  size = 'medium',
  theme = 'dark',
  color = 'blue'
}) => {
  const [intensity, setIntensity] = useState(0);
  const [angle, setAngle] = useState(0);
  const svgRef = useRef<SVGSVGElement>(null);

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
      setAngle(prev => (prev + 0.2) % 360);
    }, 50);

    return () => clearInterval(interval);
  }, [isProcessing]);

  const logoClasses = [
    'ultra-logo-v2',
    `ultra-logo-v2--${size}`,
    `ultra-logo-v2--${theme}`,
    `ultra-logo-v2--${color}`,
    isProcessing ? 'ultra-logo-v2--processing' : ''
  ].filter(Boolean).join(' ');

  return (
    <div
      className={logoClasses}
      style={{
        '--intensity': intensity,
        '--angle': `${angle}deg`,
      } as React.CSSProperties}
    >
      {/* Background wireframe that animates */}
      <div className="ultra-logo-v2__wireframe">
        {Array.from({ length: 10 }).map((_, i) => (
          <div
            key={`wireframe-${i}`}
            className="ultra-logo-v2__wireframe-line"
            style={{ transform: `rotate(${i * 36}deg)` }}
          />
        ))}
      </div>

      {/* Actual logo SVG */}
      <svg
        ref={svgRef}
        className="ultra-logo-v2__svg"
        viewBox="0 0 800 800"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Rounded square background */}
        <rect
          x="50"
          y="50"
          width="700"
          height="700"
          rx="150"
          className="ultra-logo-v2__background"
        />

        {/* Center circle */}
        <circle
          cx="400"
          cy="400"
          r="250"
          className="ultra-logo-v2__circle"
        />

        {/* Ultra "U" shape */}
        <path
          d="M300 250 L300 450 L500 450 L500 550 L200 550 L200 250 Z"
          className="ultra-logo-v2__u-shape"
        />

        {/* Arrow element */}
        <path
          d="M400 250 L550 400 L400 550"
          className="ultra-logo-v2__arrow"
          strokeWidth="100"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
        />
      </svg>

      {/* Glow effect when processing */}
      {isProcessing && (
        <div className="ultra-logo-v2__glow" style={{ opacity: intensity * 0.8 }} />
      )}
    </div>
  );
};

export default AnimatedLogoV2;
