import { cn } from "../lib/utils";

interface LoadingSkeletonProps {
  className?: string;
  variant?: 'text' | 'card' | 'button' | 'input';
  count?: number;
}

export function LoadingSkeleton({ 
  className, 
  variant = 'text',
  count = 1 
}: LoadingSkeletonProps) {
  const baseClasses = "animate-pulse bg-gradient-to-r from-white/10 via-white/20 to-white/10 rounded";
  
  const variantClasses = {
    text: "h-4 w-full",
    card: "h-32 w-full rounded-lg",
    button: "h-10 w-32 rounded-md",
    input: "h-10 w-full rounded-md"
  };

  const skeletons = Array.from({ length: count }, (_, i) => (
    <div
      key={i}
      className={cn(baseClasses, variantClasses[variant], className)}
      style={{
        backgroundSize: '200% 100%',
        animation: 'shimmer 2s ease-in-out infinite'
      }}
    />
  ));

  return <>{skeletons}</>;
}

// Add shimmer animation to global styles
const style = document.createElement('style');
style.textContent = `
  @keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
  }
`;
document.head.appendChild(style);