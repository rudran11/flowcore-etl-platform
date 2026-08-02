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
  const isFailed = data.status === 'failed';
  const isWarning = hasError && !isFailed;
  const [isHovered, setIsHovered] = useState(false);
  
  return (
    <div 
      className="group"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <NodeToolbarActions id={id} data={data} isHovered={isHovered || selected} />
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        whileHover={{ y: -2 }}
        className={`bg-card border-2 rounded-xl shadow-lg w-72 overflow-hidden transition-all duration-200 ${
          selected ? 'border-primary ring-2 ring-primary/20 shadow-primary/10' : isFailed ? 'border-destructive' : isWarning ? 'border-amber-500' : 'border-border/50 hover:border-border'
        }`}
      >
        <div className="p-3.5 flex items-center gap-3 border-b border-border/50 bg-accent/30">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
            <Play className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-semibold text-foreground truncate">Pipeline Trigger</div>
            <div className="text-xs text-muted-foreground truncate flex items-center gap-1 mt-0.5">
              <span className="bg-accent px-1.5 py-0.5 rounded border border-border/50 text-[10px] uppercase font-medium">{data.type || 'Manual'}</span>
            </div>
          </div>
          {isFailed && <AlertCircle className="w-4 h-4 text-destructive shrink-0" />}
          {isWarning && <AlertCircle className="w-4 h-4 text-amber-500 shrink-0" />}
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
  const isFailed = data.status === 'failed';
  const isWarning = hasError && !isFailed;
  
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
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        whileHover={{ y: -2 }}
        className={`bg-card border-2 rounded-xl shadow-lg w-72 overflow-hidden transition-all duration-200 ${
          selected ? 'border-primary ring-2 ring-primary/20 shadow-primary/10' : isFailed ? 'border-destructive shadow-destructive/10' : isWarning ? 'border-amber-500' : 'border-border/50 hover:border-border'
        }`}
      >
        <Handle type="target" position={Position.Top} className={`w-4 h-4 bg-background border-2 ${isFailed ? 'border-destructive' : isWarning ? 'border-amber-500' : 'border-primary'} hover:scale-125 transition-transform`} />
        
        {/* Header */}
        <div className={`p-3.5 flex items-center gap-3 border-b border-border/50 ${isFailed ? 'bg-destructive/5' : isWarning ? 'bg-amber-500/5' : 'bg-accent/30'}`}>
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center border ${isFailed ? 'bg-destructive/10 border-destructive/20 text-destructive' : isWarning ? 'bg-amber-500/10 border-amber-500/20 text-amber-500' : 'bg-background border-border/50 shadow-sm text-primary'}`}>
            <Puzzle className="w-4 h-4" />
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="text-sm font-semibold text-foreground truncate">{data.label || 'Step'}</div>
            <div className="text-[11px] text-muted-foreground truncate">{data.plugin_id || 'Unknown Plugin'}</div>
          </div>
          
          <button 
            onClick={(e) => { e.stopPropagation(); setIsCollapsed(!isCollapsed); }}
            className="w-5 h-5 flex items-center justify-center rounded-md hover:bg-accent text-muted-foreground transition-colors"
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
            ) : isFailed ? (
              <div className="flex items-center gap-1.5 text-destructive">
                <AlertCircle className="w-3.5 h-3.5" />
                <span className="font-medium text-[11px]">Failed</span>
              </div>
            ) : isWarning ? (
              <div className="flex items-center gap-1.5 text-amber-500">
                <AlertCircle className="w-3.5 h-3.5" />
                <span className="font-medium text-[11px]">Needs Config</span>
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
