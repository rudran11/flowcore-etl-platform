import { memo, useState } from 'react';
import { Handle, Position, NodeToolbar } from '@xyflow/react';
import { Play, Puzzle, CheckCircle2, AlertCircle, Clock, Copy, Trash2, ChevronDown, ChevronRight, Activity } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { usePipelineBuilderStore } from '../../../stores/pipelineBuilderStore';

const NodeToolbarActions = ({ isHovered }: { id?: string, data?: any, isHovered: boolean }) => {
  const { duplicateSelected, deleteSelected } = usePipelineBuilderStore();
  
  return (
    <NodeToolbar isVisible={isHovered} position={Position.Top} className="flex items-center gap-1 bg-card/90 backdrop-blur-md border border-border/50 shadow-md p-1 rounded-lg mb-2">
      <button 
        onClick={(e) => { e.stopPropagation(); duplicateSelected(); }}
        className="p-1.5 hover:bg-accent rounded-md text-muted-foreground hover:text-foreground transition-colors"
        title="Duplicate"
      >
        <Copy className="w-3.5 h-3.5" />
      </button>
      <button 
        onClick={(e) => { e.stopPropagation(); deleteSelected(); }}
        className="p-1.5 hover:bg-destructive/10 rounded-md text-muted-foreground hover:text-destructive transition-colors"
        title="Delete"
      >
        <Trash2 className="w-3.5 h-3.5" />
      </button>
    </NodeToolbar>
  );
};

export const TriggerNode = memo(({ id, data, selected }: any) => {
  const hasError = data.error;
  const hasWarning = data.warning;
  const isFailed = data.status === 'failed';
  const isWarning = hasWarning && !isFailed;
  const [isHovered, setIsHovered] = useState(false);
  
  return (
    <div 
      className="group relative"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <NodeToolbarActions id={id} data={data} isHovered={isHovered || selected} />
      
      {/* Running/Error Pulses */}
      {hasError && <div className="absolute -inset-2 rounded-2xl bg-status-error/20 blur-md animate-pulse pointer-events-none" />}
      {data.status === 'running' && <div className="absolute -inset-2 rounded-2xl bg-status-running/20 blur-md animate-pulse pointer-events-none" />}
      
      <div className="absolute top-0 inset-x-0 h-1 bg-emerald-500 z-10" />

      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.15 }}
        className={`bg-card rounded-xl w-72 overflow-hidden transition-all duration-200 relative hover:-translate-y-0.5 ${
          selected 
            ? 'shadow-[0_0_0_2px_hsl(var(--primary)),0_8px_24px_-4px_rgba(0,0,0,0.1)] border-transparent' 
            : isFailed || hasError 
              ? 'shadow-[0_0_0_2px_hsl(var(--status-error)),0_4px_12px_-2px_rgba(0,0,0,0.1)] border-transparent' 
              : isWarning 
                ? 'shadow-[0_0_0_2px_hsl(var(--status-warning)),0_4px_12px_-2px_rgba(0,0,0,0.1)] border-transparent' 
                : 'shadow-surface-elevated border-border'
        } border`}
      >
        <div className="p-3.5 flex items-center gap-3 border-b border-border bg-accent/20">
          <div className="w-8 h-8 rounded-md bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20 shadow-sm">
            <Play className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-semibold text-foreground tracking-tight truncate">Pipeline Trigger</div>
            <div className="text-[10px] text-muted-foreground font-mono truncate uppercase flex items-center gap-1 mt-0.5">
              <span className="bg-background px-1.5 py-0.5 rounded shadow-sm border border-border">{data.type || 'Manual'}</span>
            </div>
          </div>
          {isFailed && <AlertCircle className="w-4 h-4 text-status-error shrink-0" />}
          {isWarning && <AlertCircle className="w-4 h-4 text-status-warning shrink-0" />}
        </div>
        
        <div className="p-3.5 text-xs text-muted-foreground flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="w-3.5 h-3.5" />
            <span>{data.schedule || 'Run on demand'}</span>
          </div>
        </div>
        
        <Handle type="source" position={Position.Bottom} className="w-4 h-4 bg-background border-2 border-primary hover:scale-125 transition-transform" />
      </motion.div>
    </div>
  );
});

export const StepNode = memo(({ id, data, selected }: any) => {
  const hasError = data.error;
  const hasWarning = data.warning;
  const isFailed = data.status === 'failed';
  const isWarning = hasWarning && !isFailed;
  
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const isRunning = data.status === 'running';
  const duration = data.duration || '0ms';

  return (
    <div 
      className="group relative"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <NodeToolbarActions id={id} data={data} isHovered={isHovered || selected} />
      
      {/* Running/Error Pulses */}
      {hasError && <div className="absolute -inset-2 rounded-2xl bg-status-error/20 blur-md animate-pulse pointer-events-none" />}
      {isRunning && <div className="absolute -inset-2 rounded-2xl bg-status-running/20 blur-md animate-pulse pointer-events-none" />}
      
      {/* Band color based on plugin type */}
      <div className={`absolute top-0 inset-x-0 h-1 z-10 ${data.plugin_id?.includes('source') ? 'bg-blue-500' : data.plugin_id?.includes('destination') ? 'bg-emerald-500' : 'bg-purple-500'}`} />

      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.15 }}
        className={`bg-card rounded-xl w-72 overflow-hidden transition-all duration-200 relative hover:-translate-y-0.5 ${
          selected 
            ? 'shadow-[0_0_0_2px_hsl(var(--primary)),0_8px_24px_-4px_rgba(0,0,0,0.1)] border-transparent' 
            : isFailed || hasError 
              ? 'shadow-[0_0_0_2px_hsl(var(--status-error)),0_4px_12px_-2px_rgba(0,0,0,0.1)] border-transparent' 
              : isWarning 
                ? 'shadow-[0_0_0_2px_hsl(var(--status-warning)),0_4px_12px_-2px_rgba(0,0,0,0.1)] border-transparent' 
                : 'shadow-surface-elevated border-border'
        } border`}
      >
        <Handle type="target" position={Position.Top} className={`w-3 h-3 bg-background border-2 ${isFailed || hasError ? 'border-status-error' : isWarning ? 'border-status-warning' : 'border-primary'} hover:scale-125 transition-transform shadow-sm`} />
        
        {/* Header */}
        <div className={`p-3.5 flex items-center gap-3 border-b border-border ${isFailed || hasError ? 'bg-status-error/5' : isWarning ? 'bg-status-warning/5' : 'bg-accent/20'}`}>
          <div className={`w-8 h-8 rounded-md flex items-center justify-center border shadow-sm ${isFailed || hasError ? 'bg-status-error/10 border-status-error/20 text-status-error' : isWarning ? 'bg-status-warning/10 border-status-warning/20 text-status-warning' : 'bg-background border-border text-foreground'}`}>
            <Puzzle className="w-4 h-4" />
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="text-sm font-semibold tracking-tight text-foreground truncate">{data.label || 'Step'}</div>
            <div className="text-[10px] text-muted-foreground font-mono truncate">{data.plugin_id || 'Unknown Plugin'}</div>
          </div>
          
          <button 
            onClick={(e) => { e.stopPropagation(); setIsCollapsed(!isCollapsed); }}
            className="w-5 h-5 flex items-center justify-center rounded-md hover:bg-accent text-muted-foreground transition-colors shadow-sm bg-background border border-border"
          >
            {isCollapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
        
        {/* Body */}
        <AnimatePresence>
          {!isCollapsed && (
            <motion.div 
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="p-3.5 bg-background/50 border-b border-border/50">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-[10px] uppercase font-semibold tracking-wider text-muted-foreground">Properties</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {data.config && Object.keys(data.config).slice(0, 3).map(k => (
                    <span key={k} className="text-[10px] bg-accent border border-border/50 px-1.5 py-0.5 rounded text-foreground font-medium">
                      {k}
                    </span>
                  ))}
                  {(!data.config || Object.keys(data.config).length === 0) && (
                    <span className="text-[10px] text-muted-foreground italic">No configuration</span>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Footer / Status */}
        <div className="px-3.5 py-2.5 flex items-center justify-between bg-accent/10 text-xs">
          <div className="flex items-center gap-2">
            {isRunning ? (
              <div className="flex items-center gap-1.5 text-primary">
                <Activity className="w-3.5 h-3.5 animate-pulse" />
                <span className="font-medium text-[11px]">Running</span>
              </div>
            ) : isFailed || hasError ? (
              <div className="flex items-center gap-1.5 text-destructive group relative cursor-help">
                <AlertCircle className="w-3.5 h-3.5" />
                <span className="font-medium text-[11px]">{isFailed ? 'Failed' : 'Error'}</span>
                {data.issues && data.issues.length > 0 && (
                  <div className="absolute bottom-full left-0 mb-1 hidden group-hover:block w-48 p-2 bg-zinc-900 border border-border/50 shadow-lg rounded text-[10px] text-white z-50">
                    {data.issues[0].title}
                  </div>
                )}
              </div>
            ) : isWarning ? (
              <div className="flex items-center gap-1.5 text-amber-500 group relative cursor-help">
                <AlertCircle className="w-3.5 h-3.5" />
                <span className="font-medium text-[11px]">Warning</span>
                {data.issues && data.issues.length > 0 && (
                  <div className="absolute bottom-full left-0 mb-1 hidden group-hover:block w-48 p-2 bg-zinc-900 border border-border/50 shadow-lg rounded text-[10px] text-white z-50">
                    {data.issues[0].title}
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-1.5 text-emerald-500">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span className="font-medium text-[11px]">Ready</span>
              </div>
            )}
          </div>
          
          <div className="flex items-center gap-2 text-muted-foreground">
            {data.duration && <span className="text-[11px] font-mono">{duration}</span>}
          </div>
        </div>
        
        <Handle type="source" position={Position.Bottom} className={`w-4 h-4 bg-background border-2 ${isFailed ? 'border-destructive' : isWarning ? 'border-amber-500' : 'border-primary'} hover:scale-125 transition-transform`} />
      </motion.div>
    </div>
  );
});
