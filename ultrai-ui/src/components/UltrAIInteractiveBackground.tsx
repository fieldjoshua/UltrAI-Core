import React, { useState, useEffect, useRef } from 'react';

interface UltrAIInteractiveBackgroundProps {
  children?: React.ReactNode;
  backgroundUrl?: string;
}

export default function UltrAIInteractiveBackground({ 
  children, 
  backgroundUrl 
}: UltrAIInteractiveBackgroundProps) {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const cityLightsRef = useRef<HTMLDivElement>(null);

  // Track mouse movement for parallax effect
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const x = (e.clientX / window.innerWidth - 0.5) * 2;
      const y = (e.clientY / window.innerHeight - 0.5) * 2;
      setMousePos({ x, y });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Generate random city lights
  useEffect(() => {
    if (!cityLightsRef.current) return;
    
    const numLights = 200;
    const fragment = document.createDocumentFragment();
    
    for (let i = 0; i < numLights; i++) {
      const light = document.createElement('div');
      light.className = 'absolute rounded-full animate-pulse';
      
      // Position randomly
      const x = Math.random() * 100;
      const y = Math.random() * 80 + 10; // Keep lights in buildings area
      
      light.style.left = `${x}%`;
      light.style.top = `${y}%`;
      
      // Random sizes
      const size = 1 + Math.random() * 3;
      light.style.width = `${size}px`;
      light.style.height = `${size}px`;
      
      // Random colors (cyberpunk palette)
      const colors = ['#00ffff', '#ff00de', '#ffff00', '#00ff41', '#ff6b00'];
      light.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
      light.style.boxShadow = `0 0 ${size * 4}px currentColor`;
      
      // Random animation delay
      light.style.animationDelay = `${Math.random() * 3}s`;
      
      fragment.appendChild(light);
    }
    
    cityLightsRef.current.appendChild(fragment);
  }, []);

  return (
    <div className="relative min-h-screen bg-gray-900 overflow-hidden">
      {/* Background image if provided */}
      {backgroundUrl && (
        <div 
          className="absolute inset-0 bg-cover bg-center opacity-30"
          style={{ 
            backgroundImage: `url(${backgroundUrl})`,
            transform: `translate3d(${mousePos.x * 5}px, ${mousePos.y * 3}px, 0)`
          }}
        />
      )}
      
      {/* Cyberpunk grid overlay */}
      <div 
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `
            linear-gradient(rgba(0, 255, 255, 0.3) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 255, 0.3) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
          transform: `translate3d(${mousePos.x * -2}px, ${mousePos.y * -1}px, 0)`
        }}
      />
      
      {/* Neon city skyline silhouette */}
      <div 
        className="absolute bottom-0 left-0 right-0 h-1/3 bg-gradient-to-t from-black via-gray-900 to-transparent"
        style={{
          transform: `translate3d(${mousePos.x * 3}px, 0, 0)`
        }}
      >
        {/* Building shapes */}
        <div className="absolute bottom-0 w-full h-full">
          {/* Random building rectangles */}
          {Array.from({ length: 15 }).map((_, i) => (
            <div
              key={i}
              className="absolute bottom-0 bg-black border-t-2 border-cyan-400"
              style={{
                left: `${i * 7}%`,
                width: `${4 + Math.random() * 8}%`,
                height: `${40 + Math.random() * 60}%`,
                boxShadow: '0 0 20px rgba(0, 255, 255, 0.3)',
                transform: `translate3d(${mousePos.x * (1 + i * 0.1)}px, 0, 0)`
              }}
            />
          ))}
        </div>
        
        {/* City lights */}
        <div ref={cityLightsRef} className="absolute inset-0" />
      </div>
      
      {/* Glowing orbs */}
      <div className="absolute inset-0 pointer-events-none">
        {Array.from({ length: 8 }).map((_, i) => (
          <div
            key={i}
            className="absolute w-4 h-4 rounded-full animate-pulse"
            style={{
              left: `${10 + i * 12}%`,
              top: `${20 + Math.sin(i) * 30}%`,
              background: `radial-gradient(circle, ${
                ['#ff00de', '#00ffff', '#ffff00', '#00ff41'][i % 4]
              }, transparent)`,
              transform: `translate3d(${mousePos.x * (10 + i * 2)}px, ${mousePos.y * (5 + i)}px, 0)`,
              animationDelay: `${i * 0.5}s`,
              animationDuration: `${2 + Math.random() * 2}s`
            }}
          />
        ))}
      </div>
      
      {/* Horizontal light beam */}
      <div 
        className="absolute left-0 right-0 h-px top-1/3 bg-gradient-to-r from-transparent via-cyan-400 to-transparent opacity-60"
        style={{
          boxShadow: '0 0 20px #00ffff',
          transform: `translate3d(0, ${mousePos.y * 10}px, 0)`
        }}
      />
      
      {/* Diagonal light rays */}
      {Array.from({ length: 4 }).map((_, i) => (
        <div
          key={i}
          className="absolute w-px h-32 bg-gradient-to-b from-transparent via-pink-400 to-transparent opacity-40"
          style={{
            left: `${20 + i * 20}%`,
            top: `${10 + i * 15}%`,
            transform: `rotate(${15 + i * 5}deg) translate3d(${mousePos.x * (3 + i)}px, ${mousePos.y * (2 + i)}px, 0)`,
            boxShadow: '0 0 10px #ff00de'
          }}
        />
      ))}
      
      {/* Content overlay */}
      <div className="relative z-10 min-h-screen">
        {children}
      </div>
      
      {/* Vignette effect */}
      <div className="absolute inset-0 bg-gradient-radial from-transparent via-transparent to-black/50 pointer-events-none" />
    </div>
  );
}