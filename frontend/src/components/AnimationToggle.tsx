import React from 'react';
import { useReducedMotion } from '../hooks/useReducedMotion';
import { Switch } from './ui/switch';

export const AnimationToggle: React.FC = () => {
  const prefersReducedMotion = useReducedMotion();
  const [animationsEnabled, setAnimationsEnabled] = React.useState(!prefersReducedMotion);

  React.useEffect(() => {
    // Update body class based on preference
    if (!animationsEnabled) {
      document.body.classList.add('reduce-motion');
    } else {
      document.body.classList.remove('reduce-motion');
    }
  }, [animationsEnabled]);

  return (
    <div className="flex items-center gap-2">
      <Switch
        id="animation-toggle"
        checked={animationsEnabled}
        onCheckedChange={setAnimationsEnabled}
        aria-label="Toggle animations"
      />
      <label 
        htmlFor="animation-toggle" 
        className="text-[11px] text-white/70 cursor-pointer select-none font-medium"
      >
        Animations
      </label>
    </div>
  );
};

export default AnimationToggle;