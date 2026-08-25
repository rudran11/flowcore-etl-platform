import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../../api/client';
import { usePipelineBuilderStore } from '../../../stores/pipelineBuilderStore';
import { X, CheckCircle, XCircle, Clock, Activity, FileText } from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { motion, AnimatePresence } from 'framer-motion';
import { ScrollArea } from '../../../components/ui/scroll-area';

export const ExecutionMonitorPanel: React.FC = () => {
  const { activeRunId, isExecutionMonitorOpen, setExecutionMonitorOpen } = usePipelineBuilderStore();

  const { data: runDetails } = useQuery({
    queryKey: ['run', activeRunId],
    queryFn: async () => {
      const resp = await apiClient.get(`/runs/${activeRunId}`);
      return resp.data;
    },
    enabled: !!activeRunId && isExecutionMonitorOpen,
    refetchInterval: (data: any) => {
      // Poll every 2 seconds if running or queued
      const status = data?.status;
      if (status === 'QUEUED' || status === 'RUNNING' || status === 'PENDING') return 2000;
      return false;
    }
  });

  const getStatusInfo = (status: string) => {
    switch (status) {
      case 'COMPLETED':
      case 'SUCCESS':
        return { icon: <CheckCircle className="w-5 h-5 text-emerald-500" />, color: 'text-emerald-500', bg: 'bg-emerald-500/10' };
      case 'FAILED':
        return { icon: <XCircle className="w-5 h-5 text-status-error" />, color: 'text-status-error', bg: 'bg-status-error/10' };
      case 'RUNNING':
        return { icon: <Activity className="w-5 h-5 text-status-running animate-pulse" />, color: 'text-status-running', bg: 'bg-status-running/10 border border-status-running/20 shadow-[0_0_15px_rgba(var(--status-running),0.2)]' };
      case 'QUEUED':
      case 'PENDING':
      default:
        return { icon: <Clock className="w-5 h-5 text-muted-foreground" />, color: 'text-muted-foreground', bg: 'bg-accent/50' };
    }
  };

  const currentStatus = runDetails?.status || 'QUEUED';
  const statusInfo = getStatusInfo(currentStatus);

  return (
    <AnimatePresence>
      {isExecutionMonitorOpen && (
        <motion.div
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="fixed top-[52px] right-0 w-[450px] bottom-0 bg-card/95 backdrop-blur-xl border-l border-border shadow-surface-elevated z-40 flex flex-col"
        >
          <div className="flex items-center justify-between p-4 border-b border-border">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-primary" />
              <h2 className="text-sm font-semibold tracking-tight uppercase">Execution Trace</h2>
            </div>
            <Button variant="ghost" size="icon" className="h-7 w-7 rounded-md hover:bg-accent" onClick={() => setExecutionMonitorOpen(false)}>
              <X className="w-4 h-4" />
            </Button>
          </div>

          <div className="p-6 border-b border-border flex flex-col items-center justify-center gap-4 bg-accent/20 relative overflow-hidden">
            <div className="absolute inset-0 bg-dot-topology opacity-50 pointer-events-none" />
            <div className={`w-14 h-14 rounded-xl flex items-center justify-center relative z-10 ${statusInfo.bg}`}>
              {React.cloneElement(statusInfo.icon as React.ReactElement<any>, { className: "w-6 h-6" })}
            </div>
            <div className="text-center relative z-10">
              <h3 className={`text-xl font-bold tracking-tight uppercase ${statusInfo.color}`}>{currentStatus}</h3>
              <p className="text-[11px] text-muted-foreground font-mono mt-1 px-2 py-0.5 bg-background border border-border rounded shadow-sm">ID: {activeRunId}</p>
            </div>
          </div>

          <ScrollArea className="flex-1 p-6">
            {!runDetails ? (
              <div className="flex flex-col gap-3 animate-pulse opacity-50">
                <div className="h-3 bg-accent rounded w-3/4"></div>
                <div className="h-3 bg-accent rounded w-full"></div>
                <div className="h-3 bg-accent rounded w-5/6"></div>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Timeline Gantt Chart */}
                {(() => {
                  const steps = Object.values(runDetails.steps || {}) as any[];
                  if (steps.length === 0) return null;
                  
                  const runStart = runDetails.start_time ? new Date(runDetails.start_time).getTime() : Date.now();
                  const runEnd = runDetails.end_time ? new Date(runDetails.end_time).getTime() : Date.now();
                  const totalDurationMs = Math.max(runEnd - runStart, 100); // Prevent div by 0

                  return (
                    <div className="mb-8">
                      <h4 className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-4 flex items-center gap-2">
                        <Activity className="w-3.5 h-3.5" /> Execution Timeline
                      </h4>
                      <div className="flex flex-col gap-2">
                        {steps.map((s, idx) => {
                          const sStart = s.start_time ? new Date(s.start_time).getTime() : Date.now();
                          const sEnd = s.end_time ? new Date(s.end_time).getTime() : (s.start_time ? Date.now() : Date.now());
                          
                          // Handle queued/pending steps
                          if (!s.start_time) return null;

                          let leftPercent = ((sStart - runStart) / totalDurationMs) * 100;
                          let widthPercent = ((sEnd - sStart) / totalDurationMs) * 100;
                          
                          // Clamp values
                          leftPercent = Math.max(0, Math.min(100, leftPercent));
                          widthPercent = Math.max(2, Math.min(100 - leftPercent, widthPercent));

                          const colorClass = s.status === 'COMPLETED' ? 'bg-emerald-500' :
                                             s.status === 'FAILED' ? 'bg-status-error' :
                                             'bg-status-running animate-pulse';

                          return (
                            <div key={idx} className="relative h-6 flex items-center group">
                              <div className="w-24 text-[10px] text-muted-foreground truncate pr-2 shrink-0" title={s.step_id}>
                                {s.step_id}
                              </div>
                              <div className="flex-1 h-3 bg-accent/30 rounded-full relative overflow-hidden">
                                <div 
                                  className={`absolute h-full rounded-full ${colorClass}`}
                                  style={{ left: `${leftPercent}%`, width: `${widthPercent}%` }}
                                />
                              </div>
                              <div className="w-12 text-[10px] text-muted-foreground pl-2 shrink-0 text-right">
                                {((sEnd - sStart) / 1000).toFixed(1)}s
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })()}

                <div>
                  <h4 className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-4 flex items-center gap-2">
                    <FileText className="w-3.5 h-3.5" /> Runtime Telemetry
                  </h4>
                  <div className="space-y-0 font-mono text-[11px]">
                    {Object.values(runDetails.steps || {}).map((s: any, idx: number) => (
                      <div key={idx} className="flex flex-col gap-1 border-l border-border pl-4 pb-5 relative before:absolute before:left-[-4px] before:top-1.5 before:w-2 before:h-2 before:bg-background before:border before:border-primary before:rounded-full">
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-foreground">Step: {s.step_id} - {s.status}</span>
                          {s.end_time && (
                            <span className="text-muted-foreground">{new Date(s.end_time).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
                          )}
                        </div>
                        {s.error_message && <p className="text-status-error mt-0.5 whitespace-pre-wrap">{s.error_message}</p>}
                        
                        {s.outputs?.metrics && Object.keys(s.outputs.metrics).length > 0 && (
                          <div className="mt-2 bg-accent/40 rounded p-2 text-primary border border-border shadow-sm flex flex-col gap-1">
                            <div className="flex items-center gap-2 mb-1">
                              <Activity className="w-3 h-3" />
                              <span className="font-semibold">Metrics</span>
                            </div>
                            {Object.entries(s.outputs.metrics).map(([k, v]) => (
                              <div key={k} className="flex justify-between">
                                <span className="text-muted-foreground">{k}</span>
                                <span>{String(v)}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </ScrollArea>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
