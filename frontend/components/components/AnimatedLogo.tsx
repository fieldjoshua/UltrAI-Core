import React, { useEffect, useState } from 'react';
import './AnimatedLogo.css';

interface AnimatedLogoProps {
  isProcessing?: boolean;
  size?: 'small' | 'medium' | 'large';
  theme?: 'light' | 'dark';
  color?: 'blue' | 'purple' | 'green' | 'rainbow';
}

const AnimatedLogo: React.FC<AnimatedLogoProps> = ({
  isProcessing = false,
  size = 'medium',
  theme = 'dark',
  color = 'blue',
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
      setAngle((prev) => (prev + 0.2) % 360);
    }, 50);

    return () => clearInterval(interval);
  }, [isProcessing]);

  const logoClasses = [
    'ultra-logo',
    `ultra-logo--${size}`,
    `ultra-logo--${theme}`,
    `ultra-logo--${color}`,
    isProcessing ? 'ultra-logo--processing' : '',
  ]
    .filter(Boolean)
    .join(' ');

  // Dynamic styles based on processing state
  const wireframeOpacity = 0.05 + intensity * 0.4;
  const wireframeRotation = isProcessing
    ? `rotate(${angle}deg)`
    : 'rotate(0deg)';
  const innerWireframeRotation = isProcessing
    ? `rotate(${-angle * 0.5}deg)`
    : 'rotate(0deg)';

  return (
    <div
      className={logoClasses}
      style={
        {
          '--intensity': intensity,
          '--wireframe-opacity': wireframeOpacity,
        } as React.CSSProperties
      }
    >
      {/* Outer wireframe container */}
      <div
        className="ultra-logo__wireframe"
        style={{ transform: wireframeRotation }}
      >
        {/* Generate outer wireframe lines */}
        {Array.from({ length: 12 }).map((_, i) => (
          <div
            key={`outer-${i}`}
            className="ultra-logo__wireframe-line"
            style={{
              transform: `rotate(${i * 30}deg)`,
              opacity: wireframeOpacity,
            }}
          />
        ))}
      </div>

      {/* Inner wireframe with counter-rotation */}
      <div
        className="ultra-logo__wireframe ultra-logo__wireframe--inner"
        style={{ transform: innerWireframeRotation }}
      >
        {/* Generate inner wireframe lines */}
        {Array.from({ length: 8 }).map((_, i) => (
          <div
            key={`inner-${i}`}
            className="ultra-logo__wireframe-line ultra-logo__wireframe-line--inner"
            style={{
              transform: `rotate(${i * 45}deg)`,
              opacity: wireframeOpacity * 1.5,
            }}
          />
        ))}
      </div>

      {/* Diamond container */}
      <div className="ultra-logo__diamond">
        {/* Pulsing highlight effect */}
        {isProcessing && (
          <div
            className="ultra-logo__highlight"
            style={{ opacity: intensity * 0.7 }}
          />
        )}

        {/* Main logo circle */}
        <div className="ultra-logo__circle">
          {/* The "U" shape */}
          <div className="ultra-logo__u-shape" />
        </div>
      </div>
    </div>
  );
};

export default AnimatedLogo;
