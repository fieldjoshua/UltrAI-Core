// Optimized background image paths
// Use .jpg for much smaller file sizes

export const getOptimizedBackground = (theme: string): string => {
  // Try to use optimized JPG first, fall back to PNG
  const backgrounds: Record<string, string> = {
    morning: '/bg-morning.jpg',
    afternoon: '/bg-afternoon.jpg',
    sunset: '/bg-sunset.jpg',
    night: '/bg-night.jpg',
    // Fallbacks
    'morning-png': '/bg-morning.png',
    'afternoon-png': '/bg-afternoon.png',
    'sunset-png': '/bg-sunset.png',
    'night-png': '/bg-night.png',
  };

  return backgrounds[theme] || backgrounds.night;
};

// Preload optimized image
export const preloadBackground = (theme: string): Promise<void> => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve();
    img.onerror = () => {
      // Try PNG fallback
      const fallbackImg = new Image();
      fallbackImg.onload = () => resolve();
      fallbackImg.onerror = reject;
      fallbackImg.src = getOptimizedBackground(`${theme}-png`);
    };
    img.src = getOptimizedBackground(theme);
  });
};
