import React from 'react';

const CyberpunkCity: React.FC = () => (
  <svg
    viewBox="0 0 1840 1035"
    xmlns="http://www.w3.org/2000/svg"
    className="cyberpunk-svg"
    style={{
      width: '100%',
      maxWidth: 900,
      height: 220,
      display: 'block',
      margin: '0 auto',
    }}
  >
    {/* Example buildings (replace with actual paths for more detail) */}
    <g className="cyber-building">
      <rect x="200" y="700" width="80" height="250" rx="8" />
      <rect x="320" y="800" width="60" height="150" rx="6" />
      <rect x="420" y="750" width="100" height="200" rx="10" />
    </g>
    {/* Example bridge */}
    <g className="cyber-bridge">
      <rect x="600" y="900" width="400" height="30" rx="15" />
      <ellipse cx="800" cy="915" rx="200" ry="20" />
    </g>
    {/* Background city silhouette (stylized, simple) */}
    <g className="cyber-background">
      <rect x="0" y="950" width="1840" height="85" />
    </g>
  </svg>
);

export default CyberpunkCity;
