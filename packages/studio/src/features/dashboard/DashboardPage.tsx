import React from 'react';
import { useDashboard } from './hooks/useDashboard';
import { DashboardCard } from './components/DashboardCard';
import { DashboardGrid } from './components/DashboardGrid';
import { ExecutionTrendChart } from './components/ExecutionTrendChart';
import { RecentRunsTable } from './components/RecentRunsTable';
import { Activity, Clock, PlayCircle, CheckCircle2 } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { data, isLoading, error } = useDashboard();

  if (isLoading) {
    return <div className="p-8 text-center text-muted-foreground animate-pulse">Loading dashboard...</div>;
  }

  if (error || !data) {
    return (
      <div className="p-8">
        <div className="rounded-md bg-destructive/15 p-4 text-destructive">
          Error loading dashboard data. Make sure the backend server is running.
        </div>
      </div>
    );
  }

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms.toFixed(0)}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
        <div className="flex items-center space-x-2">
          {data.health.server === 'healthy' ? (
            <div className="flex items-center text-sm text-emerald-500">
              <div className="h-2 w-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></div>
              System Online
            </div>
          ) : (
            <div className="flex items-center text-sm text-destructive">
              <div className="h-2 w-2 rounded-full bg-destructive mr-2"></div>
              System Offline
            </div>
          )}
        </div>
      </div>
      
      <DashboardGrid>
        <DashboardCard 
          title="Total Pipelines" 
          value={data.statistics.total_pipelines} 
          icon={<Activity className="h-4 w-4" />}
          description="Registered in the system"
        />
        <DashboardCard 
          title="Total Executions" 
          value={data.statistics.total_runs} 
          icon={<PlayCircle className="h-4 w-4" />}
          description="Lifetime pipeline runs"
        />
        <DashboardCard 
          title="Success Rate" 
          value={`${data.statistics.success_rate}%`} 
          icon={<CheckCircle2 className="h-4 w-4 text-emerald-500" />}
          description="Across all terminal runs"
        />
        <DashboardCard 
          title="Avg. Duration" 
          value={formatDuration(data.statistics.avg_duration_ms)} 
          icon={<Clock className="h-4 w-4" />}
          description="For completed runs"
        />
      </DashboardGrid>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <ExecutionTrendChart data={data.trends} />
        <RecentRunsTable runs={data.recent_runs} />
      </div>
    </div>
  );
};
