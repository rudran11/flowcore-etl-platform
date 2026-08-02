import React from 'react';
import { motion } from 'framer-motion';
import { Network, Plus, ArrowLeft } from 'lucide-react';
import { usePipelineBuilderStore } from '../../../stores/pipelineBuilderStore';

export const CanvasEmptyState: React.FC = () => {
  return (
    <div className="absolute inset-0 z-0 flex items-center justify-center pointer-events-none">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="flex flex-col items-center text-center max-w-sm"
      >
        <div className="w-24 h-24 bg-card shadow-sm border border-border/50 rounded-2xl flex items-center justify-center mb-6 relative">
          <div className="absolute inset-0 bg-primary/10 rounded-2xl animate-pulse" />
          <Network className="w-10 h-10 text-primary relative z-10" />
          
          {/* Decorative small nodes around the main one */}
          <div className="absolute -top-3 -right-3 w-8 h-8 bg-card border border-border/50 rounded-lg flex items-center justify-center shadow-sm">
            <div className="w-2 h-2 bg-emerald-500 rounded-full" />
          </div>
          <div className="absolute -bottom-3 -left-3 w-8 h-8 bg-card border border-border/50 rounded-lg flex items-center justify-center shadow-sm">
            <div className="w-2 h-2 bg-blue-500 rounded-full" />
          </div>
        </div>
        
        <h3 className="text-xl font-semibold text-foreground mb-2">Build your Pipeline</h3>
        <p className="text-sm text-muted-foreground mb-8">
          The canvas is currently empty. Drag and drop connectors from the palette on the left to start building your ETL workflow.
        </p>
        
        <div className="flex items-center gap-3 text-sm font-medium text-muted-foreground bg-accent/50 px-4 py-2 rounded-full border border-border/50">
          <ArrowLeft className="w-4 h-4" />
          <span>Select a connector to begin</span>
        </div>
      </motion.div>
    </div>
  );
};
