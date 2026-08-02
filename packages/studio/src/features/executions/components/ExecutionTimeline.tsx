import React, { useMemo } from 'react';
import { ExecutionResponse } from '../../../api/executions';
import { format, compareAsc } from 'date-fns';
import { CheckCircle2, AlertCircle, Play, RotateCcw, Box, ArrowRight } from 'lucide-react';

interface ExecutionTimelineProps {
  run: ExecutionResponse;
}

type TimelineEvent = {
  id: string;
  time: Date;
  title: string;
  description: string;
  status: string;
  type: 'pipeline' | 'step';
  icon: React.ReactNode;
  color: string;
};

export const ExecutionTimeline: React.FC<ExecutionTimelineProps> = ({ run }) => {
  const events = useMemo(() => {
    const list: TimelineEvent[] = [];

    // Pipeline Submitted
    if (run.submitted_at) {
      list.push({
        id: 'pipeline-submitted',
        time: new Date(run.submitted_at),
        title: 'Execution Submitted',
        description: `Triggered manually, version ${run.pipeline_version}`,
        status: 'PENDING',
        type: 'pipeline',
        icon: <ArrowRight className="w-4 h-4 text-white" />,
        color: 'bg-primary'
      });
    }

    // Pipeline Started
    if (run.started_at) {
      list.push({
        id: 'pipeline-started',
        time: new Date(run.started_at),
        title: 'Execution Started',
        description: 'Pipeline execution began processing',
        status: 'RUNNING',
        type: 'pipeline',
        icon: <Play className="w-4 h-4 text-white ml-0.5" />,
        color: 'bg-blue-500'
      });
    }

    // Steps
    if (run.steps) {
      Object.entries(run.steps).forEach(([stepId, step]) => {
        if (step.start_time) {
          list.push({
            id: `step-${stepId}-started`,
            time: new Date(step.start_time),
            title: `Step Started: ${stepId}`,
            description: `Retries so far: ${step.retry_count || 0}`,
            status: 'RUNNING',
            type: 'step',
            icon: <Box className="w-3.5 h-3.5 text-blue-500" />,
            color: 'bg-blue-500/20 border border-blue-500/50'
          });
        }
        if (step.end_time) {
          const isError = step.status === 'FAILED';
          list.push({
            id: `step-${stepId}-ended`,
            time: new Date(step.end_time),
            title: `Step ${step.status}: ${stepId}`,
            description: step.duration_ms ? `Duration: ${(step.duration_ms / 1000).toFixed(2)}s` : '',
            status: step.status,
            type: 'step',
            icon: isError ? <AlertCircle className="w-3.5 h-3.5 text-destructive" /> : <CheckCircle2 className="w-3.5 h-3.5 text-green-500" />,
            color: isError ? 'bg-destructive/20 border border-destructive/50' : 'bg-green-500/20 border border-green-500/50'
          });
        }
        
        // Hypothetically if we wanted to show retries chronologically, we'd need history.
        // For now we just show total retries in the description.
      });
    }

    // Pipeline Finished
    if (run.finished_at) {
      const isError = run.status === 'FAILED';
      const calculatedDuration = run.duration_ms || (run.finished_at && run.submitted_at ? new Date(run.finished_at).getTime() - new Date(run.submitted_at).getTime() : 0);
      list.push({
        id: 'pipeline-finished',
        time: new Date(run.finished_at),
        title: `Execution ${run.status}`,
        description: `Total duration: ${calculatedDuration ? (calculatedDuration / 1000).toFixed(2) + 's' : 'N/A'}`,
        status: run.status,
        type: 'pipeline',
        icon: isError ? <AlertCircle className="w-4 h-4 text-white" /> : <CheckCircle2 className="w-4 h-4 text-white" />,
        color: isError ? 'bg-destructive' : 'bg-green-500'
      });
    }

    // Sort chronologically
    return list.sort((a, b) => compareAsc(a.time, b.time));
  }, [run]);

  if (events.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-48 text-muted-foreground">
        <RotateCcw className="w-8 h-8 opacity-20 mb-2" />
        <p>No timeline events available</p>
      </div>
    );
  }

  return (
    <div className="p-6 relative">
      <div className="absolute left-10 top-8 bottom-8 w-0.5 bg-border/60" />
      
      <div className="space-y-8 relative z-10">
        {events.map((event) => (
          <div key={event.id} className="flex gap-6 group">
            <div className="flex flex-col items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center z-10 transition-transform group-hover:scale-110 shadow-sm ${event.color} ${event.type === 'step' ? 'w-6 h-6 ml-1' : ''}`}>
                {event.icon}
              </div>
            </div>
            
            <div className={`flex-1 pt-1 ${event.type === 'step' ? 'mt-0' : ''}`}>
              <div className="flex items-center gap-2 mb-1">
                <span className={`font-semibold ${event.type === 'pipeline' ? 'text-base' : 'text-sm text-foreground/90'}`}>
                  {event.title}
                </span>
                <span className="text-xs font-mono text-muted-foreground ml-auto bg-muted/50 px-2 py-0.5 rounded border border-border/50">
                  {format(event.time, 'HH:mm:ss.SSS')}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">
                {event.description}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
