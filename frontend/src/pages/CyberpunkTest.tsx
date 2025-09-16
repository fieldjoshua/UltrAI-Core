import React from 'react';
import CyberpunkCityBackground from '../components/CyberpunkCityBackground';

/**
 * Minimal test page for debugging cyberpunk background
 */
const CyberpunkTest: React.FC = () => {
  return (
    <div className="min-h-screen">
      <CyberpunkCityBackground
        intensity="medium"
        interactive={false}
        performanceMode="balanced"
      >
        <div className="relative z-10 p-8">
          <h1 className="text-4xl font-bold text-white">Cyberpunk Test Page</h1>
          <p className="text-gray-300 mt-4">
            Testing the baseline city background
          </p>
        </div>
      </CyberpunkCityBackground>
    </div>
  );
};

export default CyberpunkTest;
