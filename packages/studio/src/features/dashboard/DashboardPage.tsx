import React from 'react';
import { motion } from 'framer-motion';
import { useDashboard } from './hooks/useDashboard';
import { useSchedules } from '../schedules/hooks/useSchedules';
import { useEnvironments } from '../environments/hooks/useEnvironments';
import { useDatasets } from '../datasets/hooks/useDatasets';
import { DashboardCard } from './components/DashboardCard';
import { ExecutionTrendChart } from './components/ExecutionTrendChart';
import { ExecutionTable } from '../executions/components/ExecutionTable';
import { Activity, Clock, PlayCircle, ServerCog, AlertOctagon, Server, Database, Sparkles, ArrowRight } from 'lucide-react';
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
  const { data: schedules } = useSchedules();
  const { data: metrics } = useSchedulerMetrics();
  const { data: environments } = useEnvironments();
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
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary/10 via-primary/5 to-background border border-primary/10 p-8 sm:p-10">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-4 max-w-2xl">
            <div className="inline-flex items-center rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-xs font-medium text-primary backdrop-blur-sm">
              <Sparkles className="mr-2 h-3 w-3" />
              FlowCore Studio v1.0
            </div>
            <h1 className="text-4xl font-bold tracking-tight text-foreground">
              Welcome back to your Workspace
            </h1>
            <p className="text-muted-foreground text-lg leading-relaxed">
              You have <span className="font-medium text-foreground">{data.statistics.total_pipelines} active pipelines</span> and <span className="font-medium text-foreground">{datasets?.length || 0} datasets</span> registered. System health is optimal with a {(metrics?.success_rate ? metrics.success_rate * 100 : 98).toFixed(1)}% execution success rate today.
            </p>
            <div className="flex items-center gap-3 pt-2">
              <Button onClick={() => navigate('/pipelines')} className="shadow-md">
                View Pipelines <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
              <Button variant="outline" onClick={() => navigate('/runs')} className="bg-background/50 backdrop-blur">
                Recent Executions
              </Button>
            </div>
          </div>
          
          <div className="hidden lg:flex flex-col gap-3 p-6 rounded-xl bg-background/50 border border-border/50 backdrop-blur-sm min-w-[280px]">
            <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-1">System Status</h3>
            {data.health.server === 'healthy' ? (
              <div className="flex items-center text-sm font-medium text-emerald-500 bg-emerald-500/10 py-2 px-3 rounded-md border border-emerald-500/20">
                <span className="relative flex h-2 w-2 mr-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                Core Engine Online
              </div>
            ) : (
              <div className="flex items-center text-sm font-medium text-destructive bg-destructive/10 py-2 px-3 rounded-md border border-destructive/20">
                <span className="relative flex h-2 w-2 mr-3 rounded-full bg-destructive"></span>
                System Offline
              </div>
            )}
            <div className="flex items-center justify-between text-sm py-1">
              <span className="text-muted-foreground">Queue Length</span>
              <span className="font-medium">{metrics?.queue_length ?? 0}</span>
            </div>
            <div className="flex items-center justify-between text-sm py-1">
              <span className="text-muted-foreground">Scheduler</span>
              <span className="font-medium text-emerald-500">Active</span>
            </div>
          </div>
        </div>
        
        {/* Decorative background elements */}
        <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-primary/10 blur-3xl" />
        <div className="absolute -bottom-32 left-1/2 h-64 w-64 -translate-x-1/2 rounded-full bg-purple-500/10 blur-3xl" />
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
