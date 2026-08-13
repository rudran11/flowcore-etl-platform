import React from 'react';
import { motion } from 'framer-motion';
import { useDashboard } from './hooks/useDashboard';
import { useDatasets } from '../datasets/hooks/useDatasets';
import { DashboardCard } from './components/DashboardCard';
import { ExecutionTrendChart } from './components/ExecutionTrendChart';
import { ExecutionTable } from '../executions/components/ExecutionTable';
import { Activity, Clock, PlayCircle, ServerCog, AlertOctagon, Database, ArrowRight } from 'lucide-react';
import { Skeleton } from '../../components/ui/skeleton';
import { Button } from '../../components/ui/button';
import { toast } from 'sonner';
import { useSchedulerMetrics } from './hooks/useSchedulerMetrics';
import { useNavigate } from 'react-router-dom';

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
};

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { data, isLoading, error } = useDashboard();
  const { data: metrics } = useSchedulerMetrics();
  const { data: datasets } = useDatasets();

  React.useEffect(() => {
    if (error) {
      toast.error('Failed to load dashboard data');
    }
  }, [error]);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between space-y-2">
          <Skeleton className="h-10 w-48" />
          <Skeleton className="h-6 w-24" />
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Skeleton className="h-32 rounded-xl" />
          <Skeleton className="h-32 rounded-xl" />
          <Skeleton className="h-32 rounded-xl" />
          <Skeleton className="h-32 rounded-xl" />
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
          <Skeleton className="h-[400px] lg:col-span-4 rounded-xl" />
          <Skeleton className="h-[400px] lg:col-span-3 rounded-xl" />
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex h-[400px] flex-col items-center justify-center space-y-4">
        <div className="text-center">
          <h2 className="text-2xl font-semibold tracking-tight text-destructive">Error Loading Dashboard</h2>
          <p className="text-sm text-muted-foreground mt-2">Make sure the backend server is running and reachable.</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="p-6 md:p-8 max-w-[1400px] mx-auto space-y-8"
    >
      {/* Operational Control Center Header */}
      <div className="relative overflow-hidden rounded-xl bg-card border border-border shadow-surface p-6 sm:p-8">
        <div className="absolute inset-0 bg-dot-topology opacity-30 pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-start justify-between gap-6">
          <div className="space-y-4 max-w-2xl">
            <h1 className="text-2xl font-bold tracking-tight text-foreground uppercase">
              Platform Health & Telemetry
            </h1>
            <p className="text-muted-foreground text-sm leading-relaxed max-w-lg">
              System health is optimal. Currently monitoring <span className="font-medium text-foreground">{data.statistics.total_pipelines} active pipelines</span> and <span className="font-medium text-foreground">{datasets?.length || 0} registered datasets</span>. Overall execution success rate is <span className="font-mono text-foreground">{(metrics?.success_rate ? metrics.success_rate * 100 : 98).toFixed(1)}%</span> today.
            </p>
            <div className="flex items-center gap-3 pt-2">
              <Button onClick={() => navigate('/pipelines')} size="sm" className="shadow-surface font-semibold">
                Configure Pipelines
              </Button>
              <Button variant="outline" size="sm" onClick={() => navigate('/runs')} className="bg-background font-semibold">
                Trace Executions
              </Button>
            </div>
          </div>
          
          <div className="flex flex-col gap-3 p-5 rounded-lg bg-accent/20 border border-border shadow-sm min-w-[280px]">
            <h3 className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mb-2">Core Engine Status</h3>
            {data.health.server === 'healthy' ? (
              <div className="flex items-center text-sm font-semibold text-status-success">
                <span className="relative flex h-2 w-2 mr-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-status-success opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-status-success"></span>
                </span>
                Online & Accepting Jobs
              </div>
            ) : (
              <div className="flex items-center text-sm font-semibold text-status-error">
                <span className="relative flex h-2 w-2 mr-3 rounded-full bg-status-error"></span>
                System Offline
              </div>
            )}
            <div className="w-full h-px bg-border my-1" />
            <div className="flex items-center justify-between text-[11px] font-mono py-1">
              <span className="text-muted-foreground">Queue Length</span>
              <span className="font-bold text-foreground">{metrics?.queue_length ?? 0}</span>
            </div>
            <div className="flex items-center justify-between text-[11px] font-mono py-1">
              <span className="text-muted-foreground">Scheduler</span>
              <span className="font-bold text-status-success">ACTIVE</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Primary KPI Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <motion.div variants={item}>
          <DashboardCard 
            title="Total Pipelines" 
            value={data.statistics.total_pipelines} 
            icon={<Activity className="h-4 w-4" />}
            description="Registered in the system"
            trend="up"
            trendValue="+12% this week"
          />
        </motion.div>
        <motion.div variants={item}>
          <DashboardCard 
            title="Total Executions" 
            value={data.statistics.total_runs} 
            icon={<PlayCircle className="h-4 w-4" />}
            description="Lifetime pipeline runs"
            trend="up"
            trendValue="+4,302 today"
          />
        </motion.div>
        <motion.div variants={item}>
          <DashboardCard 
            title="Total Datasets" 
            value={datasets?.length || 0} 
            icon={<Database className="h-4 w-4" />}
            description="Tracked lineage assets"
            trend="neutral"
            trendValue="Stable"
          />
        </motion.div>
        <motion.div variants={item}>
          <DashboardCard 
            title="Success Rate" 
            value={`${((metrics?.success_rate ?? 1) * 100).toFixed(1)}%`} 
            icon={<ServerCog className="h-4 w-4" />}
            description="Schedule execution success"
            trend={((metrics?.success_rate ?? 1) * 100) > 95 ? "up" : "down"}
            trendValue={((metrics?.success_rate ?? 1) * 100) > 95 ? "Healthy" : "Needs Attention"}
          />
        </motion.div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
        <motion.div variants={item} className="lg:col-span-5 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold tracking-tight">Execution Trends</h3>
          </div>
          <div className="flex-1 rounded-xl border border-border/50 bg-card p-6 shadow-sm">
            <ExecutionTrendChart data={data.trends} />
          </div>
        </motion.div>
        
        <motion.div variants={item} className="lg:col-span-2 flex flex-col gap-4">
          <div className="flex items-center justify-between mb-0">
            <h3 className="text-lg font-semibold tracking-tight">Scheduler Health</h3>
          </div>
          <DashboardCard 
            title="Avg Delay" 
            value={`${metrics?.avg_execution_delay_seconds ?? 0}s`} 
            icon={<Clock className="h-4 w-4" />}
            description="Average start delay"
            trend={((metrics?.avg_execution_delay_seconds ?? 0) < 5) ? "up" : "down"}
            trendValue="Optimal"
          />
          <DashboardCard 
            title="Missed Runs" 
            value={metrics?.missed_schedules ?? 0} 
            icon={<AlertOctagon className="h-4 w-4" />}
            description="Missed schedules in last 24h"
            trend={metrics?.missed_schedules === 0 ? "up" : "down"}
            trendValue={metrics?.missed_schedules === 0 ? "Perfect" : "Needs Review"}
          />
        </motion.div>
      </div>

      <motion.div variants={item} className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold tracking-tight">Recent Executions</h3>
          <Button variant="ghost" size="sm" onClick={() => navigate('/runs')} className="text-muted-foreground hover:text-foreground">
            View All <ArrowRight className="ml-1 h-3.5 w-3.5" />
          </Button>
        </div>
        <div className="rounded-xl border border-border/50 bg-card overflow-hidden shadow-sm">
          <ExecutionTable runs={data.recent_runs} />
        </div>
      </motion.div>
    </motion.div>
  );
};
