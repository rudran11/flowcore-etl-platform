import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Play, Puzzle, CheckCircle2, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

export const TriggerNode = memo(({ data }: any) => {
  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-zinc-950 border-2 border-emerald-500/50 rounded-xl shadow-lg shadow-emerald-500/10 w-64 overflow-hidden"
    >
      <div className="bg-emerald-500/10 p-3 flex items-center gap-3 border-b border-emerald-500/20">
        <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center">
          <Play className="w-4 h-4 text-emerald-500" />
        </div>
        <div>
          <div className="text-sm font-semibold text-emerald-500">Trigger</div>
          <div className="text-xs text-zinc-400">{data.type || 'Manual'}</div>
        </div>
      </div>
      
      {data.schedule && (
        <div className="p-3 text-xs text-zinc-300">
          <span className="text-zinc-500 mr-2">Schedule:</span>
          <span className="font-mono bg-zinc-900 px-1.5 py-0.5 rounded">{data.schedule}</span>
        </div>
      )}
      
      <Handle type="source" position={Position.Bottom} className="w-3 h-3 bg-emerald-500 border-2 border-zinc-950" />
    </motion.div>
  );
});

import { usePipelineBuilderStore } from '../../../stores/pipelineBuilderStore';

export const StepNode = memo((props: any) => {
  const { data, selected, id } = props;
  const hasError = data.error;
  const { openTemplateDialog } = usePipelineBuilderStore();

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`bg-zinc-950 border-2 rounded-xl shadow-lg w-64 overflow-hidden transition-colors ${
        selected ? 'border-primary' : hasError ? 'border-rose-500/50' : 'border-white/10 hover:border-white/20'
      } ${selected ? 'shadow-primary/20' : 'shadow-black/50'}`}
    >
      <Handle type="target" position={Position.Top} className={`w-3 h-3 ${hasError ? 'bg-rose-500' : 'bg-zinc-400'} border-2 border-zinc-950`} />
      
      <div className={`p-3 flex items-center gap-3 border-b ${hasError ? 'border-rose-500/20 bg-rose-500/5' : 'border-white/5 bg-zinc-900/50'}`}>
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${hasError ? 'bg-rose-500/20' : 'bg-zinc-800'}`}>
          <Puzzle className={`w-4 h-4 ${hasError ? 'text-rose-500' : 'text-zinc-400'}`} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-semibold text-white truncate">{data.label}</div>
          <div className="text-xs text-zinc-500 truncate">{data.plugin_id || 'Unknown Plugin'}</div>
        </div>
        {hasError ? (
          <AlertCircle className="w-4 h-4 text-rose-500 shrink-0" />
        ) : (
          <CheckCircle2 className="w-4 h-4 text-emerald-500/50 shrink-0" />
        )}
        <button 
          onClick={(e) => {
            e.stopPropagation();
            openTemplateDialog({ id, type: 'stepNode', data, position: { x: 0, y: 0 } });
          }}
          className="ml-1 w-6 h-6 rounded flex items-center justify-center hover:bg-zinc-800 text-zinc-500 hover:text-white transition-colors"
          title="Save as Template"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>
        </button>
      </div>
      
      <div className="p-3 bg-zinc-950/50">
        <div className="text-xs text-zinc-500 mb-1">Configuration</div>
        <div className="flex flex-wrap gap-1">
          {data.config && Object.keys(data.config).slice(0, 3).map(k => (
            <span key={k} className="text-[10px] bg-zinc-900 border border-white/5 px-1.5 py-0.5 rounded text-zinc-400">
              {k}
            </span>
          ))}
          {(!data.config || Object.keys(data.config).length === 0) && (
            <span className="text-[10px] text-zinc-600 italic">Empty</span>
          )}
        </div>
      </div>
      
      <Handle type="source" position={Position.Bottom} className={`w-3 h-3 ${hasError ? 'bg-rose-500' : 'bg-zinc-400'} border-2 border-zinc-950`} />
    </motion.div>
  );
});
