import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useExecution, useCancelExecution } from '../hooks/useExecution';
import { Button } from '../../../components/ui/button';
import { Card, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { PipelineStatusBadge } from '../../pipelines/components/PipelineStatusBadge';
import { ExecutionDAG } from '../components/ExecutionDAG';
import { ExecutionLogs } from '../components/ExecutionLogs';
import { ArrowLeft, Clock, Zap, Download, XCircle, RotateCcw, AlertCircle } from 'lucide-react';
import { formatDistanceToNow, format } from 'date-fns';
import { Progress } from '../../../components/ui/progress';

export const ExecutionDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: run, isLoading } = useExecution(id || '');
  const cancelExecution = useCancelExecution();
  
  const [activeTab, setActiveTab] = useState('dag');

  if (isLoading) {
    return <div className="flex h-[50vh] items-center justify-center text-muted-foreground animate-pulse">Loading execution details...</div>;
  }

  if (!run) {
    return <div className="flex h-[50vh] items-center justify-center text-destructive">Execution run not found.</div>;
  }

  const isTerminal = ['COMPLETED', 'FAILED', 'CANCELLED'].includes(run.status);
  
  const handleCancel = () => {
    if (id) cancelExecution.mutate(id);
  };
  
  const handleDownload = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(run, null, 2));
    const a = document.createElement('a');
    a.setAttribute("href", dataStr);
    a.setAttribute("download", `execution-${run.run_id}.json`);
    document.body.appendChild(a);
    a.click();
    a.remove();
  };

  const steps = Object.values(run.steps || {});
  const totalSteps = steps.length;
  const completedSteps = steps.filter(s => s.status === 'COMPLETED').length;
  const failedSteps = steps.filter(s => s.status === 'FAILED').length;
  const totalRetries = steps.reduce((sum, s) => sum + (s.retry_count || 0), 0);
  
  const progressValue = isTerminal ? 100 : (totalSteps === 0 ? 0 : Math.round((completedSteps / totalSteps) * 100));

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/runs')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold tracking-tight">{run.pipeline_id}</h1>
              <PipelineStatusBadge status={run.status} />
              <Badge variant="outline">v{run.pipeline_version}</Badge>
            </div>
            <p className="text-muted-foreground font-mono text-xs mt-1">
              Run ID: {run.run_id}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleDownload} className="gap-2">
            <Download className="h-4 w-4" /> Export Metadata
          </Button>
          
          {!isTerminal && (
            <Button variant="destructive" size="sm" onClick={handleCancel} disabled={cancelExecution.isPending} className="gap-2">
              <XCircle className="h-4 w-4" /> Cancel
            </Button>
          )}
          {run.status === 'FAILED' && (
            <Button variant="default" size="sm" className="gap-2">
              <RotateCcw className="h-4 w-4" /> Retry Failed
            </Button>
          )}
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-4 flex flex-row items-center gap-4">
            <div className="p-2 bg-blue-500/10 rounded-lg">
              <Clock className="h-5 w-5 text-blue-500" />
            </div>
            <div>
              <p className="text-xs font-medium text-muted-foreground">Duration</p>
              <h3 className="text-lg font-bold">
                {run.duration_ms ? `${(run.duration_ms / 1000).toFixed(1)}s` : 'In Progress'}
              </h3>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex flex-row items-center gap-4">
            <div className="p-2 bg-green-500/10 rounded-lg">
              <Zap className="h-5 w-5 text-green-500" />
            </div>
            <div className="w-full">
              <div className="flex justify-between items-center mb-1">
                <p className="text-xs font-medium text-muted-foreground">Steps Completed</p>
                <span className="text-xs font-bold">{completedSteps}/{totalSteps}</span>
              </div>
              <Progress value={progressValue} className="h-1.5 w-full" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex flex-row items-center gap-4">
            <div className="p-2 bg-destructive/10 rounded-lg">
              <AlertCircle className="h-5 w-5 text-destructive" />
            </div>
            <div>
              <p className="text-xs font-medium text-muted-foreground">Failed Steps</p>
              <h3 className="text-lg font-bold">{failedSteps}</h3>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex flex-row items-center gap-4">
            <div className="p-2 bg-amber-500/10 rounded-lg">
              <RotateCcw className="h-5 w-5 text-amber-500" />
            </div>
            <div>
              <p className="text-xs font-medium text-muted-foreground">Total Retries</p>
              <h3 className="text-lg font-bold">{totalRetries}</h3>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {run.error && (
        <div className="bg-destructive/10 border-l-4 border-destructive p-4 rounded-r-lg">
          <p className="text-destructive font-semibold">Execution Error</p>
          <p className="text-sm mt-1 font-mono text-destructive/80">{run.error}</p>
        </div>
      )}

      <Card className="shadow-sm">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <div className="flex items-center justify-between border-b px-4">
            <TabsList className="h-12 bg-transparent border-none p-0 space-x-6">
              <TabsTrigger 
                value="dag" 
                className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-0 h-12 font-medium"
              >
                Live DAG
              </TabsTrigger>
              <TabsTrigger 
                value="timeline" 
                className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-0 h-12 font-medium"
              >
                Timeline
              </TabsTrigger>
              <TabsTrigger 
                value="logs" 
                className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-0 h-12 font-medium"
              >
                Logs
              </TabsTrigger>
              <TabsTrigger 
                value="outputs" 
                className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-0 h-12 font-medium"
              >
                Outputs
              </TabsTrigger>
            </TabsList>
            <div className="text-xs text-muted-foreground">
              Started {run.started_at ? formatDistanceToNow(new Date(run.started_at), { addSuffix: true }) : 'N/A'}
            </div>
          </div>
          
          <div className="p-0">
            <TabsContent value="dag" className="m-0 border-0 p-0">
              <ExecutionDAG run={run} />
            </TabsContent>
            
            <TabsContent value="timeline" className="m-0 p-6">
              <div className="space-y-6">
                <div className="flex gap-4">
                  <div className="flex flex-col items-center">
                    <div className="w-3 h-3 rounded-full bg-primary" />
                    <div className="w-0.5 h-full bg-border mt-2" />
                  </div>
                  <div>
                    <p className="font-semibold text-sm">Execution Submitted</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {format(new Date(run.submitted_at), 'MMM d, yyyy HH:mm:ss')}
                    </p>
                  </div>
                </div>
                {run.started_at && (
                  <div className="flex gap-4">
                    <div className="flex flex-col items-center">
                      <div className="w-3 h-3 rounded-full bg-blue-500" />
                      <div className="w-0.5 h-full bg-border mt-2" />
                    </div>
                    <div>
                      <p className="font-semibold text-sm">Execution Started</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {format(new Date(run.started_at), 'MMM d, yyyy HH:mm:ss')}
                      </p>
                    </div>
                  </div>
                )}
                {run.finished_at && (
                  <div className="flex gap-4">
                    <div className="flex flex-col items-center">
                      <div className={`w-3 h-3 rounded-full ${run.status === 'COMPLETED' ? 'bg-green-500' : 'bg-destructive'}`} />
                    </div>
                    <div>
                      <p className="font-semibold text-sm">Execution {run.status}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {format(new Date(run.finished_at), 'MMM d, yyyy HH:mm:ss')}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </TabsContent>
            
            <TabsContent value="logs" className="m-0 p-0 border-0">
              <ExecutionLogs run={run} />
            </TabsContent>
            
            <TabsContent value="outputs" className="m-0 p-6">
              <div className="bg-muted p-4 rounded-lg overflow-x-auto">
                <pre className="text-sm font-mono text-muted-foreground">
                  {JSON.stringify(run.outputs, null, 2)}
                </pre>
              </div>
            </TabsContent>
          </div>
        </Tabs>
      </Card>
    </div>
  );
};
