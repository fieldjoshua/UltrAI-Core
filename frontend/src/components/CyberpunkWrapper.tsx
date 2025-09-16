import React, { useState, useEffect } from 'react';
import CyberpunkCityBackground from './CyberpunkCityBackground';
import './CyberpunkWrapper.css';

interface CyberpunkWrapperProps {
  children: React.ReactNode;
  enableBackground?: boolean;
  intensity?: 'minimal' | 'medium' | 'full';
  performanceMode?: 'high' | 'balanced' | 'battery';
}

/**
 * Wrapper component that provides cyberpunk background with user controls
 * Integrates with the existing Universal Container system
 */
export const CyberpunkWrapper: React.FC<CyberpunkWrapperProps> = ({
  children,
  enableBackground = true,
  intensity = 'medium',
  performanceMode = 'balanced',
}) => {
  const [backgroundEnabled, setBackgroundEnabled] = useState(() => {
    // Check localStorage for user preference
    const saved = localStorage.getItem('cyberpunk-background-enabled');
    return saved !== null ? JSON.parse(saved) : enableBackground;
  });

  const [userIntensity, setUserIntensity] = useState(() => {
    const saved = localStorage.getItem('cyberpunk-background-intensity');
    return saved || intensity;
  });

  const [userPerformanceMode, setUserPerformanceMode] = useState(() => {
    const saved = localStorage.getItem('cyberpunk-background-performance');
    return saved || performanceMode;
  });

  // Save preferences to localStorage
  useEffect(() => {
    localStorage.setItem(
      'cyberpunk-background-enabled',
      JSON.stringify(backgroundEnabled)
    );
  }, [backgroundEnabled]);

  useEffect(() => {
    localStorage.setItem('cyberpunk-background-intensity', userIntensity);
  }, [userIntensity]);

  useEffect(() => {
    localStorage.setItem(
      'cyberpunk-background-performance',
      userPerformanceMode
    );
  }, [userPerformanceMode]);

  // Auto-detect performance mode based on device capabilities
  useEffect(() => {
    const detectPerformanceMode = () => {
      const hardwareConcurrency = navigator.hardwareConcurrency || 2;
      const memory = (navigator as any).deviceMemory || 4;

      if (hardwareConcurrency <= 2 || memory <= 2) {
        setUserPerformanceMode('battery');
      } else if (hardwareConcurrency >= 8 && memory >= 8) {
        setUserPerformanceMode('high');
      } else {
        setUserPerformanceMode('balanced');
      }
    };

    // Only auto-detect if user hasn't manually set preference
    if (!localStorage.getItem('cyberpunk-background-performance')) {
      detectPerformanceMode();
    }
  }, []);

  return (
    <div className="cyberpunk-wrapper">
      {backgroundEnabled && (
        <CyberpunkCityBackground
          intensity={userIntensity as 'minimal' | 'medium' | 'full'}
          interactive={true}
          performanceMode={
            userPerformanceMode as 'high' | 'balanced' | 'battery'
          }
        />
      )}

      {/* Background Controls */}
      <div className="cyberpunk-controls">
        <button
          onClick={() => setBackgroundEnabled(!backgroundEnabled)}
          className="background-toggle"
          title={`${backgroundEnabled ? 'Disable' : 'Enable'} cyberpunk background`}
          aria-label={`${backgroundEnabled ? 'Disable' : 'Enable'} cyberpunk background`}
        >
          {backgroundEnabled ? '🏙️' : '🌑'}
        </button>

        {backgroundEnabled && (
          <>
            <select
              value={userIntensity}
              onChange={e => setUserIntensity(e.target.value)}
              className="intensity-selector"
              title="Animation intensity"
              aria-label="Animation intensity"
            >
              <option value="minimal">Minimal</option>
              <option value="medium">Medium</option>
              <option value="full">Full</option>
            </select>

            <select
              value={userPerformanceMode}
              onChange={e => setUserPerformanceMode(e.target.value)}
              className="performance-selector"
              title="Performance mode"
              aria-label="Performance mode"
            >
              <option value="battery">Battery</option>
              <option value="balanced">Balanced</option>
              <option value="high">High</option>
            </select>
          </>
        )}
      </div>

      {/* Content with overlay */}
      <div
        className={`content-wrapper ${backgroundEnabled ? 'with-background' : 'without-background'}`}
      >
        {children}
      </div>
    </div>
  );
};

export default CyberpunkWrapper;
