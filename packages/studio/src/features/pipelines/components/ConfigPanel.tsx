import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, AlertTriangle } from 'lucide-react';
import Editor from '@monaco-editor/react';
import yaml from 'yaml';
import { usePipelineBuilderStore } from '../../../stores/pipelineBuilderStore';
import { Button } from '../../../components/ui/button';

interface ConfigPanelProps {
  nodeId: string | null;
  onClose: () => void;
}

export const ConfigPanel: React.FC<ConfigPanelProps> = ({ nodeId, onClose }) => {
  const { nodes, setNodes, syncToYaml } = usePipelineBuilderStore();
  
  const [editorValue, setEditorValue] = useState('');
  const [error, setError] = useState<string | null>(null);

  const node = nodes.find(n => n.id === nodeId);

  useEffect(() => {
    if (node) {
      if (node.type === 'triggerNode') {
        const triggerData = { type: node.data.type, schedule: node.data.schedule };
        setEditorValue(yaml.stringify(triggerData));
      } else {
        setEditorValue(yaml.stringify(node.data.config || {}));
      }
      setError(null);
    }
  }, [nodeId]); // Intentionally not depending on node to avoid overriding editor on node update

  if (!nodeId || !node) return null;

  const handleApply = () => {
    try {
      const parsed = yaml.parse(editorValue) || {};
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
      onClose();
    } catch (e: any) {
      setError(e.message);
    }
  };

  return (
    <motion.div
      initial={{ x: 400, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 400, opacity: 0 }}
      transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      className="absolute top-4 right-4 bottom-4 w-96 bg-zinc-950/90 border border-white/10 rounded-xl shadow-2xl backdrop-blur-xl flex flex-col overflow-hidden z-10"
    >
      <div className="flex items-center justify-between p-4 border-b border-white/5 bg-white/5">
        <div>
          <h3 className="font-semibold text-white">Configure Node</h3>
          <p className="text-xs text-zinc-400">{String(node.data.label || nodeId)}</p>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8 text-zinc-400 hover:text-white">
          <X className="w-4 h-4" />
        </Button>
      </div>

      <div className="flex-1 relative">
        <Editor
          height="100%"
          defaultLanguage="yaml"
          theme="vs-dark"
          value={editorValue}
          onChange={(val) => setEditorValue(val || '')}
          options={{
            minimap: { enabled: false },
            fontSize: 13,
            wordWrap: 'on',
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            padding: { top: 16 },
          }}
        />
      </div>

      <div className="p-4 border-t border-white/5 bg-zinc-900 flex justify-end gap-2">
        <Button variant="ghost" onClick={onClose}>Cancel</Button>
        <Button onClick={handleApply}>Apply Configuration</Button>
      </div>

      <AnimatePresence>
        {error && (
          <motion.div 
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="bg-rose-500/10 border-t border-rose-500/20 p-3 flex gap-2 items-start"
          >
            <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
            <div className="text-xs text-rose-400 font-mono break-all">{error}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};
