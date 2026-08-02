import React, { useState } from 'react';
import { useExecutions } from '../hooks/useExecutions';
import { ExecutionTable } from '../components/ExecutionTable';
import { Input } from '../../../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../components/ui/select';
import { Button } from '../../../components/ui/button';
import { RefreshCcw, Activity, CheckCircle2, Clock, Zap } from 'lucide-react';
import { PageHeader } from '../../../components/ui/page-header';
import { StatCard } from '../../../components/ui/stat-card';
import { EmptyState } from '../../../components/ui/empty-state';

import { useExecutionMetrics } from '../hooks/useExecutionMetrics';
import { formatDistanceToNow } from 'date-fns';

export const ExecutionsPage: React.FC = () => {
  const [pipelineId, setPipelineId] = useState('');
  const [status, setStatus] = useState('ALL');
  
  const { data, isLoading, refetch, isRefetching } = useExecutions(25, 0, pipelineId || undefined, status);
  const { data: metrics, isLoading: isMetricsLoading } = useExecutionMetrics();
  
  const runs = data?.items || [];

  const formatDuration = (ms: number) => {
    if (!ms) return '0s';
    return `${(ms / 1000).toFixed(1)}s`;
  };

  return (
    <div className="p-6 md:p-8 max-w-[1400px] mx-auto space-y-8 animate-in fade-in duration-500 w-full">
      <PageHeader
        title="Executions"
        subtitle="Monitor and manage all pipeline runs across the platform."
        icon={Activity}
        actions={
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => refetch()}
            className="gap-2"
          >
            <RefreshCcw className={`h-4 w-4 ${isRefetching ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        }
      />

      <div className="grid gap-4 grid-cols-2 md:grid-cols-4 lg:grid-cols-5">
        <StatCard 
          title="Total Runs" 
          value={metrics?.total || 0} 
          icon={<Activity className="h-4 w-4" />}
          description="All recorded executions"
        />
        <StatCard 
          title="Running Now" 
          value={metrics?.running || 0} 
          icon={<RefreshCcw className="h-4 w-4" />}
          description="Active executions"
        />
        <StatCard 
          title="Queued" 
          value={metrics?.queued || 0} 
          icon={<Clock className="h-4 w-4" />}
          description="Waiting for resources"
        />
        <StatCard 
          title="Success Rate" 
          value={`${metrics?.successRate || 0}%`} 
          icon={<CheckCircle2 className="h-4 w-4" />}
          description={`Failure: ${metrics?.failureRate || 0}%`}
          trend={metrics?.successRate && metrics.successRate > 90 ? "up" : "down"}
          trendValue={metrics?.successRate && metrics.successRate > 90 ? "Healthy" : "Needs Attention"}
        />
        <StatCard 
          title="Avg Duration" 
          value={formatDuration(metrics?.avgDuration || 0)} 
          icon={<Zap className="h-4 w-4" />}
          description={`Longest: ${formatDuration(metrics?.longestDuration || 0)}`}
        />
      </div>

      <div className="flex gap-4 text-xs text-muted-foreground bg-accent/30 p-2 px-4 rounded-md border border-border/50">
        <div className="flex items-center gap-2">
          <span className="font-medium text-foreground">Last Success:</span>
          {metrics?.lastSuccess ? formatDistanceToNow(new Date(metrics.lastSuccess), { addSuffix: true }) : 'N/A'}
        </div>
        <div className="flex items-center gap-2 border-l border-border/50 pl-4">
          <span className="font-medium text-foreground">Last Failure:</span>
          {metrics?.lastFailure ? formatDistanceToNow(new Date(metrics.lastFailure), { addSuffix: true }) : 'N/A'}
        </div>
      </div>

      <div className="flex flex-col sm:flex-row items-center gap-4">
        <div className="w-full sm:w-64">
          <Input 
            placeholder="Filter by Pipeline ID..." 
            value={pipelineId}
            onChange={(e) => setPipelineId(e.target.value)}
          />
        </div>
        <div className="w-full sm:w-48">
          <Select value={status} onValueChange={setStatus}>
            <SelectTrigger>
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">All Statuses</SelectItem>
              <SelectItem value="PENDING">Pending</SelectItem>
              <SelectItem value="RUNNING">Running</SelectItem>
              <SelectItem value="COMPLETED">Completed</SelectItem>
              <SelectItem value="FAILED">Failed</SelectItem>
              <SelectItem value="CANCELLED">Cancelled</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="mt-4">
        {runs.length === 0 && !isLoading && !isRefetching ? (
          <EmptyState 
            icon={Activity}
            title="No executions found"
            description="We couldn't find any executions matching your filters."
          />
        ) : (
          <ExecutionTable 
            runs={runs} 
            loading={isLoading && !isRefetching} 
            title=""
            description=""
          />
        )}
      </div>
    </div>
  );
};
