import { useState, useEffect } from 'react';
import { Alert, AlertTitle, AlertDescription } from '../components/ui/alert';
import { Skeleton } from '../components/ui/skeleton';

export default function Dashboard() {
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState<{
    totalAnalyses: number;
    modelsAvailable: number;
    avgProcessingTime: number;
  } | null>(null);

  useEffect(() => {
    // Simulate loading stats
    const timer = setTimeout(() => {
      setStats({
        totalAnalyses: 42,
        modelsAvailable: 6,
        avgProcessingTime: 3.2,
      });
      setIsLoading(false);
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="text-white space-y-6">
      <h1 className="text-2xl font-bold mb-2">Dashboard</h1>

      {/* Welcome Alert */}
      <Alert className="bg-blue-500/10 border-blue-500/50">
        <AlertTitle>Welcome back!</AlertTitle>
        <AlertDescription>
          Your AI orchestration system is ready. Check your stats below.
        </AlertDescription>
      </Alert>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Total Analyses */}
        <div className="glass-panel p-6 rounded-lg">
          <h3 className="text-sm font-medium opacity-70 mb-2">
            Total Analyses
          </h3>
          {isLoading ? (
            <Skeleton className="h-8 w-20" />
          ) : (
            <p className="text-3xl font-bold">{stats?.totalAnalyses}</p>
          )}
        </div>

        {/* Models Available */}
        <div className="glass-panel p-6 rounded-lg">
          <h3 className="text-sm font-medium opacity-70 mb-2">
            Models Available
          </h3>
          {isLoading ? (
            <Skeleton className="h-8 w-16" />
          ) : (
            <p className="text-3xl font-bold text-green-400">
              {stats?.modelsAvailable}
            </p>
          )}
        </div>

        {/* Avg Processing Time */}
        <div className="glass-panel p-6 rounded-lg">
          <h3 className="text-sm font-medium opacity-70 mb-2">
            Avg Processing Time
          </h3>
          {isLoading ? (
            <Skeleton className="h-8 w-24" />
          ) : (
            <p className="text-3xl font-bold">{stats?.avgProcessingTime}s</p>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="glass-panel p-6 rounded-lg">
        <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
        {isLoading ? (
          <div className="space-y-3">
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-12 w-full" />
          </div>
        ) : (
          <div className="text-sm opacity-60">
            No recent activity to display.
          </div>
        )}
      </div>
    </div>
  );
}
