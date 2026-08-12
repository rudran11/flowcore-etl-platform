import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { usePipelineBuilderStore } from '../../../stores/pipelineBuilderStore';
import { X, AlertTriangle, AlertCircle, Info, ChevronRight, Settings2, Trash2, CheckCircle2, Loader2 } from 'lucide-react';
import { useReactFlow } from '@xyflow/react';
import { Button } from '../../../components/ui/button';
import { ValidationIssue } from '../utils/validationEngine';

export const ValidationPanel: React.FC = () => {
  const { 
    validationIssues, 
    isValidationPanelOpen, 
    setValidationPanelOpen,
    validatePipeline,
    deleteSelected,
    nodes,
    setNodes
  } = usePipelineBuilderStore();
  
  const [isRevalidating, setIsRevalidating] = useState(false);
  const { fitView, setCenter } = useReactFlow();

  const handleRevalidate = () => {
    setIsRevalidating(true);
    setTimeout(() => {
      validatePipeline();
      setIsRevalidating(false);
    }, 400); // give users a brief visual feedback that something happened
  };

  const errors = validationIssues.filter(i => i.severity === 'error');
  const warnings = validationIssues.filter(i => i.severity === 'warning');
  const suggestions = validationIssues.filter(i => i.severity === 'suggestion');

  if (!isValidationPanelOpen) return null;

  const handleIssueClick = (issue: ValidationIssue) => {
    if (issue.nodeId) {
      // Focus node
      const node = nodes.find(n => n.id === issue.nodeId);
      if (node) {
        setCenter(node.position.x + 100, node.position.y + 50, { zoom: 1.2, duration: 800 });
        setNodes(nodes.map(n => ({ ...n, selected: n.id === issue.nodeId })));
      }
    } else {
      fitView({ duration: 800 });
    }
  };

  const handleQuickFix = (issue: ValidationIssue, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!issue.nodeId) return;

    if (issue.quickFix === 'delete_node') {
      setNodes(nodes.map(n => ({ ...n, selected: n.id === issue.nodeId })));
      setTimeout(() => deleteSelected(), 50);
    } else if (issue.quickFix === 'open_config') {
      setNodes(nodes.map(n => ({ ...n, selected: n.id === issue.nodeId })));
      // ConfigPanel opens automatically when a node is selected
    }
  };

  const handleFixNext = () => {
    const nextIssue = errors[0] || warnings[0] || suggestions[0];
    if (nextIssue) {
      handleIssueClick(nextIssue);
      if (nextIssue.quickFix === 'open_config') {
        handleQuickFix(nextIssue, { stopPropagation: () => {} } as any);
      }
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ y: '100%', opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: '100%', opacity: 0 }}
        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
        className="absolute bottom-4 left-1/2 -translate-x-1/2 w-[600px] max-h-[400px] bg-card border border-border/50 shadow-2xl rounded-xl flex flex-col z-40 overflow-hidden"
      >
        <div className="flex items-center justify-between p-3 border-b border-white/5 bg-zinc-950/80 backdrop-blur-sm">
          <div className="flex items-center gap-4">
            <h3 className="font-semibold text-sm flex items-center gap-2">
              Pipeline Validation
              <span className="text-[10px] bg-white/10 px-2 py-0.5 rounded-full">{validationIssues.length} Issues</span>
            </h3>
            
            <div className="flex items-center gap-3 text-[11px] font-medium">
              <div className="flex items-center gap-1 text-red-400">
                <AlertCircle className="w-3.5 h-3.5" /> {errors.length}
              </div>
              <div className="flex items-center gap-1 text-amber-400">
                <AlertTriangle className="w-3.5 h-3.5" /> {warnings.length}
              </div>
              <div className="flex items-center gap-1 text-blue-400">
                <Info className="w-3.5 h-3.5" /> {suggestions.length}
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button 
              variant="outline" 
              size="sm" 
              className="h-7 text-[10px] px-2 border-white/10 gap-1.5 min-w-[80px]" 
              onClick={handleRevalidate}
              disabled={isRevalidating}
            >
              {isRevalidating && <Loader2 className="w-3 h-3 animate-spin" />}
              {isRevalidating ? 'Checking...' : 'Revalidate'}
            </Button>
            <Button variant="ghost" size="icon" onClick={() => setValidationPanelOpen(false)} className="h-7 w-7 text-muted-foreground hover:text-foreground rounded-full">
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-2 bg-zinc-950/30 custom-scrollbar space-y-2">
          {validationIssues.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-40 text-center text-muted-foreground opacity-70">
              <CheckCircle2 className="w-12 h-12 text-emerald-500 mb-3 opacity-80" />
              <p className="text-sm font-medium text-emerald-400">No issues found</p>
              <p className="text-[11px]">Your pipeline is structurally sound and ready to run.</p>
            </div>
          ) : (
            validationIssues.map(issue => (
              <div 
                key={issue.id} 
                className="group flex flex-col p-3 rounded-lg border border-white/5 bg-zinc-900/50 hover:bg-zinc-800/80 cursor-pointer transition-colors"
                onClick={() => handleIssueClick(issue)}
              >
                <div className="flex items-start gap-3">
                  <div className={`mt-0.5 shrink-0 ${
                    issue.severity === 'error' ? 'text-red-400' : 
                    issue.severity === 'warning' ? 'text-amber-400' : 'text-blue-400'
                  }`}>
                    {issue.severity === 'error' ? <AlertCircle className="w-4 h-4" /> : 
                     issue.severity === 'warning' ? <AlertTriangle className="w-4 h-4" /> : 
                     <Info className="w-4 h-4" />}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <h4 className="text-xs font-semibold text-foreground flex items-center gap-2">
                      {issue.title}
                      {issue.nodeId && <span className="text-[10px] font-mono bg-white/5 px-1.5 rounded text-muted-foreground">{issue.nodeId}</span>}
                    </h4>
                    <p className="text-[11px] text-muted-foreground mt-1 leading-relaxed">{issue.description}</p>
                  </div>
                  
                  {issue.quickFix && (
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                      <Button 
                        variant="secondary" 
                        size="sm" 
                        className="h-7 text-[10px] px-2.5 bg-white/5 hover:bg-white/10"
                        onClick={(e) => handleQuickFix(issue, e)}
                      >
                        {issue.quickFix === 'open_config' ? (
                          <><Settings2 className="w-3 h-3 mr-1" /> Configure</>
                        ) : (
                          <><Trash2 className="w-3 h-3 mr-1 text-red-400" /> <span className="text-red-400">Delete</span></>
                        )}
                      </Button>
                    </div>
                  )}
                  
                  <div className="shrink-0 text-muted-foreground/30 group-hover:text-muted-foreground transition-colors mt-2 ml-2">
                    <ChevronRight className="w-4 h-4" />
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {validationIssues.length > 0 && (
          <div className="p-3 border-t border-white/5 bg-zinc-950/80 backdrop-blur-sm flex justify-between items-center">
            <span className="text-[10px] text-muted-foreground">Click an issue to locate it on the canvas.</span>
            <Button size="sm" className="h-7 text-[11px] px-4" onClick={handleFixNext}>
              Fix Next Issue
            </Button>
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  );
};
