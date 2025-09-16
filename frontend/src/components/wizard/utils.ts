// Utility functions for wizard components

export const mapColorHex = (color: string): string => {
  const colorMap: Record<string, string> = {
    mint: '#00ff9f',
    blue: '#00d4ff',
    purple: '#bd00ff',
    pink: '#ff6cfc',
    orange: '#ff6600',
    yellow: '#ffd700',
    green: '#00ff00',
    red: '#ff3366',
  };
  return colorMap[color] || '#ffffff';
};

export const mapColorRGBA = (color: string, alpha: number): string => {
  const hex = mapColorHex(color);
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

export const getGlassBackground = (isNonTimeSkin: boolean): string => {
  return isNonTimeSkin
    ? 'rgba(255, 255, 255, 0.05)'
    : 'rgba(0, 0, 0, 0.4)';
};

export const getGlassBorder = (isNonTimeSkin: boolean): string => {
  return isNonTimeSkin
    ? 'rgba(255, 255, 255, 0.1)'
    : 'rgba(255, 255, 255, 0.15)';
};

export const getTextColor = (isNonTimeSkin: boolean): string => {
  return isNonTimeSkin ? 'text-gray-900' : 'text-white';
};

export const getGradientText = (): React.CSSProperties => ({
  background: 'linear-gradient(90deg, #00ff9f, #00d4ff, #bd00ff)',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  backgroundClip: 'text',
  textShadow: 'none',
});

export const getAnimatedBillboardStyle = (): React.CSSProperties => ({
  background: 'linear-gradient(45deg, rgba(0,0,0,0.8), rgba(0,0,0,0.6))',
  border: '3px solid transparent',
  borderImage: 'linear-gradient(45deg, #ff6600, #00ff9f, #00d4ff, #bd00ff) 1',
  boxShadow: '0 0 80px rgba(255,102,0,0.4), inset 0 0 60px rgba(0,255,159,0.1)',
  animation: 'ultrai-billboard-sweep 3s ease-in-out infinite',
  backgroundSize: '200% 200%',
});