import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../../api/client';
import { usePipelineBuilderStore } from '../../../stores/pipelineBuilderStore';
import { History, X, CheckCircle, XCircle, Clock, Activity } from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { motion, AnimatePresence } from 'framer-motion';
import { ScrollArea } from '../../../components/ui/scroll-area';

interface ExecutionHistoryDrawerProps {
  pipelineId: string;
  isOpen: boolean;
  onClose: () => void;
}

export const ExecutionHistoryDrawer: React.FC<ExecutionHistoryDrawerProps> = ({ pipelineId, isOpen, onClose }) => {
  const { setExecutionMonitorOpen } = usePipelineBuilderStore();

  const { data, isLoading } = useQuery({
    queryKey: ['runs', pipelineId],
    queryFn: async () => {
      const resp = await apiClient.get(`/runs?pipeline_id=${pipelineId}&limit=50`);
      return resp.data;
    },
    enabled: isOpen,
    refetchInterval: isOpen ? 5000 : false
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLETED':
      case 'SUCCESS':
        return <CheckCircle className="w-4 h-4 text-emerald-500" />;
      case 'FAILED':
        return <XCircle className="w-4 h-4 text-destructive" />;
      case 'RUNNING':
        return <Activity className="w-4 h-4 text-primary animate-pulse" />;
      case 'QUEUED':
      default:
        return <Clock className="w-4 h-4 text-muted-foreground" />;
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ x: '-100%' }}
          animate={{ x: 0 }}
          exit={{ x: '-100%' }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="fixed top-14 left-0 w-[400px] bottom-0 bg-card/95 backdrop-blur-xl border-r border-border shadow-2xl z-40 flex flex-col"
        >
          <div className="flex items-center justify-between p-4 border-b border-border/50">
            <div className="flex items-center gap-2">
              <History className="w-5 h-5 text-muted-foreground" />
              <h2 className="text-sm font-semibold">Execution History</h2>
            </div>
            <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>

          <ScrollArea className="flex-1">
            {isLoading ? (
              <div className="p-4 space-y-4">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="animate-pulse flex items-center gap-3">
                    <div className="w-8 h-8 bg-white/5 rounded-full" />
                    <div className="flex-1 space-y-2">
                      <div className="h-3 bg-white/5 rounded w-1/2" />
                      <div className="h-3 bg-white/5 rounded w-1/3" />
                    </div>
                  </div>
                ))}
              </div>
            ) : data?.items?.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground">
                <Clock className="w-8 h-8 mx-auto mb-3 opacity-20" />
                <p>No execution runs found.</p>
              </div>
            ) : (
              <div className="divide-y divide-border/30">
                {data?.items?.map((run: any) => (
                  <div 
                    key={run.id}
                    onClick={() => {
                      setExecutionMonitorOpen(true, run.id);
                      onClose();
                    }}
                    className="p-4 flex items-center gap-4 hover:bg-white/5 cursor-pointer transition-colors"
                  >
                    <div className="flex-shrink-0">
                      {getStatusIcon(run.status)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-foreground truncate">{run.pipeline_version}</p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {new Date(run.created_at).toLocaleString()}
                      </p>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <p className={`text-xs font-semibold capitalize ${run.status === 'FAILED' ? 'text-destructive' : run.status === 'COMPLETED' ? 'text-emerald-500' : run.status === 'RUNNING' ? 'text-primary' : 'text-muted-foreground'}`}>
                        {run.status.toLowerCase()}
                      </p>
                    </div>
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
