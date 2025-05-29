import React from 'react';
import CyberpunkTheme from './CyberpunkTheme';

const CyberpunkDemo: React.FC = () => {
  return (
    <CyberpunkTheme
      billboardTitle="ULTRA AI - MULTIPLY YOUR AI!"
      billboardSubtitle="Intelligence Multiplication System"
      cost={12.50}
      credit={87.50}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '2rem', marginTop: '2rem' }}>
        <div className="cyber-ui-element cyber-ui-prompt" style={{ flex: 1 }}>
          <h3 style={{ color: '#ff00de', margin: '0 0 1rem 0' }}>Enter Your Prompt</h3>
          <p>Start simple with your query. The city evolves as you build your experience, with each step adding depth to your journey.</p>
        </div>
        
        <div className="cyber-ui-element cyber-ui-model" style={{ flex: 1 }}>
          <h3 style={{ color: '#00ffff', margin: '0 0 1rem 0' }}>Select Your Models</h3>
          <p>Choose which AI models to include in your analysis for maximum intelligence multiplication and diverse perspectives.</p>
        </div>
        
        <div className="cyber-ui-element cyber-ui-analysis" style={{ flex: 1 }}>
          <h3 style={{ color: '#00ff9f', margin: '0 0 1rem 0' }}>Choose Analysis Pattern</h3>
          <p>Select a specialized "feather" pattern to optimize how the models collaborate and enhance each other's capabilities.</p>
        </div>
      </div>
      
      <div style={{ textAlign: 'center', marginTop: '3rem' }}>
        <button className="cyber-button" onClick={() => alert('Analysis started! The city continues to evolve...')}>
          ANALYZE
        </button>
      </div>
    </CyberpunkTheme>
  );
};

export default CyberpunkDemo;