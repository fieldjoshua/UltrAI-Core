import { useEffect, useState } from 'react';

export default function DemoIndicator() {
  const [isVisible, setIsVisible] = useState(false);
  const isDemoMode =
    import.meta.env.VITE_API_MODE === 'mock' ||
    import.meta.env.VITE_DEMO_MODE === 'true';

  useEffect(() => {
    if (isDemoMode) {
      setIsVisible(true);
    }
  }, [isDemoMode]);

  if (!isVisible) return null;

  return (
    <div className="fixed top-4 right-4 z-50 animate-fade-in">
      <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-green-500/20 to-cyan-500/20 border border-green-400/30 backdrop-blur-md">
        <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
        <span className="text-xs font-medium text-green-300">
          Demo Environment
        </span>
      </div>
    </div>
  );
}
