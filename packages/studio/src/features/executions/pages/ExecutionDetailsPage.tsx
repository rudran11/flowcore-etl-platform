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
import { ExecutionTimeline } from '../components/ExecutionTimeline';
import { ArrowLeft, Clock, Download, XCircle, RotateCcw, AlertCircle, Activity, Server, Hash, Play } from 'lucide-react';
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
  


  const calculatedDuration = run?.duration_ms || (run?.finished_at && run?.submitted_at ? new Date(run.finished_at).getTime() - new Date(run.submitted_at).getTime() : 0);
  const displayStartedAt = run?.started_at || run?.submitted_at;
  
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

      <div className="flex flex-col lg:flex-row gap-6 h-[calc(100vh-140px)]">
        {/* Main Content Area */}
        <div className="flex-1 overflow-hidden flex flex-col min-w-0">
          {run.error && (
            <div className="bg-destructive/10 border-l-4 border-destructive p-4 rounded-r-lg mb-4 shrink-0">
              <p className="text-destructive font-semibold">Execution Error</p>
              <p className="text-sm mt-1 font-mono text-destructive/80">{run.error}</p>
            </div>
          )}

          <Card className="shadow-sm flex-1 flex flex-col overflow-hidden border-border/50">
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
              Started {displayStartedAt ? formatDistanceToNow(new Date(displayStartedAt), { addSuffix: true }) : 'N/A'}
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto">
            <TabsContent value="dag" className="m-0 border-0 p-0">
              <ExecutionDAG run={run} />
            </TabsContent>
            
            <TabsContent value="timeline" className="m-0 p-0 border-0">
              <ExecutionTimeline run={run} />
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

        {/* Sidebar */}
        <div className="w-full lg:w-80 shrink-0 flex flex-col gap-4 overflow-y-auto custom-scrollbar pr-1">
          <Card className="border-border/50 shadow-sm overflow-hidden">
            <div className="bg-muted/50 p-4 border-b border-border/50">
              <h3 className="font-semibold text-sm flex items-center gap-2">
                <Activity className="w-4 h-4 text-primary" /> Execution Details
              </h3>
            </div>
            <CardContent className="p-0">
              <div className="divide-y divide-border/50">
                <div className="p-4 flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Pipeline Version</span>
                  <span className="text-sm font-medium">v{run.pipeline_version}</span>
                </div>
                <div className="p-4 flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Trigger Type</span>
                  <span className="text-sm font-medium flex items-center gap-1"><Play className="w-3 h-3"/> Manual</span>
                </div>
                <div className="p-4 flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Environment</span>
                  <span className="text-sm font-medium flex items-center gap-1"><Server className="w-3 h-3"/> Production</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/50 shadow-sm overflow-hidden">
            <div className="bg-muted/50 p-4 border-b border-border/50">
              <h3 className="font-semibold text-sm flex items-center gap-2">
                <Clock className="w-4 h-4 text-blue-500" /> Timing & Performance
              </h3>
            </div>
            <CardContent className="p-0">
              <div className="divide-y divide-border/50">
                <div className="p-4 flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Queue Wait Time</span>
                  <span className="text-sm font-medium">
                    {run.started_at && run.submitted_at 
                      ? `${Math.max(0, (new Date(run.started_at).getTime() - new Date(run.submitted_at).getTime()) / 1000).toFixed(1)}s` 
                      : '0s'}
                  </span>
                </div>
                <div className="p-4 flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Total Duration</span>
                  <span className="text-sm font-medium">{calculatedDuration ? `${(calculatedDuration / 1000).toFixed(1)}s` : 'Running'}</span>
                </div>
                <div className="p-4 flex flex-col gap-1">
                  <span className="text-xs text-muted-foreground">Started At</span>
                  <span className="text-sm font-medium">{displayStartedAt ? format(new Date(displayStartedAt), 'MMM d, yyyy HH:mm:ss') : 'N/A'}</span>
                </div>
                <div className="p-4 flex flex-col gap-1">
                  <span className="text-xs text-muted-foreground">Ended At</span>
                  <span className="text-sm font-medium">{run.finished_at ? format(new Date(run.finished_at), 'MMM d, yyyy HH:mm:ss') : 'N/A'}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/50 shadow-sm overflow-hidden">
            <div className="bg-muted/50 p-4 border-b border-border/50">
              <h3 className="font-semibold text-sm flex items-center gap-2">
                <Hash className="w-4 h-4 text-amber-500" /> Metrics
              </h3>
            </div>
            <CardContent className="p-4 space-y-4">
              <div>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-xs text-muted-foreground">Steps Completed</span>
                  <span className="text-xs font-bold">{completedSteps}/{totalSteps}</span>
                </div>
                <Progress value={progressValue} className="h-1.5 w-full bg-muted" />
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-muted-foreground flex items-center gap-1"><AlertCircle className="w-3 h-3 text-destructive"/> Failed Steps</span>
                <span className="text-sm font-medium text-destructive">{failedSteps}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-muted-foreground flex items-center gap-1"><RotateCcw className="w-3 h-3 text-amber-500"/> Total Retries</span>
                <span className="text-sm font-medium">{totalRetries}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
