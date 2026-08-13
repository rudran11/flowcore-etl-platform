import React, { useState } from 'react';
import { Database, Filter } from 'lucide-react';

export const InteractivePipeline: React.FC = () => {
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  const Node = ({ id, label, icon: Icon, colorClass }: any) => {
    const isHovered = hoveredNode === id;
    const isFaded = hoveredNode && hoveredNode !== id;

    return (
      <div 
        onMouseEnter={() => setHoveredNode(id)}
        onMouseLeave={() => setHoveredNode(null)}
        className={`
          relative z-10 flex items-center gap-3 bg-card border border-border p-3 rounded-lg cursor-pointer
          transition-all duration-300 ease-out shadow-sm
          ${isHovered ? 'translate-y-[-4px] shadow-surface-elevated ring-1 ring-primary/30' : ''}
          ${isFaded ? 'opacity-40' : 'opacity-100'}
        `}
      >
        <div className={`w-8 h-8 rounded-md bg-background flex items-center justify-center border border-border ${colorClass}`}>
          <Icon className="w-4 h-4" />
        </div>
        <span className="font-semibold text-sm">{label}</span>

        {/* Hover Tooltip */}
        {isHovered && (
          <div className="absolute top-full left-1/2 -translate-x-1/2 mt-3 w-40 bg-foreground text-background text-[10px] p-2 rounded shadow-xl font-mono text-center z-50">
            {id === 'n1' && '1,284 records read'}
            {id === 'n2' && 'JSON parsed (12ms)'}
            {id === 'n3' && 'Inserted successfully'}
            <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-foreground rotate-45" />
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="w-full h-full flex items-center justify-center relative p-8">
      {/* Background SVG Edge */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 0 }}>
        <path 
          d="M 20% 50% L 50% 50% L 80% 50%" 
          fill="none" 
          stroke="hsl(var(--primary))" 
          strokeWidth="2"
          className="transition-opacity duration-300"
          style={{ opacity: hoveredNode ? 1 : 0.2 }}
        />
        {hoveredNode && (
          <circle r="3" fill="hsl(var(--primary))" filter="drop-shadow(0 0 4px hsl(var(--primary)))">
            <animateMotion dur="1s" repeatCount="indefinite" path="M 20% 50% L 50% 50% L 80% 50%" />
          </circle>
        )}
      </svg>

      <div className="flex items-center w-full justify-between max-w-sm">
        <Node id="n1" label="PostgreSQL" icon={Database} colorClass="text-blue-400" />
        <Node id="n2" label="Transform" icon={Filter} colorClass="text-emerald-400" />
        <Node id="n3" label="S3 Output" icon={Database} colorClass="text-purple-400" />
      </div>
    </div>
  );
};
