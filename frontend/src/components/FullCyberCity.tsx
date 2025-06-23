import React from 'react';

/**
 * Renders the full cyberpunk city PNG with neon-glow filters.
 * The image file (aquaArtboard 2.png) should live in /public/assets.
 */
const FullCyberCity: React.FC<{ maxWidth?: number; height?: number }> = ({
  maxWidth = 1200,
  height = 320,
}) => (
  <div style={{ width: '100%', display: 'flex', justifyContent: 'center' }}>
    <img
      src="/assets/aquaArtboard 2.png"
      alt="Cyberpunk City Full"
      className="cyber-city-img"
      style={{ width: '100%', maxWidth, height, objectFit: 'cover' }}
    />
  </div>
);

export default FullCyberCity;