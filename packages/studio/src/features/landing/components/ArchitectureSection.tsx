import React from 'react';

export const ArchitectureSection: React.FC = () => {
  return (
    <div className="w-full bg-[#0D0D12] rounded-2xl border border-white/10 p-6 overflow-hidden shadow-[inset_0_0_20px_rgba(0,0,0,0.5)] font-mono text-[10px] md:text-xs">
      <div className="flex items-center justify-between mb-4 text-slate-500 border-b border-white/5 pb-2">
        <span>flowcore-engine-trace</span>
        <span className="text-emerald-500 flex items-center gap-2">
          <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
          LIVE
        </span>
      </div>

      <div className="space-y-4 text-slate-300">
        <div className="flex items-start gap-4 hover:bg-white/5 p-2 rounded transition-colors">
          <span className="text-slate-500 w-16">00:00:01</span>
          <span className="text-blue-400 w-20">[PIPELINE]</span>
          <span>Initializing DAG compilation...</span>
        </div>
        <div className="flex items-start gap-4 hover:bg-white/5 p-2 rounded transition-colors">
          <span className="text-slate-500 w-16">00:00:04</span>
          <span className="text-emerald-400 w-20">[VALIDATE]</span>
          <span>Schema verified. 3 nodes identified.</span>
        </div>
        <div className="flex items-start gap-4 hover:bg-white/5 p-2 rounded transition-colors bg-white/5">
          <span className="text-slate-500 w-16">00:00:12</span>
          <span className="text-purple-400 w-20 animate-pulse">[EXECUTE]</span>
          <div className="flex-1">
            <p>Orchestrating batch sequence</p>
            <div className="mt-2 flex items-center gap-1">
              <div className="h-1 bg-emerald-500 rounded flex-1" />
              <div className="h-1 bg-emerald-500/30 rounded flex-1" />
              <div className="h-1 bg-emerald-500/10 rounded flex-1" />
            </div>
          </div>
        </div>
        <div className="flex items-start gap-4 hover:bg-white/5 p-2 rounded transition-colors">
          <span className="text-slate-500 w-16">00:00:45</span>
          <span className="text-blue-400 w-20">[SYSTEM]</span>
          <span>Records committed: <span className="text-emerald-400 font-bold">145,204</span></span>
        </div>
      </div>
    </div>
  );
};
