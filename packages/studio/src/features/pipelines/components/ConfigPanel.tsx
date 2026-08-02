import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, AlertTriangle, Puzzle, Play } from 'lucide-react';
import Editor from '@monaco-editor/react';
import yaml from 'yaml';
import { usePipelineBuilderStore } from '../../../stores/pipelineBuilderStore';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { useTheme } from 'next-themes';

interface ConfigPanelProps {
  nodeId: string | null;
  onClose: () => void;
}

export const ConfigPanel: React.FC<ConfigPanelProps> = ({ nodeId, onClose }) => {
  const { nodes, setNodes, syncToYaml } = usePipelineBuilderStore();
  
  const [editorValue, setEditorValue] = useState('');
  const [error, setError] = useState<string | null>(null);

  const node = nodes.find(n => n.id === nodeId);
  const { theme } = useTheme();
  const isDark = theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
  
  const [activeTab, setActiveTab] = useState<'form' | 'yaml' | 'docs'>('form');
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const isRunning = node?.data?.status === 'running';

  useEffect(() => {
    if (node) {
      if (node.type === 'triggerNode') {
        const triggerData = { type: node.data.type || 'schedule', schedule: node.data.schedule || '0 0 * * *' };
        setEditorValue(yaml.stringify(triggerData));
        setFormData(triggerData);
      } else {
        const configData = node.data.config || {};
        setEditorValue(yaml.stringify(configData));
        setFormData(configData);
      }
      setError(null);
      setHasUnsavedChanges(false);
    }
  }, [nodeId]); // Intentionally not depending on node to avoid overriding editor on node update

  if (!nodeId || !node) return null;

  const handleApply = () => {
    try {
      const parsed = activeTab === 'yaml' ? (yaml.parse(editorValue) || {}) : formData;
      setError(null);
      
      setNodes(nodes.map(n => {
        if (n.id === nodeId) {
          if (n.type === 'triggerNode') {
            return { ...n, data: { ...n.data, type: parsed.type, schedule: parsed.schedule, error: false } };
          } else {
            return { ...n, data: { ...n.data, config: parsed, error: Object.keys(parsed).length === 0 } };
          }
        }
        return n;
      }));
      
      syncToYaml();
      setHasUnsavedChanges(false);
      onClose();
    } catch (e: any) {
      setError(e.message);
    }
  };

  const handleFormChange = (key: string, value: string) => {
    setFormData(prev => ({ ...prev, [key]: value }));
    setHasUnsavedChanges(true);
  };
  
  const handleYamlChange = (val: string | undefined) => {
    setEditorValue(val || '');
    setHasUnsavedChanges(true);
  };

  return (
    <motion.div
      initial={{ x: '100%' }}
      animate={{ x: 0 }}
      exit={{ x: '100%' }}
      transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      className="absolute top-0 right-0 bottom-0 w-[400px] bg-card border-l border-border/50 shadow-2xl flex flex-col z-20"
    >
      <div className="flex flex-col border-b border-border/50 bg-background/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="flex items-center justify-between p-4 pb-2">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center">
              {node.type === 'triggerNode' ? <Play className="w-4 h-4 text-primary" /> : <Puzzle className="w-4 h-4 text-primary" />}
            </div>
            <div>
              <h3 className="font-semibold text-foreground leading-tight">{String(node.data.label || nodeId)}</h3>
              <p className="text-[11px] text-muted-foreground">{node.type === 'triggerNode' ? 'Pipeline Trigger' : String(node.data.plugin_id || 'Unknown Plugin')}</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8 text-muted-foreground hover:text-foreground rounded-full">
            <X className="w-4 h-4" />
          </Button>
        </div>
        
        <div className="flex px-4 gap-4 mt-2">
          <button 
            className={`text-xs font-semibold pb-2 border-b-2 transition-colors ${activeTab === 'form' ? 'border-primary text-foreground' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
            onClick={() => setActiveTab('form')}
          >
            Form
          </button>
          <button 
            className={`text-xs font-semibold pb-2 border-b-2 transition-colors ${activeTab === 'yaml' ? 'border-primary text-foreground' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
            onClick={() => setActiveTab('yaml')}
          >
            YAML
          </button>
          <button 
            className={`text-xs font-semibold pb-2 border-b-2 transition-colors ${activeTab === 'docs' ? 'border-primary text-foreground' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
            onClick={() => setActiveTab('docs')}
          >
            Docs
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar relative">
        {isRunning && (
          <div className="absolute inset-0 bg-background/50 backdrop-blur-[1px] z-10 flex flex-col items-center justify-center p-6 text-center">
            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-3">
              <Play className="w-5 h-5 text-primary" />
            </div>
            <h4 className="text-sm font-semibold text-foreground mb-1">Pipeline is Running</h4>
            <p className="text-xs text-muted-foreground">Configuration is read-only during execution.</p>
          </div>
        )}

        {activeTab === 'form' && (
          <div className="p-4 flex flex-col gap-4">
            {Object.keys(formData).length === 0 ? (
              <div className="text-center text-sm text-muted-foreground p-8 bg-accent/30 rounded-xl border border-border/50">
                No configuration fields defined. Try using the YAML editor.
              </div>
            ) : (
              Object.entries(formData).map(([key, value]) => (
                <div key={key} className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">{key}</label>
                  <Input 
                    value={String(value)}
                    onChange={(e) => handleFormChange(key, e.target.value)}
                    className="h-9 bg-accent/50 border-border/50 shadow-sm focus-visible:ring-primary/20"
                    disabled={isRunning}
                  />
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'yaml' && (
          <div className="h-full">
            <Editor
              height="100%"
              defaultLanguage="yaml"
              theme={isDark ? "vs-dark" : "light"}
              value={editorValue}
              onChange={handleYamlChange}
              options={{
                minimap: { enabled: false },
                fontSize: 13,
                wordWrap: 'on',
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
                padding: { top: 16 },
                readOnly: isRunning,
              }}
            />
          </div>
        )}

        {activeTab === 'docs' && (
          <div className="p-6 text-center">
            <div className="w-16 h-16 bg-accent rounded-2xl mx-auto flex items-center justify-center mb-4 border border-border/50">
              <Puzzle className="w-8 h-8 text-muted-foreground" />
            </div>
            <h4 className="font-semibold text-foreground mb-2">Connector Documentation</h4>
            <p className="text-xs text-muted-foreground">Documentation for {node.data.plugin_id} will be available here when the backend API is connected.</p>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-border/50 bg-background/50 backdrop-blur-sm flex items-center justify-between sticky bottom-0">
        {hasUnsavedChanges ? (
          <span className="text-[11px] font-medium text-amber-500 flex items-center gap-1.5"><AlertTriangle className="w-3.5 h-3.5"/> Unsaved changes</span>
        ) : (
          <span className="text-[11px] font-medium text-muted-foreground">All changes saved</span>
        )}
        
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={onClose} className="h-8 text-xs px-3 border-border/50 shadow-sm" disabled={isRunning}>Cancel</Button>
          <Button size="sm" onClick={handleApply} className="h-8 text-xs px-4 shadow-sm" disabled={!hasUnsavedChanges || isRunning}>Save Changes</Button>
        </div>
      </div>

      <AnimatePresence>
        {error && (
          <motion.div 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 20, opacity: 0 }}
            className="absolute bottom-16 left-4 right-4 bg-destructive/10 border border-destructive/20 rounded-lg p-3 flex gap-2 items-start shadow-sm backdrop-blur-md"
          >
            <AlertTriangle className="w-4 h-4 text-destructive shrink-0 mt-0.5" />
            <div className="text-xs text-destructive font-mono break-all">{error}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};
