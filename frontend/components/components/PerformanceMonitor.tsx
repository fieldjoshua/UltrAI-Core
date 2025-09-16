import React, { useState, useEffect, useMemo } from 'react';
import {
  Activity,
  BarChart3,
  Memory,
  Clock,
  FileText,
  RefreshCw,
  Server,
} from 'lucide-react';
import axios from 'axios';

interface PerformanceMetrics {
  requests_processed: number;
  documents_processed: number;
  avg_processing_time: number;
  total_processing_time: number;
  max_memory_usage: number;
  total_chunks_processed: number;
  cache_hits: number;
  current_memory_usage_mb: number;
  uptime_seconds: number;
  start_time: string;
  cache_stats?: {
    memory_cache_size?: number;
  };
}

const API_URL = 'http://localhost:8081';

// Thin gauge component for visualizing metrics
const PerformanceGauge = React.memo(
  ({
    value,
    maxValue,
    label,
    color = 'bg-cyan-500',
    icon: Icon,
  }: {
    value: number;
    maxValue: number;
    label: string;
    color?: string;
    icon: React.ElementType;
  }) => {
    // Calculate percentage with safety check
    const percentage = useMemo(() => {
      const calculatedPercentage = Math.min(100, (value / maxValue) * 100 || 0);
      return Math.max(0, calculatedPercentage); // Ensure it's not negative
    }, [value, maxValue]);

    return (
      <div className="space-y-1">
        <div className="flex items-center justify-between text-xs mb-1">
          <div className="flex items-center gap-1">
            <Icon className="w-3 h-3 text-gray-400" />
            <span className="text-gray-400">{label}</span>
          </div>
          <span className="text-gray-300 font-mono">
            {value.toFixed(value < 10 ? 1 : 0)}
          </span>
        </div>
        <div className="w-full bg-gray-800 h-1.5 rounded-full overflow-hidden">
          <div
            className={`h-full ${color} transition-all duration-500 ease-out rounded-full`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
    );
  }
);

PerformanceGauge.displayName = 'PerformanceGauge';

// Main component
export const PerformanceMonitor = React.memo(() => {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Format time in a readable format
  const formatTime = (seconds: number): string => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    return [hrs > 0 ? `${hrs}h` : '', mins > 0 ? `${mins}m` : '', `${secs}s`]
      .filter(Boolean)
      .join(' ');
  };

  // Calculate additional metrics
  const derivedMetrics = useMemo(() => {
    if (!metrics) return null;

    const avgDocumentTime =
      metrics.documents_processed > 0
        ? metrics.total_processing_time / metrics.documents_processed
        : 0;

    const chunksPerDocument =
      metrics.documents_processed > 0
        ? metrics.total_chunks_processed / metrics.documents_processed
        : 0;

    const cacheHitRate =
      metrics.requests_processed + metrics.documents_processed > 0
        ? metrics.cache_hits /
          (metrics.requests_processed + metrics.documents_processed)
        : 0;

    return {
      avgDocumentTime,
      chunksPerDocument,
      cacheHitRate,
      uptimeFormatted: formatTime(metrics.uptime_seconds),
    };
  }, [metrics]);

  // Fetch performance metrics
  const fetchMetrics = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await axios.get(`${API_URL}/api/metrics`);
      setMetrics(response.data);
    } catch (err) {
      console.error('Error fetching performance metrics:', err);
      setError('Failed to load performance metrics');
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch and auto-refresh setup
  useEffect(() => {
    fetchMetrics();

    let intervalId: NodeJS.Timeout | null = null;

    if (autoRefresh) {
      intervalId = setInterval(fetchMetrics, 5000); // Refresh every 5 seconds
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [autoRefresh]);

  // Handle manual refresh
  const handleRefresh = () => {
    fetchMetrics();
  };

  // Handle auto-refresh toggle
  const toggleAutoRefresh = () => {
    setAutoRefresh(prev => !prev);
  };

  if (loading && !metrics) {
    return (
      <div className="bg-black/20 border border-gray-800 rounded-lg p-3 animate-pulse text-center">
        <Activity className="w-5 h-5 text-cyan-500 mx-auto mb-2 animate-pulse" />
        <p className="text-gray-400 text-sm">Loading performance metrics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-950/20 border border-red-900 rounded-lg p-3 text-center">
        <Activity className="w-5 h-5 text-red-500 mx-auto mb-2" />
        <p className="text-red-400 text-sm">{error}</p>
      </div>
    );
  }

  return (
    <div className="bg-black/20 border border-gray-800 rounded-lg p-4 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-cyan-500" />
          <h3 className="text-cyan-300 font-semibold">System Performance</h3>
        </div>
        <div className="flex gap-2">
          <button
            className={`
              p-1.5 rounded-full text-gray-400 hover:text-cyan-400 focus:outline-none
              ${autoRefresh ? 'bg-cyan-950 text-cyan-400' : 'hover:bg-gray-800'}
            `}
            onClick={toggleAutoRefresh}
            title={autoRefresh ? 'Auto-refresh on' : 'Auto-refresh off'}
          >
            <RefreshCw
              className={`w-3.5 h-3.5 ${autoRefresh ? 'animate-spin' : ''}`}
            />
          </button>

          <button
            className="p-1.5 rounded-full text-gray-400 hover:text-cyan-400 hover:bg-gray-800 focus:outline-none"
            onClick={handleRefresh}
            title="Refresh now"
          >
            <Server className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {metrics && derivedMetrics && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-3">
              <PerformanceGauge
                value={metrics.current_memory_usage_mb}
                maxValue={1024} // 1GB
                label="Memory Usage (MB)"
                color="bg-purple-500"
                icon={Memory}
              />

              <PerformanceGauge
                value={metrics.avg_processing_time}
                maxValue={5} // 5 seconds
                label="Avg Processing Time (s)"
                color="bg-cyan-500"
                icon={Clock}
              />

              <PerformanceGauge
                value={derivedMetrics.chunksPerDocument}
                maxValue={20} // 20 chunks per document
                label="Chunks per Document"
                color="bg-green-500"
                icon={FileText}
              />
            </div>

            <div className="space-y-3">
              <PerformanceGauge
                value={derivedMetrics.cacheHitRate * 100}
                maxValue={100} // 100%
                label="Cache Hit Rate (%)"
                color="bg-yellow-500"
                icon={Activity}
              />

              <PerformanceGauge
                value={metrics.requests_processed}
                maxValue={100} // 100 requests
                label="Requests Processed"
                color="bg-blue-500"
                icon={Server}
              />

              <PerformanceGauge
                value={metrics.documents_processed}
                maxValue={50} // 50 documents
                label="Documents Processed"
                color="bg-pink-500"
                icon={FileText}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs text-gray-400 mt-2 border-t border-gray-800 pt-2">
            <div>
              <div className="flex justify-between">
                <span>Uptime:</span>
                <span className="text-gray-300">
                  {derivedMetrics.uptimeFormatted}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Memory Cache Items:</span>
                <span className="text-gray-300">
                  {metrics.cache_stats?.memory_cache_size || 0}
                </span>
              </div>
            </div>
            <div>
              <div className="flex justify-between">
                <span>Total Chunks:</span>
                <span className="text-gray-300">
                  {metrics.total_chunks_processed}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Peak Memory (MB):</span>
                <span className="text-gray-300">
                  {metrics.max_memory_usage.toFixed(1)}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
});

PerformanceMonitor.displayName = 'PerformanceMonitor';
