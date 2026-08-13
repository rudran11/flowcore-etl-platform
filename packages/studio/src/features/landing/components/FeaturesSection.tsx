import React from 'react';
import { InteractivePipeline } from './InteractivePipeline';
import { ArchitectureSection } from './ArchitectureSection';
import { Box, CheckCircle, Play, Activity } from 'lucide-react';

export const FeaturesSection: React.FC = () => {
  return (
    <section id="platform" className="w-full py-32 relative z-10 border-t border-white/5 bg-transparent min-h-[150vh] flex flex-col justify-center">
      <div className="max-w-[1400px] mx-auto px-6 w-full">
        
        <div className="text-center max-w-3xl mx-auto mb-32 bg-background/80 backdrop-blur-md p-8 rounded-3xl border border-white/5 shadow-surface-elevated">
          <h2 className="text-sm font-bold tracking-widest uppercase text-primary mb-4">The Complete Lifecycle</h2>
          <h3 className="text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            One system for your entire data infrastructure.
          </h3>
        </div>

        <div className="grid md:grid-cols-2 gap-8 mb-32">
          {/* BUILD */}
          <div className="bg-card/70 backdrop-blur-md border border-border shadow-surface rounded-3xl p-10 overflow-hidden relative group min-h-[500px]">
            <div className="absolute inset-0 bg-dot-topology opacity-20 pointer-events-none" />
            <div className="relative z-10 mb-12">
              <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center text-primary mb-6 shadow-sm border border-primary/20">
                <Box className="w-6 h-6" />
              </div>
              <h4 className="text-2xl font-bold mb-3">Build Visually</h4>
              <p className="text-muted-foreground text-lg leading-relaxed max-w-sm">
                Construct complex ETL pipelines using a strictly typed visual DAG. Connect sources, map schemas, and stream data seamlessly.
              </p>
            </div>
            {/* Embedded interactive pipeline */}
            <div className="h-[250px] relative mt-auto border border-border/50 rounded-2xl bg-background/50 overflow-hidden shadow-inner">
              <InteractivePipeline />
            </div>
          </div>

          {/* VALIDATE & EXECUTE */}
          <div className="flex flex-col gap-8 min-h-[500px]">
            <div className="bg-card/70 backdrop-blur-md border border-border shadow-surface rounded-3xl p-10 relative flex-1">
              <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center text-emerald-400 mb-6 shadow-sm border border-emerald-500/20">
                <CheckCircle className="w-6 h-6" />
              </div>
              <h4 className="text-2xl font-bold mb-3">Schema Validation</h4>
              <p className="text-muted-foreground text-lg leading-relaxed">
                Strongly typed connector schemas ensure your pipeline won't run unless the data contracts match perfectly.
              </p>
            </div>
            
            <div className="bg-card/70 backdrop-blur-md border border-border shadow-surface rounded-3xl p-10 relative flex-1">
              <div className="w-12 h-12 bg-purple-500/10 rounded-xl flex items-center justify-center text-purple-400 mb-6 shadow-sm border border-purple-500/20">
                <Play className="w-6 h-6" />
              </div>
              <h4 className="text-2xl font-bold mb-3">DAG Execution Engine</h4>
              <p className="text-muted-foreground text-lg leading-relaxed">
                A deterministic execution layer orchestrates parallelism and dependency resolution automatically.
              </p>
            </div>
          </div>
        </div>

        {/* OBSERVE / ARCHITECTURE */}
        <div id="observability" className="bg-card/70 backdrop-blur-md border border-border shadow-surface rounded-3xl p-10 md:p-16 overflow-hidden relative min-h-[600px] flex items-center">
          <div className="flex flex-col md:flex-row gap-12 items-center">
            <div className="w-full md:w-1/3 relative z-10">
              <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center text-blue-400 mb-6 shadow-sm border border-blue-500/20">
                <Activity className="w-6 h-6" />
              </div>
              <h4 className="text-3xl font-bold mb-4">Deep Observability</h4>
              <p className="text-muted-foreground text-lg leading-relaxed">
                Every execution is tracked. View real-time traces, node-level status telemetry, and structured logs inside the Studio.
              </p>
            </div>
            <div className="w-full md:w-2/3">
              <ArchitectureSection />
            </div>
          </div>
        </div>

      </div>
    </section>
  );
};
