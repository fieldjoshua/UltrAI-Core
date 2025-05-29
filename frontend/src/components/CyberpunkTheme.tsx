import React, { useEffect, useState, useRef } from 'react';
import './CyberpunkTheme.css';

interface CyberpunkThemeProps {
  children?: React.ReactNode;
  showBillboard?: boolean;
  billboardTitle?: string;
  billboardSubtitle?: string;
  showCityscape?: boolean;
  showGrid?: boolean;
  showFloatingElements?: boolean;
  cost?: number;
  credit?: number;
}

const CyberpunkTheme: React.FC<CyberpunkThemeProps> = ({
  children,
  showBillboard = true,
  billboardTitle = "ULTRA AI - MULTIPLY YOUR AI!",
  billboardSubtitle = "Intelligence Multiplication System",
  showCityscape = true,
  showGrid = true,
  showFloatingElements = true,
  cost = 12.50,
  credit = 87.50
}) => {
  const [isDay, setIsDay] = useState(false);
  const [currentTime, setCurrentTime] = useState('22:30');
  const [gridVisible, setGridVisible] = useState(false);
  const cityLightsRef = useRef<HTMLDivElement>(null);

  // Generate random city lights
  const generateCityLights = () => {
    if (!cityLightsRef.current) return;
    
    const numLights = 300;
    const fragment = document.createDocumentFragment();
    
    for (let i = 0; i < numLights; i++) {
      const light = document.createElement('div');
      light.classList.add('light');
      
      // Position randomly, but more concentrated in the middle height
      const x = Math.random() * 100; // percentage
      const yFactor = Math.pow(Math.random(), 1.5);
      const y = (1 - yFactor) * 90; // percentage
      
      light.style.left = `${x}%`;
      light.style.bottom = `${y}%`;
      
      // Random sizes for variation
      const size = 1 + Math.random() * 2;
      light.style.width = `${size}px`;
      light.style.height = `${size}px`;
      
      // Random animation delay
      light.style.animationDelay = `${Math.random() * 5}s`;
      
      // Slightly different colors
      const hue = 50 + Math.random() * 10;
      const saturation = 80 + Math.random() * 20;
      const lightness = 70 + Math.random() * 30;
      light.style.backgroundColor = `hsla(${hue}, ${saturation}%, ${lightness}%, ${0.6 + Math.random() * 0.4})`;
      
      fragment.appendChild(light);
    }
    
    cityLightsRef.current.appendChild(fragment);
  };

  // Toggle day/night
  const toggleDayNight = () => {
    setIsDay(!isDay);
    setCurrentTime(isDay ? '22:30' : '10:30');
    setGridVisible(!isDay);
  };

  useEffect(() => {
    if (showCityscape) {
      generateCityLights();
    }
    
    // Show grid after a short delay
    if (showGrid) {
      const timer = setTimeout(() => {
        setGridVisible(true);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [showCityscape, showGrid]);

  return (
    <div className="cyberpunk-theme">
      <div className={`scene ${isDay ? 'day' : ''}`}></div>
      
      {showGrid && (
        <div className={`grid-background ${gridVisible ? 'visible' : ''}`}></div>
      )}

      {showBillboard && (
        <div className="header-billboard">
          <div className="billboard">
            <h1>{billboardTitle}</h1>
            <p>{billboardSubtitle}</p>
          </div>
          <div className="scaffolding">
            <div className="scaffold-beam left"></div>
            <div className="scaffold-beam right"></div>
            <div className="scaffold-beam left-2"></div>
            <div className="scaffold-beam right-2"></div>
            <div className="scaffold-support top"></div>
            <div className="scaffold-support bottom"></div>
            <div className="scaffold-diagonal left"></div>
            <div className="scaffold-diagonal right"></div>
          </div>
        </div>
      )}

      {showCityscape && (
        <div className="cityscape">
          <div className="buildings"></div>
          <div className="city-lights" ref={cityLightsRef}></div>
          
          <div className="main-building">
            <div className="building-top-light"></div>
            <div className="building-windows">
              {Array.from({ length: 35 }).map((_, i) => (
                <div key={i} className="building-window"></div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="cyberpunk-container">
        {children}
      </div>

      {showFloatingElements && (
        <>
          <div className="floating-cost">Cost: ${cost.toFixed(2)}</div>
          <div className="floating-credit">Credit: ${credit.toFixed(2)}</div>
          
          <div className="toggle-container">
            <button className="day-night-toggle" onClick={toggleDayNight}>
              Toggle Day/Night
            </button>
          </div>
          <div className="time-indicator">Time: {currentTime}</div>
        </>
      )}
    </div>
  );
};

export default CyberpunkTheme;