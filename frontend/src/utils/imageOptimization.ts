// Image optimization utilities for background images

interface GradientColors {
  [theme: string]: string[];
}

interface ImageResult {
  full: string;
  placeholder: string;
}

export const optimizeBackgroundImages = () => {
  // Create low-quality placeholders using canvas
  const createPlaceholder = (theme: string): string => {
    const canvas = document.createElement('canvas');
    canvas.width = 32; // Very small for fast loading
    canvas.height = 18;
    const ctx = canvas.getContext('2d');
    
    if (!ctx) {
      return '';
    }

    // Create gradient based on theme
    const gradients: GradientColors = {
      morning: ['#FFD6A5', '#FFAB91', '#FF7043'],
      afternoon: ['#81D4FA', '#4FC3F7', '#29B6F6'],
      sunset: ['#FF8A65', '#FF7043', '#FF5722'],
      night: ['#303F9F', '#283593', '#1A237E'],
    };

    const colors = gradients[theme] || gradients.night;
    const gradient = ctx.createLinearGradient(
      0,
      0,
      canvas.width,
      canvas.height
    );
    gradient.addColorStop(0, colors[0]);
    gradient.addColorStop(0.5, colors[1]);
    gradient.addColorStop(1, colors[2]);

    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    return canvas.toDataURL('image/jpeg', 0.7);
  };

  // Preload images with progressive enhancement
  const preloadWithBlur = (imageSrc: string, theme: string): Promise<ImageResult> => {
    return new Promise(resolve => {
      // First show placeholder
      const placeholder = createPlaceholder(theme);

      // Then load full image
      const img = new Image();
      img.onload = () => resolve({ full: imageSrc, placeholder });
      img.onerror = () => resolve({ full: placeholder, placeholder });
      img.src = imageSrc;
    });
  };

  return { createPlaceholder, preloadWithBlur };
};

// CSS for blur-up effect
export const blurUpStyles = `
  .bg-blur-up {
    position: relative;
    overflow: hidden;
  }
  
  .bg-blur-up::before {
    content: '';
    position: absolute;
    inset: 0;
    background-size: cover;
    background-position: center;
    filter: blur(20px);
    transform: scale(1.1);
    transition: opacity 0.8s ease-out;
    z-index: 1;
  }
  
  .bg-blur-up::after {
    content: '';
    position: absolute;
    inset: 0;
    background-size: cover;
    background-position: center;
    opacity: 0;
    transition: opacity 0.8s ease-out;
    z-index: 2;
  }
  
  .bg-blur-up.loaded::before {
    opacity: 0;
  }
  
  .bg-blur-up.loaded::after {
    opacity: 1;
  }
`;