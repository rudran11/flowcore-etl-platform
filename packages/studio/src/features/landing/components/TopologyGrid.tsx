import React, { useEffect, useState } from 'react';
import { Database, Filter, Server } from 'lucide-react';
import { DataFlowSVG } from './DataFlowSVG';

interface NodeProps {
  id: string;
  type: 'source' | 'transform' | 'destination';
  icon: React.ComponentType<any>;
  label: string;
  sublabel: string;
  x: number;
  y: number;
  z: number;
  is3D: boolean;
  delay?: number;
}

const Node: React.FC<NodeProps> = ({ type, icon: Icon, label, sublabel, x, y, z, is3D, delay = 0 }) => {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    const timer = setTimeout(() => setMounted(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);

  const typeStyles = {
    source: 'border-blue-500/50 shadow-[0_0_20px_rgba(59,130,246,0.15)] text-blue-400',
    transform: 'border-emerald-500/50 shadow-[0_0_20px_rgba(16,185,129,0.15)] text-emerald-400',
    destination: 'border-purple-500/50 shadow-[0_0_20px_rgba(168,85,247,0.15)] text-purple-400',
  };

  const style = is3D ? {
    transform: `translate3d(${x}px, ${y}px, ${z}px)`,
    transition: 'opacity 0.8s ease-out, transform 0.8s cubic-bezier(0.16, 1, 0.3, 1)',
    opacity: mounted ? 1 : 0,
    // When not mounted, it sits flat on the grid
    ...( !mounted && { transform: `translate3d(${x}px, ${y}px, 0px)` } )
  } : {
    left: `calc(50% + ${x}px)`,
    top: `calc(50% + ${y}px)`,
    transform: 'translate(-50%, -50%)',
    opacity: mounted ? 1 : 0,
    transition: 'opacity 0.8s ease-out',
  };

  return (
    <div 
      className={`absolute w-48 bg-card border-t-2 border-border/50 rounded-xl p-3 shadow-surface-elevated flex flex-col gap-2 ${typeStyles[type]}`}
      style={style}
    >
      <div className="absolute top-0 left-0 right-0 h-1 rounded-t-[10px] bg-current opacity-20" />
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-background border border-border/50 flex items-center justify-center text-current shadow-sm">
          <Icon className="w-4 h-4" />
        </div>
        <div className="flex flex-col">
          <span className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">{type}</span>
          <span className="text-sm font-semibold text-foreground tracking-tight">{label}</span>
        </div>
      </div>
      <div className="px-2 py-1 bg-background/50 rounded border border-border/50 font-mono text-[10px] text-muted-foreground flex justify-between items-center">
        <span>{sublabel}</span>
        {mounted && (
          <span className="relative flex h-1.5 w-1.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-current opacity-75"></span>
            <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-current"></span>
          </span>
        )}
      </div>
    </div>
  );
};

export const TopologyGrid: React.FC<{ is3D: boolean }> = ({ is3D }) => {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    // Wake up sequence triggers the SVG lines
    const timer = setTimeout(() => setMounted(true), 1500); // Wait for nodes
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="relative w-full max-w-[1000px] h-[600px]" style={{ transformStyle: 'preserve-3d' }}>
      {/* Data Flow SVG Lines (Midground) */}
      <div 
        className="absolute inset-0 pointer-events-none transition-opacity duration-1000"
        style={{ 
          transform: is3D ? 'translateZ(10px)' : 'none',
          opacity: mounted ? 1 : 0
        }}
      >
        <DataFlowSVG is3D={is3D} />
      </div>

      {/* Nodes (Foreground) */}
      <div className="absolute inset-0 pointer-events-none" style={{ transformStyle: 'preserve-3d' }}>
        <Node id="src1" type="source" icon={Database} label="PostgreSQL" sublabel="users_db" x={-300} y={-150} z={80} is3D={is3D} delay={100} />
        <Node id="src2" type="source" icon={Server} label="S3 Bucket" sublabel="raw_events" x={-250} y={150} z={60} is3D={is3D} delay={300} />
        
        <Node id="tf1" type="transform" icon={Filter} label="Aggregation" sublabel="group_by_id" x={0} y={-50} z={120} is3D={is3D} delay={600} />
        <Node id="tf2" type="transform" icon={Filter} label="Enrichment" sublabel="join_meta" x={50} y={100} z={100} is3D={is3D} delay={800} />
        
        <Node id="dst1" type="destination" icon={Database} label="ClickHouse" sublabel="analytics" x={300} y={-100} z={70} is3D={is3D} delay={1100} />
      </div>
    </div>
  );
};
