import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import {
  BarChart3,
  Activity,
  HardDrive,
  Clock,
  FileText,
  Server,
  Layers,
  RefreshCw,
  Database,
  Cpu,
  MemoryStick,
} from 'lucide-react';

interface MetricsHistory {
  timestamps: string[];
  memory_usage: number[];
  processing_time: number[];
  requests_processed: number[];
  documents_processed: number[];
  chunks_processed: number[];
}

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

interface SystemMetrics {
  cpu_percent: number;
  disk_usage_percent: number;
  memory_usage_mb: number;
}

const API_URL = 'http://localhost:8081';
const HISTORY_LIMIT = 20; // Number of data points to keep in history

// Simple mini chart component
const MiniChart = React.memo(
  ({
    data,
    color = '#22d3ee',
    height = 40,
    width = 120,
    filled = false,
  }: {
    data: number[];
    color?: string;
    height?: number;
    width?: number;
    filled?: boolean;
  }) => {
    if (!data || data.length === 0) return null;

    // Calculate min/max for scaling
    const minValue = Math.min(...data);
    const maxValue = Math.max(...data);
    const range = maxValue - minValue || 1; // Avoid division by zero

    // Calculate points for the polyline
    const points = data
      .map((value, index) => {
        const x = (index / (data.length - 1)) * width;
        const normalizedValue = (value - minValue) / range;
        const y = height - normalizedValue * height;
        return `${x},${y}`;
      })
      .join(' ');

    // For filled chart, add bottom corners
    const areaPoints = filled ? `${points} ${width},${height} 0,${height}` : '';

    return (
      <svg width={width} height={height} className="overflow-visible">
        {filled ? (
          <polygon
            points={areaPoints}
            fill={`${color}20`} // Semi-transparent fill
            stroke="none"
          />
        ) : null}
        <polyline
          points={points}
          fill="none"
          stroke={color}
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    );
  }
);

MiniChart.displayName = 'MiniChart';

// Metric card component
const MetricCard = React.memo(
  ({
    title,
    value,
    unit = '',
    icon: Icon,
    history = [],
    chartColor = '#22d3ee',
    trend = 0,
  }: {
    title: string;
    value: number | string;
    unit?: string;
    icon: React.ElementType;
    history?: number[];
    chartColor?: string;
    trend?: number;
  }) => {
    // Determine trend indicator
    const trendIndicator = useMemo(() => {
      if (trend > 0) return <span className="text-green-500">↑</span>;
      if (trend < 0) return <span className="text-red-500">↓</span>;
      return null;
    }, [trend]);

    return (
      <div className="bg-gray-900/40 border border-gray-800 rounded-lg p-3 flex flex-col">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Icon className="w-4 h-4 text-gray-400" />
            <h3 className="text-sm text-gray-300">{title}</h3>
          </div>
          <div className="text-xs text-gray-500">{trendIndicator}</div>
        </div>

        <div className="flex items-center justify-between">
          <div className="text-xl font-medium text-cyan-300">
            {typeof value === 'number' ? value.toLocaleString() : value}
            <span className="text-xs text-gray-500 ml-1">{unit}</span>
          </div>

          <div className="h-10">
            {history.length > 1 && (
              <MiniChart
                data={history}
                color={chartColor}
                filled={true}
                height={40}
                width={80}
              />
            )}
          </div>
        </div>
      </div>
    );
  }
);

MetricCard.displayName = 'MetricCard';

// Main dashboard component
export const PerformanceDashboard = () => {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(
    null
  );
  const [healthResponse, setHealthResponse] = useState<any>(null);
  const [metricsHistory, setMetricsHistory] = useState<MetricsHistory>({
    timestamps: [],
    memory_usage: [],
    processing_time: [],
    requests_processed: [],
    documents_processed: [],
    chunks_processed: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Format time in a readable format
  const formatTime = useCallback((seconds: number): string => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    return [hrs > 0 ? `${hrs}h` : '', mins > 0 ? `${mins}m` : '', `${secs}s`]
      .filter(Boolean)
      .join(' ');
  }, []);

  // Calculate derived metrics
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
  }, [metrics, formatTime]);

  // Add metrics to history
  const updateMetricsHistory = useCallback((newMetrics: PerformanceMetrics) => {
    setMetricsHistory((prev) => {
      const now = new Date().toISOString();

      // Add new data points
      const timestamps = [...prev.timestamps, now].slice(-HISTORY_LIMIT);
      const memory_usage = [
        ...prev.memory_usage,
        newMetrics.current_memory_usage_mb,
      ].slice(-HISTORY_LIMIT);
      const processing_time = [
        ...prev.processing_time,
        newMetrics.avg_processing_time,
      ].slice(-HISTORY_LIMIT);
      const requests_processed = [
        ...prev.requests_processed,
        newMetrics.requests_processed,
      ].slice(-HISTORY_LIMIT);
      const documents_processed = [
        ...prev.documents_processed,
        newMetrics.documents_processed,
      ].slice(-HISTORY_LIMIT);
      const chunks_processed = [
        ...prev.chunks_processed,
        newMetrics.total_chunks_processed,
      ].slice(-HISTORY_LIMIT);

      return {
        timestamps,
        memory_usage,
        processing_time,
        requests_processed,
        documents_processed,
        chunks_processed,
      };
    });
  }, []);

  // Calculate trends (percentage change between most recent values)
  const calculateTrend = useCallback((data: number[]): number => {
    if (data.length < 2) return 0;

    const current = data[data.length - 1];
    const previous = data[data.length - 2];

    if (previous === 0) return 0;
    return ((current - previous) / previous) * 100;
  }, []);

  // Fetch performance metrics
  const fetchMetrics = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch from API
      const response = await axios.get(`${API_URL}/api/metrics`);
      const historyResponse = await axios.get(`${API_URL}/api/metrics/history`);
      const healthResp = await axios.get(`${API_URL}/health`);

      // Update state
      setMetrics(response.data);
      setSystemMetrics(healthResp.data.metrics);
      setHealthResponse(healthResp.data);

      // Update metrics history with data from history endpoint
      if (historyResponse.data) {
        setMetricsHistory({
          timestamps: historyResponse.data.timestamps || [],
          memory_usage: historyResponse.data.memory_usage || [],
          processing_time: historyResponse.data.avg_processing_time || [],
          requests_processed: historyResponse.data.requests_processed || [],
          documents_processed: historyResponse.data.documents_processed || [],
          chunks_processed: historyResponse.data.chunks_processed || [],
        });
      } else {
        // Fallback to updating with current metrics
        updateMetricsHistory(response.data);
      }
    } catch (err) {
      console.error('Error fetching performance metrics:', err);
      setError('Failed to load performance metrics');
    } finally {
      setLoading(false);
    }
  }, [updateMetricsHistory]);

  // Initial fetch and auto-refresh setup
  useEffect(() => {
    fetchMetrics();

    let intervalId: NodeJS.Timeout | null = null;

    if (autoRefresh) {
      intervalId = setInterval(fetchMetrics, 5000);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [autoRefresh, fetchMetrics]);

  // Toggle auto-refresh
  const toggleAutoRefresh = () => {
    setAutoRefresh((prev) => !prev);
  };

  // Dashboard layout
  return (
    <div className="min-h-screen bg-gray-900 text-gray-300 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <BarChart3 className="w-6 h-6 text-cyan-500" />
            <h1 className="text-xl font-bold text-cyan-300">
              Performance Dashboard
            </h1>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={fetchMetrics}
              className="flex items-center gap-1 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-md text-sm"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>

            <button
              onClick={toggleAutoRefresh}
              className={`
                flex items-center gap-1 px-3 py-1.5 rounded-md text-sm
                ${
                  autoRefresh
                    ? 'bg-cyan-900/50 text-cyan-300 hover:bg-cyan-900/70'
                    : 'bg-gray-800 hover:bg-gray-700'
                }
              `}
            >
              <Activity
                className={`w-4 h-4 ${autoRefresh ? 'text-cyan-400' : ''}`}
              />
              <span>
                {autoRefresh ? 'Auto-refresh On' : 'Auto-refresh Off'}
              </span>
            </button>
          </div>
        </div>

        {loading && !metrics ? (
          <div className="flex items-center justify-center h-64">
            <div className="flex flex-col items-center gap-3">
              <RefreshCw className="w-8 h-8 text-cyan-500 animate-spin" />
              <p className="text-gray-400">Loading metrics...</p>
            </div>
          </div>
        ) : error ? (
          <div className="bg-red-950/20 border border-red-900 rounded-lg p-6 text-center">
            <p className="text-red-400">{error}</p>
            <button
              onClick={fetchMetrics}
              className="mt-4 px-4 py-2 bg-red-900/30 hover:bg-red-900/50 rounded-md text-sm"
            >
              Retry
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {/* System overview */}
            <div className="bg-black/20 border border-gray-800 rounded-lg p-4">
              <h2 className="text-lg font-semibold text-cyan-300 mb-4">
                System Overview
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {systemMetrics && (
                  <>
                    <MetricCard
                      title="CPU Usage"
                      value={systemMetrics.cpu_percent.toFixed(1)}
                      unit="%"
                      icon={Cpu}
                      history={metricsHistory.processing_time}
                      chartColor="#22d3ee"
                      trend={calculateTrend(metricsHistory.processing_time)}
                    />

                    <MetricCard
                      title="Memory Usage"
                      value={systemMetrics.memory_usage_mb.toFixed(1)}
                      unit="MB"
                      icon={MemoryStick}
                      history={metricsHistory.memory_usage}
                      chartColor="#a855f7"
                      trend={calculateTrend(metricsHistory.memory_usage)}
                    />

                    <MetricCard
                      title="Disk Usage"
                      value={systemMetrics.disk_usage_percent.toFixed(1)}
                      unit="%"
                      icon={HardDrive}
                      chartColor="#f43f5e"
                    />
                  </>
                )}
              </div>
            </div>

            {/* Performance metrics */}
            {metrics && derivedMetrics && (
              <div className="bg-black/20 border border-gray-800 rounded-lg p-4">
                <h2 className="text-lg font-semibold text-cyan-300 mb-4">
                  Performance Metrics
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <MetricCard
                    title="Requests Processed"
                    value={metrics.requests_processed}
                    icon={Activity}
                    history={metricsHistory.requests_processed}
                    chartColor="#3b82f6"
                    trend={calculateTrend(metricsHistory.requests_processed)}
                  />

                  <MetricCard
                    title="Documents Processed"
                    value={metrics.documents_processed}
                    icon={FileText}
                    history={metricsHistory.documents_processed}
                    chartColor="#f97316"
                    trend={calculateTrend(metricsHistory.documents_processed)}
                  />

                  <MetricCard
                    title="Total Chunks"
                    value={metrics.total_chunks_processed}
                    icon={Layers}
                    history={metricsHistory.chunks_processed}
                    chartColor="#84cc16"
                    trend={calculateTrend(metricsHistory.chunks_processed)}
                  />

                  <MetricCard
                    title="Avg Processing Time"
                    value={metrics.avg_processing_time.toFixed(2)}
                    unit="s"
                    icon={Clock}
                    history={metricsHistory.processing_time}
                    chartColor="#22d3ee"
                  />

                  <MetricCard
                    title="Memory Cache Size"
                    value={metrics.cache_stats?.memory_cache_size || 0}
                    unit="items"
                    icon={Database}
                    chartColor="#a855f7"
                  />

                  <MetricCard
                    title="Peak Memory Usage"
                    value={metrics.max_memory_usage.toFixed(1)}
                    unit="MB"
                    icon={MemoryStick}
                    chartColor="#f43f5e"
                  />
                </div>
              </div>
            )}

            {/* Additional metrics */}
            {metrics && derivedMetrics && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-black/20 border border-gray-800 rounded-lg p-4">
                  <h2 className="text-lg font-semibold text-cyan-300 mb-4">
                    Efficiency
                  </h2>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-gray-400" />
                        <span className="text-sm">
                          Average document processing time
                        </span>
                      </div>
                      <span className="text-cyan-300 font-mono">
                        {derivedMetrics.avgDocumentTime.toFixed(2)}s
                      </span>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Layers className="w-4 h-4 text-gray-400" />
                        <span className="text-sm">
                          Chunks per document (avg)
                        </span>
                      </div>
                      <span className="text-cyan-300 font-mono">
                        {derivedMetrics.chunksPerDocument.toFixed(1)}
                      </span>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Database className="w-4 h-4 text-gray-400" />
                        <span className="text-sm">Cache hit rate</span>
                      </div>
                      <span className="text-cyan-300 font-mono">
                        {(derivedMetrics.cacheHitRate * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>

                <div className="bg-black/20 border border-gray-800 rounded-lg p-4">
                  <h2 className="text-lg font-semibold text-cyan-300 mb-4">
                    System Info
                  </h2>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-gray-400" />
                        <span className="text-sm">Uptime</span>
                      </div>
                      <span className="text-cyan-300 font-mono">
                        {derivedMetrics.uptimeFormatted}
                      </span>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Server className="w-4 h-4 text-gray-400" />
                        <span className="text-sm">Server started</span>
                      </div>
                      <span className="text-cyan-300 font-mono">
                        {new Date(metrics.start_time).toLocaleString()}
                      </span>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Activity className="w-4 h-4 text-gray-400" />
                        <span className="text-sm">Status</span>
                      </div>
                      <span className="text-green-400 font-medium">
                        Operational
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* System information section */}
            {healthResponse && healthResponse.system_info && (
              <div className="bg-black/20 border border-gray-800 rounded-lg p-4 mt-6">
                <h2 className="text-lg font-semibold text-cyan-300 mb-4">
                  System Information
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Server className="w-4 h-4 text-gray-400" />
                        <span className="text-sm">Platform</span>
                      </div>
                      <span className="text-cyan-300 font-mono">
                        {healthResponse.system_info.platform}
                      </span>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Cpu className="w-4 h-4 text-gray-400" />
                        <span className="text-sm">CPU Cores</span>
                      </div>
                      <span className="text-cyan-300 font-mono">
                        {healthResponse.system_info.cpu_count}
                      </span>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <MemoryStick className="w-4 h-4 text-gray-400" />
                        <span className="text-sm">Total Memory</span>
                      </div>
                      <span className="text-cyan-300 font-mono">
                        {healthResponse.system_info.memory_total.toFixed(2)} GB
                      </span>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Activity className="w-4 h-4 text-gray-400" />
                        <span className="text-sm">Python Version</span>
                      </div>
                      <span className="text-cyan-300 font-mono">
                        {
                          healthResponse.system_info.python_version.split(
                            ' '
                          )[0]
                        }
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PerformanceDashboard;
