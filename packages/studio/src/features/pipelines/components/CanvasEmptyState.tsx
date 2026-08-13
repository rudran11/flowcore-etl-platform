import React from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
import { IllustrationNoPipelines } from '../../../components/ui/FlowCoreIllustrations';

export const CanvasEmptyState: React.FC = () => {
  return (
    <div className="absolute inset-0 z-0 flex items-center justify-center pointer-events-none">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="flex flex-col items-center text-center max-w-sm"
      >
        <div className="mb-6 relative w-64 h-40 flex items-center justify-center text-primary">
          <IllustrationNoPipelines className="w-full h-full text-primary" />
        </div>
        
        <h3 className="text-xl font-bold tracking-tight text-foreground mb-2">Build your Pipeline</h3>
        <p className="text-sm text-muted-foreground mb-8">
          The canvas is currently empty. Drag and drop connectors from the palette on the left to start building your ETL workflow.
        </p>
        
        <div className="flex items-center gap-3 text-sm font-semibold text-muted-foreground bg-accent/30 px-4 py-2.5 rounded-full border border-border shadow-surface backdrop-blur-sm">
          <ArrowLeft className="w-4 h-4 text-primary" />
          <span>Select a connector to begin</span>
        </div>
      </motion.div>
    </div>
  );
};
