import React from 'react';
import { Database, FileJson, Server, Cloud, Table2, LayoutGrid } from 'lucide-react';

export const ConnectorEcosystem: React.FC = () => {
  return (
    <section id="ecosystem" className="w-full py-48 bg-transparent relative z-10 border-t border-white/5 overflow-hidden min-h-[100vh] flex flex-col justify-center">
      <div className="absolute inset-0 bg-dot-topology opacity-20 pointer-events-none" />
      
      <div className="max-w-[1400px] mx-auto px-6 relative z-10 w-full">
        <div className="text-center max-w-3xl mx-auto mb-16 bg-background/80 backdrop-blur-md p-8 rounded-3xl border border-white/5 shadow-surface-elevated">
          <h2 className="text-sm font-bold tracking-widest uppercase text-primary mb-4">Extensible Architecture</h2>
          <h3 className="text-4xl font-bold tracking-tight text-foreground">
            Connect to any source or destination.
          </h3>
        </div>

        <div className="relative h-[400px] w-full max-w-4xl mx-auto flex items-center justify-center">
          
          {/* Central Hub */}
          <div className="absolute w-24 h-24 bg-card border border-border shadow-surface-elevated rounded-2xl flex flex-col items-center justify-center z-20 shadow-[0_0_40px_rgba(var(--primary),0.2)] ring-1 ring-primary/30">
            <LayoutGrid className="w-8 h-8 text-primary mb-1" />
            <span className="text-[10px] font-bold uppercase tracking-wider text-primary">FlowCore</span>
          </div>

          {/* Connectors */}
          <div className="absolute w-full h-full animate-[spin_60s_linear_infinite]">
            <div className="absolute top-10 left-10 w-16 h-16 bg-card border border-border rounded-xl flex items-center justify-center shadow-surface">
              <Database className="w-6 h-6 text-blue-400" />
            </div>
            <div className="absolute bottom-10 left-20 w-16 h-16 bg-card border border-border rounded-xl flex items-center justify-center shadow-surface">
              <Table2 className="w-6 h-6 text-emerald-400" />
            </div>
            <div className="absolute top-20 right-10 w-16 h-16 bg-card border border-border rounded-xl flex items-center justify-center shadow-surface">
              <Cloud className="w-6 h-6 text-purple-400" />
            </div>
            <div className="absolute bottom-20 right-20 w-16 h-16 bg-card border border-border rounded-xl flex items-center justify-center shadow-surface">
              <FileJson className="w-6 h-6 text-amber-400" />
            </div>
            <div className="absolute top-1/2 left-0 -translate-y-1/2 w-16 h-16 bg-card border border-border rounded-xl flex items-center justify-center shadow-surface">
              <Server className="w-6 h-6 text-slate-400" />
            </div>
            
            {/* SVG Connecting Lines */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-20 -z-10">
              <path d="M 50% 50% L 10% 10%" stroke="hsl(var(--primary))" strokeWidth="2" strokeDasharray="4 4" />
              <path d="M 50% 50% L 20% 90%" stroke="hsl(var(--primary))" strokeWidth="2" strokeDasharray="4 4" />
              <path d="M 50% 50% L 90% 20%" stroke="hsl(var(--primary))" strokeWidth="2" strokeDasharray="4 4" />
              <path d="M 50% 50% L 80% 80%" stroke="hsl(var(--primary))" strokeWidth="2" strokeDasharray="4 4" />
              <path d="M 50% 50% L 0% 50%" stroke="hsl(var(--primary))" strokeWidth="2" strokeDasharray="4 4" />
            </svg>
          </div>

        </div>
      </div>
    </section>
  );
};
