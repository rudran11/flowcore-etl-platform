import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Puzzle, Clock, AlertTriangle, Zap } from 'lucide-react';
import { ExecutionResponse } from '../../../api/executions';

interface NodeInspectionPanelProps {
  nodeId: string;
  run: ExecutionResponse;
  onClose: () => void;
}

export const NodeInspectionPanel: React.FC<NodeInspectionPanelProps> = ({ nodeId, run, onClose }) => {
  const stepRun = run.steps?.[nodeId];
  const isTrigger = nodeId === 'trigger';

  const formatMs = (ms?: number) => {
    if (!ms) return '-';
    return `${(ms / 1000).toFixed(2)}s`;
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ x: 400, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: 400, opacity: 0 }}
        transition={{ type: 'spring', bounce: 0, duration: 0.3 }}
        className="absolute top-0 right-0 w-80 h-full bg-card/95 backdrop-blur-md border-l border-border/50 shadow-2xl z-50 flex flex-col overflow-hidden"
      >
        <div className="h-14 border-b border-border/50 flex items-center justify-between px-4 bg-accent/30 shrink-0">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded flex items-center justify-center bg-primary/10 text-primary">
              <Puzzle className="w-3.5 h-3.5" />
            </div>
            <span className="font-semibold text-sm truncate">{nodeId}</span>
          </div>
          <button 
            onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded-md hover:bg-accent text-muted-foreground transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-6 custom-scrollbar">
          {!stepRun && !isTrigger ? (
            <div className="text-sm text-muted-foreground text-center mt-10">
              No execution data for this node yet.
            </div>
          ) : (
            <>
              <div className="space-y-3">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Runtime Info</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="bg-muted/50 p-2 rounded-lg border border-border/50">
                    <div className="text-[10px] text-muted-foreground mb-1 flex items-center gap-1"><Clock className="w-3 h-3"/> Duration</div>
                    <div className="font-mono font-medium">{formatMs(stepRun?.duration_ms)}</div>
                  </div>
                  <div className="bg-muted/50 p-2 rounded-lg border border-border/50">
                    <div className="text-[10px] text-muted-foreground mb-1 flex items-center gap-1"><Zap className="w-3 h-3"/> Status</div>
                    <div className="font-medium text-xs font-mono">{stepRun?.status || (isTrigger ? run.status : 'PENDING')}</div>
                  </div>
                </div>
              </div>

              {stepRun?.error_message && (
                <div className="space-y-2">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-destructive flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5" /> Error Details
                  </h4>
                  <div className="bg-destructive/10 border border-destructive/20 text-destructive text-xs p-3 rounded-md font-mono whitespace-pre-wrap break-all">
                    {stepRun.error_message}
                  </div>
                </div>
              )}

              {stepRun?.outputs && Object.keys(stepRun.outputs).length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Outputs</h4>
                  <div className="bg-black/40 text-emerald-400 p-3 rounded-md text-[11px] font-mono overflow-x-auto whitespace-pre-wrap border border-white/5">
                    {JSON.stringify(stepRun.outputs, null, 2)}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
};
