import React from 'react';
import CyberpunkTheme from './CyberpunkTheme';

const CyberpunkDebug: React.FC = () => {
  return (
    <div>
      {/* Debug info */}
      <div
        style={{
          position: 'fixed',
          top: 10,
          right: 10,
          background: 'black',
          color: 'cyan',
          padding: '10px',
          border: '2px solid cyan',
          zIndex: 9999,
          fontFamily: 'monospace',
        }}
      >
        <h3>Cyberpunk Debug</h3>
        <p>CSS Import: ✓</p>
        <p>Component Loaded: ✓</p>
        <p>Time: {new Date().toLocaleTimeString()}</p>
      </div>

      {/* Force all features on */}
      <CyberpunkTheme
        showBillboard={true}
        billboardTitle="ULTRA AI - MULTIPLY YOUR AI!"
        billboardSubtitle="Intelligence Multiplication System"
        showCityscape={true}
        showGrid={true}
        showFloatingElements={true}
        cost={25.0}
        credit={75.0}
      >
        <div
          style={{
            minHeight: '400px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
          }}
        >
          <div style={{ textAlign: 'center' }}>
            <h1 style={{ fontSize: '3rem', color: '#00ffff' }}>
              Cyberpunk Theme Active
            </h1>
            <p style={{ color: '#ff00de' }}>You should see:</p>
            <ul style={{ textAlign: 'left', color: '#00ff9f' }}>
              <li>Animated cityscape background</li>
              <li>Neon billboard at top</li>
              <li>Grid pattern overlay</li>
              <li>Glowing city lights</li>
              <li>Day/night transitions</li>
            </ul>
          </div>
        </div>
      </CyberpunkTheme>
    </div>
  );
};

export default CyberpunkDebug;
