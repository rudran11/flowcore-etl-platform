import React from 'react';
import { motion } from 'framer-motion';
import { useDashboard } from './hooks/useDashboard';
import { useSchedules } from '../schedules/hooks/useSchedules';
import { DashboardCard } from './components/DashboardCard';
import { DashboardGrid } from './components/DashboardGrid';
import { ExecutionTrendChart } from './components/ExecutionTrendChart';
import { ExecutionTable } from '../executions/components/ExecutionTable';
import { Activity, Clock, PlayCircle, ServerCog, AlertOctagon } from 'lucide-react';
import { Skeleton } from '../../components/ui/skeleton';
import { toast } from 'sonner';
import { useSchedulerMetrics } from './hooks/useSchedulerMetrics';

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
  const { data, isLoading, error } = useDashboard();
  const { data: schedules } = useSchedules();
  const { data: metrics } = useSchedulerMetrics();

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
      className="space-y-4"
    >
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
        <div className="flex items-center space-x-2">
          {data.health.server === 'healthy' ? (
            <div className="flex items-center text-sm font-medium text-emerald-500">
              <span className="relative flex h-2 w-2 mr-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              System Online
            </div>
          ) : (
            <div className="flex items-center text-sm font-medium text-destructive">
              <span className="relative flex h-2 w-2 mr-2 rounded-full bg-destructive"></span>
              System Offline
            </div>
          )}
        </div>
      </div>
      
      <DashboardGrid>
        <motion.div variants={item}>
          <DashboardCard 
            title="Total Pipelines" 
            value={data.statistics.total_pipelines} 
            icon={<Activity className="h-4 w-4" />}
            description="Registered in the system"
          />
        </motion.div>
        <motion.div variants={item}>
          <DashboardCard 
            title="Total Executions" 
            value={data.statistics.total_runs} 
            icon={<PlayCircle className="h-4 w-4" />}
            description="Lifetime pipeline runs"
          />
        </motion.div>
        <motion.div variants={item}>
          <DashboardCard 
            title="Active Schedules" 
            value={schedules?.filter((s: any) => s.status === 'ACTIVE').length || 0} 
            icon={<Clock className="h-4 w-4 text-blue-500" />}
            description="Currently running schedules"
          />
        </motion.div>
        <motion.div variants={item}>
          <DashboardCard 
            title="Total Schedules" 
            value={schedules?.length || 0} 
            icon={<Clock className="h-4 w-4" />}
            description="Configured in the system"
          />
        </motion.div>
      </DashboardGrid>

      <h3 className="text-xl font-bold tracking-tight mt-6">Scheduler Health</h3>
      <DashboardGrid>
        <motion.div variants={item}>
          <DashboardCard 
            title="Queue Length" 
            value={metrics?.queue_length ?? 0} 
            icon={<ServerCog className="h-4 w-4 text-emerald-500" />}
            description="Jobs waiting to execute"
          />
        </motion.div>
        <motion.div variants={item}>
          <DashboardCard 
            title="Avg Delay" 
            value={`${metrics?.avg_execution_delay_seconds ?? 0}s`} 
            icon={<Clock className="h-4 w-4 text-amber-500" />}
            description="Average start delay"
          />
        </motion.div>
        <motion.div variants={item}>
          <DashboardCard 
            title="Success Rate" 
            value={`${((metrics?.success_rate ?? 1) * 100).toFixed(1)}%`} 
            icon={<Activity className="h-4 w-4 text-emerald-500" />}
            description="Schedule execution success"
          />
        </motion.div>
        <motion.div variants={item}>
          <DashboardCard 
            title="Missed Runs" 
            value={metrics?.missed_schedules ?? 0} 
            icon={<AlertOctagon className="h-4 w-4 text-destructive" />}
            description="Missed schedules in last 24h"
          />
        </motion.div>
      </DashboardGrid>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <motion.div variants={item} className="lg:col-span-4">
          <ExecutionTrendChart data={data.trends} />
        </motion.div>
        <motion.div variants={item} className="lg:col-span-3">
          <ExecutionTable runs={data.recent_runs} />
        </motion.div>
      </div>
    </motion.div>
  );
};
