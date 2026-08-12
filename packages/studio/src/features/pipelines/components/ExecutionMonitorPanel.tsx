import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../../api/client';
import { usePipelineBuilderStore } from '../../../stores/pipelineBuilderStore';
import { X, PlayCircle, CheckCircle, XCircle, Clock, Activity, FileText } from 'lucide-react';
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
      const status = data?.state?.state?.[data?.state?.state.length - 1]?.status;
      if (status === 'QUEUED' || status === 'RUNNING') return 2000;
      return false;
    }
  });

  const getStatusInfo = (status: string) => {
    switch (status) {
      case 'COMPLETED':
      case 'SUCCESS':
        return { icon: <CheckCircle className="w-5 h-5 text-emerald-500" />, color: 'text-emerald-500', bg: 'bg-emerald-500/10' };
      case 'FAILED':
        return { icon: <XCircle className="w-5 h-5 text-destructive" />, color: 'text-destructive', bg: 'bg-destructive/10' };
      case 'RUNNING':
        return { icon: <Activity className="w-5 h-5 text-primary animate-pulse" />, color: 'text-primary', bg: 'bg-primary/10' };
      case 'QUEUED':
      default:
        return { icon: <Clock className="w-5 h-5 text-muted-foreground" />, color: 'text-muted-foreground', bg: 'bg-muted' };
    }
  };

  const currentStatus = runDetails?.state?.state?.[runDetails?.state?.state.length - 1]?.status || 'QUEUED';
  const statusInfo = getStatusInfo(currentStatus);

  return (
    <AnimatePresence>
      {isExecutionMonitorOpen && (
        <motion.div
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="fixed top-14 right-0 w-[450px] bottom-0 bg-card/95 backdrop-blur-xl border-l border-border shadow-2xl z-40 flex flex-col"
        >
          <div className="flex items-center justify-between p-4 border-b border-border/50">
            <div className="flex items-center gap-2">
              <PlayCircle className="w-5 h-5 text-muted-foreground" />
              <h2 className="text-sm font-semibold">Execution Monitor</h2>
            </div>
            <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full" onClick={() => setExecutionMonitorOpen(false)}>
              <X className="w-4 h-4" />
            </Button>
          </div>

          <div className="p-6 border-b border-border/50 flex flex-col items-center justify-center gap-4">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center ${statusInfo.bg}`}>
              {React.cloneElement(statusInfo.icon as React.ReactElement<any>, { className: "w-8 h-8" })}
            </div>
            <div className="text-center">
              <h3 className={`text-xl font-bold capitalize ${statusInfo.color}`}>{currentStatus.toLowerCase()}</h3>
              <p className="text-xs text-muted-foreground font-mono mt-1">Run ID: {activeRunId}</p>
            </div>
          </div>

          <ScrollArea className="flex-1 p-6">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-4 flex items-center gap-2">
              <FileText className="w-4 h-4" /> Runtime Logs
            </h4>
            
            {!runDetails ? (
              <div className="flex flex-col gap-3 animate-pulse">
                <div className="h-4 bg-white/5 rounded w-3/4"></div>
                <div className="h-4 bg-white/5 rounded w-full"></div>
                <div className="h-4 bg-white/5 rounded w-5/6"></div>
              </div>
            ) : (
              <div className="space-y-4 font-mono text-[11px]">
                {runDetails.state?.state?.map((s: any, idx: number) => (
                  <div key={idx} className="flex flex-col gap-1 border-l-2 border-border pl-3 pb-4">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-foreground">{s.status}</span>
                      <span className="text-muted-foreground">{new Date(s.timestamp).toLocaleTimeString()}</span>
                    </div>
                    {s.message && <p className="text-muted-foreground mt-1">{s.message}</p>}
                    {s.node_id && (
                      <div className="mt-2 bg-black/40 rounded p-2 text-primary border border-primary/20">
                        Node: {s.node_id}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
