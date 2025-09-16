import React, { memo } from 'react';
import { Activity, Wifi, WifiOff, AlertCircle } from 'lucide-react';

interface SystemStatusPanelProps {
  modelStatuses: Record<string, 'checking' | 'ready' | 'error'>;
  isNonTimeSkin: boolean;
  isDemoMode: boolean;
  isStagingEnv: boolean;
}

const SystemStatusPanel = memo(function SystemStatusPanel({
  modelStatuses,
  isNonTimeSkin,
  isDemoMode,
  isStagingEnv,
}: SystemStatusPanelProps) {
  const readyModels = Object.values(modelStatuses).filter(s => s === 'ready').length;
  const totalModels = Object.keys(modelStatuses).length;
  const allReady = readyModels === totalModels && totalModels > 0;

  return (
    <div
      className={`
        absolute bottom-6 left-6 
        px-4 py-2 rounded-lg backdrop-blur-sm text-xs
        ${isNonTimeSkin ? 'bg-gray-100/80 text-gray-600' : 'bg-black/30 text-white/60'}
        flex items-center gap-3
      `}
      role="status"
      aria-live="polite"
    >
      {/* Connection status */}
      <div className="flex items-center gap-2">
        {allReady ? (
          <Wifi className="w-3 h-3 text-green-400" aria-label="Connected" />
        ) : readyModels > 0 ? (
          <WifiOff className="w-3 h-3 text-yellow-400" aria-label="Partial connection" />
        ) : (
          <AlertCircle className="w-3 h-3 text-red-400" aria-label="Connection error" />
        )}
        <span className="font-mono">
          {readyModels}/{totalModels}
        </span>
      </div>

      {/* Latency indicator */}
      <div className="flex items-center gap-2">
        <Activity className="w-3 h-3" />
        <span className="font-mono">
          {isDemoMode ? '~12ms' : '~250ms'}
        </span>
      </div>

      {/* Environment indicator */}
      {(isDemoMode || isStagingEnv) && (
        <div className="flex items-center gap-2 ml-2 pl-2 border-l border-white/20">
          <span className={`
            px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider
            ${isDemoMode 
              ? 'bg-cyan-500/20 text-cyan-400' 
              : 'bg-orange-500/20 text-orange-400'
            }
          `}>
            {isDemoMode ? 'DEMO' : 'STAGING'}
          </span>
        </div>
      )}

      {/* API status */}
      <div className="flex items-center gap-2 ml-2 pl-2 border-l border-white/20">
        <div className={`
          w-2 h-2 rounded-full animate-pulse
          ${allReady ? 'bg-green-400' : readyModels > 0 ? 'bg-yellow-400' : 'bg-red-400'}
        `} />
        <span>API</span>
      </div>
    </div>
  );
});

export default SystemStatusPanel;