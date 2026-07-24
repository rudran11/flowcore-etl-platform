import React, { useState } from 'react';
import { useExecutions } from '../hooks/useExecutions';
import { ExecutionTable } from '../components/ExecutionTable';
import { Card, CardContent } from '../../../components/ui/card';
import { Input } from '../../../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../components/ui/select';
import { Button } from '../../../components/ui/button';
import { RefreshCcw, Activity, CheckCircle2, XCircle } from 'lucide-react';
import { motion } from 'framer-motion';

export const ExecutionsPage: React.FC = () => {
  const [pipelineId, setPipelineId] = useState('');
  const [status, setStatus] = useState('ALL');
  
  const { data, isLoading, refetch, isRefetching } = useExecutions(25, 0, pipelineId || undefined, status);
  
  const runs = data?.items || [];
  
  // Calculate some simple metrics from the current page of runs for the mini summary cards
  const totalRuns = data?.total || 0;
  const completedRuns = runs.filter(r => r.status === 'COMPLETED').length;
  const failedRuns = runs.filter(r => r.status === 'FAILED').length;
  const successRate = runs.length > 0 ? Math.round((completedRuns / runs.length) * 100) : 0;

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Executions</h1>
          <p className="text-muted-foreground mt-1">
            Monitor and manage all pipeline runs across the platform.
          </p>
        </div>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={() => refetch()}
          className="gap-2"
        >
          <RefreshCcw className={`h-4 w-4 ${isRefetching ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card>
            <CardContent className="p-6 flex flex-row items-center gap-4">
              <div className="p-3 bg-blue-500/10 rounded-xl">
                <Activity className="h-6 w-6 text-blue-500" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Runs</p>
                <h3 className="text-2xl font-bold">{totalRuns}</h3>
              </div>
            </CardContent>
          </Card>
        </motion.div>
        
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card>
            <CardContent className="p-6 flex flex-row items-center gap-4">
              <div className="p-3 bg-green-500/10 rounded-xl">
                <CheckCircle2 className="h-6 w-6 text-green-500" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Success Rate (Recent)</p>
                <h3 className="text-2xl font-bold">{successRate}%</h3>
              </div>
            </CardContent>
          </Card>
        </motion.div>
        
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Card>
            <CardContent className="p-6 flex flex-row items-center gap-4">
              <div className="p-3 bg-destructive/10 rounded-xl">
                <XCircle className="h-6 w-6 text-destructive" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Failed Runs (Recent)</p>
                <h3 className="text-2xl font-bold">{failedRuns}</h3>
              </div>
            </CardContent>
          </Card>
        </motion.div>
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
        <ExecutionTable 
          runs={runs} 
          loading={isLoading && !isRefetching} 
          title=""
          description=""
        />
      </div>
    </div>
  );
};
