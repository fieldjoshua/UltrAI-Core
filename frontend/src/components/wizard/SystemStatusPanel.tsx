import React from 'react';
import { Activity, Wifi, WifiOff, AlertCircle } from 'lucide-react';

export type ModelStatus = 'checking' | 'ready' | 'error';

export interface SystemStatusPanelProps {
  modelStatuses: Record<string, ModelStatus>;
  isDemoMode?: boolean;
  isStagingEnv?: boolean;
  isNonTimeSkin?: boolean;
}

export default function SystemStatusPanel({
  modelStatuses,
  isDemoMode = false,
  isStagingEnv = false,
  isNonTimeSkin = false,
}: SystemStatusPanelProps) {
  const readyCount = Object.values(modelStatuses).filter((s) => s === 'ready').length;
  const totalCount = Object.keys(modelStatuses).length;
  const allReady = readyCount === totalCount && totalCount > 0;
  const partialReady = readyCount > 0 && readyCount < totalCount;
  const noneReady = readyCount === 0;

  const getConnectionStatus = () => {
    if (allReady) return { icon: Wifi, label: 'Connected', color: 'text-green-400' };
    if (partialReady) return { icon: WifiOff, label: 'Partial connection', color: 'text-yellow-400' };
    return { icon: AlertCircle, label: 'Connection error', color: 'text-red-400' };
  };

  const connectionStatus = getConnectionStatus();
  const ConnectionIcon = connectionStatus.icon;

  const getStatusColor = () => {
    if (allReady) return 'bg-green-400';
    if (partialReady) return 'bg-yellow-400';
    return 'bg-red-400';
  };

  const latency = isDemoMode ? '~12ms' : '~250ms';

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
      aria-label={`System status: ${readyCount} of ${totalCount} models ready`}
    >
      {/* Connection status */}
      <div className="flex items-center gap-2">
        <ConnectionIcon
          className={`w-3 h-3 ${connectionStatus.color}`}
          aria-label={connectionStatus.label}
        />
        <span className="font-mono">
          {readyCount}/{totalCount}
        </span>
      </div>

      {/* Latency indicator */}
      <div className="flex items-center gap-2" aria-label={`Latency: ${latency}`}>
        <Activity className="w-3 h-3" aria-hidden="true" />
        <span className="font-mono">{latency}</span>
      </div>

      {/* Environment badges */}
      {(isDemoMode || isStagingEnv) && (
        <div className="flex items-center gap-2 ml-2 pl-2 border-l border-white/20">
          {isDemoMode && (
            <span
              className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-cyan-500/20 text-cyan-400"
              role="note"
              aria-label="Demo mode active"
            >
              DEMO
            </span>
          )}
          {isStagingEnv && (
            <span
              className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-orange-500/20 text-orange-400"
              role="note"
              aria-label="Staging environment"
            >
              STAGING
            </span>
          )}
        </div>
      )}

      {/* API status pulse */}
      <div className="flex items-center gap-2 ml-2 pl-2 border-l border-white/20">
        <div
          className={`w-2 h-2 rounded-full animate-pulse ${getStatusColor()}`}
          aria-hidden="true"
        />
        <span>API</span>
      </div>
    </div>
  );
}
