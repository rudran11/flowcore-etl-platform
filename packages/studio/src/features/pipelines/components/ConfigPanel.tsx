import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, AlertTriangle, Puzzle, Play, CheckCircle2, Loader2, Activity } from 'lucide-react';
import Editor from '@monaco-editor/react';
import { usePipelineBuilderStore } from '../../../stores/pipelineBuilderStore';
import { Button } from '../../../components/ui/button';
import { useTheme } from 'next-themes';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../../../components/ui/tabs';
import { ScrollArea } from '../../../components/ui/scroll-area';
import { SchemaForm } from './SchemaForm';
import { PreviewPanel } from './PreviewPanel';
import { toast } from 'sonner';
import { pluginsApi } from '../../../api/plugins';

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
  
  const [activeTab, setActiveTab] = useState<'config' | 'docs' | 'schema' | 'json' | 'preview'>('config');
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [isFormValid, setIsFormValid] = useState(true);
  
  const [pluginMeta, setPluginMeta] = useState<any>(null);
  
  // Test connection state
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<{success: boolean, message?: string, latency?: number, timestamp?: Date} | null>(null);
  const isRunning = node?.data?.status === 'running';

  useEffect(() => {
    if (node) {
      if (node.type === 'triggerNode') {
        const triggerData = { 
          type: node.data.type || 'schedule', 
          schedule: node.data.schedule || '0 0 * * *',
          concurrency_policy: node.data.concurrency_policy || 'ALLOW'
        };
        setEditorValue(JSON.stringify(triggerData, null, 2));
        setFormData(triggerData);
        setPluginMeta({
           name: 'Pipeline Trigger',
           documentation: 'Configure how this pipeline is triggered and its concurrency behavior.',
           config_schema: {
             type: 'object',
             properties: {
               type: { type: 'string', enum: ['manual', 'schedule', 'webhook'] },
               schedule: { type: 'string', description: 'Cron expression for schedule type' },
               concurrency_policy: { type: 'string', enum: ['ALLOW', 'QUEUE', 'REJECT'], description: 'How to handle concurrent runs' }
             },
             required: ['type', 'concurrency_policy']
           }
        });
      } else {
        const configData = node.data.config || {};
        setEditorValue(JSON.stringify(configData, null, 2));
        setFormData(configData);
        
        // Fetch plugin metadata
        if (node.data.plugin_id) {
          pluginsApi.getPlugin(node.data.plugin_id as string).then(res => {
            setPluginMeta(res);
            
            // Auto-populate empty config with defaults from schema
            if (res.config_schema?.properties && (!configData || Object.keys(configData).length === 0)) {
              const defaults: Record<string, any> = {};
              for (const [k, prop] of Object.entries(res.config_schema.properties)) {
                if ((prop as any).default !== undefined) {
                  defaults[k] = (prop as any).default;
                }
              }
              setFormData(defaults);
              setEditorValue(JSON.stringify(defaults, null, 2));
            }
          }).catch(err => {
            console.error("Failed to load plugin metadata:", err);
          });
        }
      }
      setError(null);
      setTestResult(null);
      setHasUnsavedChanges(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [nodeId]); // Intentionally not depending on node to avoid overriding editor on node update

  if (!nodeId || !node) return null;

  const handleTestConnection = async () => {
    if (node.type === 'triggerNode' || !node.data.plugin_id) return;
    
    setIsTesting(true);
    setTestResult(null);
    try {
      const res = await pluginsApi.validatePlugin({
        plugin_id: node.data.plugin_id as string,
        config: formData
      });
      if (res.success) {
        setTestResult({ success: true, latency: 0, timestamp: new Date() });
        toast.success('Connection test successful!');
      } else {
        setTestResult({ success: false, message: res.errors?.[0] || 'Connection failed', timestamp: new Date() });
        toast.error('Connection test failed');
      }
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Unknown error';
      setTestResult({ success: false, message: msg, timestamp: new Date() });
      toast.error('Connection test failed');
    } finally {
      setIsTesting(false);
    }
  };

  const handleApply = () => {
    try {
      let parsed = activeTab === 'json' ? (JSON.parse(editorValue) || {}) : formData;
      
      // Merge defaults from schema if using the visual form
      if (activeTab === 'config' && pluginMeta?.config_schema?.properties) {
        const defaults: Record<string, any> = {};
        for (const [k, prop] of Object.entries(pluginMeta.config_schema.properties)) {
          if ((prop as any).default !== undefined) {
            defaults[k] = (prop as any).default;
          }
        }
        parsed = { ...defaults, ...parsed };
      }

      setError(null);
      
      setNodes(nodes.map(n => {
        if (n.id === nodeId) {
          if (n.type === 'triggerNode') {
            return { ...n, data: { ...n.data, type: parsed.type, schedule: parsed.schedule, concurrency_policy: parsed.concurrency_policy, error: false } };
          } else {
            let hasError = false;
            if (pluginMeta?.config_schema?.required) {
              hasError = pluginMeta.config_schema.required.some((key: string) => !parsed[key]);
            }
            return { ...n, data: { ...n.data, config: parsed, error: hasError } };
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
    setFormData(prev => {
      const next = { ...prev, [key]: value };
      setEditorValue(JSON.stringify(next, null, 2));
      return next;
    });
    setHasUnsavedChanges(true);
  };
  
  const handleYamlChange = (val: string | undefined) => {
    setEditorValue(val || '');
    try {
      const parsed = JSON.parse(val || '{}');
      setFormData(parsed);
      setError(null);
    } catch (e) {
      // Ignore parse errors while typing
    }
    setHasUnsavedChanges(true);
  };

  // Removed getMaskedJson as it corrupts data on edit

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
      </div>

      <div className="flex-1 overflow-hidden flex flex-col relative bg-zinc-950/50">
        <Tabs value={activeTab} onValueChange={(v: any) => setActiveTab(v)} className="flex-1 flex flex-col h-full overflow-hidden">
          <div className="px-4 py-2 border-b border-white/5 bg-zinc-950/80 sticky top-0 z-10 backdrop-blur-md">
              <TabsList className="grid w-full grid-cols-5 bg-zinc-900 border border-white/10 p-1 h-9">
                <TabsTrigger value="config" className="text-[11px] data-[state=active]:bg-primary/20 data-[state=active]:text-primary rounded-sm h-7">Config</TabsTrigger>
                <TabsTrigger value="preview" className="text-[11px] data-[state=active]:bg-primary/20 data-[state=active]:text-primary rounded-sm h-7">Preview</TabsTrigger>
                <TabsTrigger value="docs" className="text-[11px] data-[state=active]:bg-primary/20 data-[state=active]:text-primary rounded-sm h-7">Docs</TabsTrigger>
                <TabsTrigger value="schema" className="text-[11px] data-[state=active]:bg-primary/20 data-[state=active]:text-primary rounded-sm h-7">Schema</TabsTrigger>
                <TabsTrigger value="json" className="text-[11px] data-[state=active]:bg-primary/20 data-[state=active]:text-primary rounded-sm h-7">JSON</TabsTrigger>
              </TabsList>
            </div>
            
            <div className="flex-1 overflow-hidden relative">
              <TabsContent value="config" className="h-full m-0 data-[state=inactive]:hidden flex flex-col">
                <ScrollArea className="flex-1">
                  <div className="pb-6">
                    <SchemaForm 
                      schema={pluginMeta?.config_schema} 
                      formData={formData} 
                      onChange={handleFormChange} 
                      setIsValid={setIsFormValid}
                    />
                    
                    {node.type !== 'triggerNode' && (
                      <div className="px-4 pt-2 pb-4 mb-4 border-t border-white/5 mx-4 mt-2">
                        <Button 
                          variant="outline" 
                          className="w-full bg-zinc-900 border-white/10 hover:bg-zinc-800 hover:text-white"
                          onClick={handleTestConnection}
                          disabled={isTesting || !isFormValid}
                        >
                          {isTesting ? (
                            <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Testing...</>
                          ) : (
                            <><Activity className="w-4 h-4 mr-2" /> Test Connection</>
                          )}
                        </Button>
                        
                        {testResult && (
                          <div className={`mt-3 p-3 rounded-md border text-sm flex flex-col gap-1 ${
                            testResult.success 
                              ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' 
                              : 'bg-red-500/10 border-red-500/20 text-red-400'
                          }`}>
                            <div className="flex items-center gap-2 font-medium">
                              {testResult.success ? <CheckCircle2 className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
                              {testResult.success ? 'Connection Successful' : 'Connection Failed'}
                            </div>
                            {testResult.message && (
                              <p className="text-xs opacity-80 mt-1">{testResult.message}</p>
                            )}
                            <div className="flex justify-between items-center mt-1 text-[10px] opacity-60">
                              <span>Tested: Just now</span>
                              {testResult.latency !== undefined && <span>{testResult.latency} ms</span>}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </ScrollArea>
              </TabsContent>

              <TabsContent value="preview" className="h-full m-0 data-[state=inactive]:hidden flex flex-col">
                <PreviewPanel nodeId={nodeId} isActive={activeTab === 'preview'} />
              </TabsContent>

              <TabsContent value="docs" className="h-full m-0 data-[state=inactive]:hidden p-4">
                <ScrollArea className="h-full pr-4">
                  <div className="prose prose-invert prose-sm max-w-none">
                    {pluginMeta?.documentation ? (
                      <div dangerouslySetInnerHTML={{ __html: pluginMeta.documentation.replace(/\n/g, '<br/>') }} />
                    ) : (
                      <p className="text-muted-foreground">No documentation available for this connector.</p>
                    )}
                  </div>
                </ScrollArea>
              </TabsContent>
              
              <TabsContent value="schema" className="h-full m-0 data-[state=inactive]:hidden relative">
                 <Editor
                    height="100%"
                    language="json"
                    theme={isDark ? "vs-dark" : "light"}
                    value={pluginMeta?.config_schema ? JSON.stringify(pluginMeta.config_schema, null, 2) : '{}'}
                    options={{ minimap: { enabled: false }, fontSize: 12, wordWrap: 'on', padding: { top: 16 }, readOnly: true }}
                 />
              </TabsContent>

              <TabsContent value="json" className="h-full m-0 data-[state=inactive]:hidden relative">
                 <Editor
                    height="100%"
                    language="json"
                    theme={isDark ? "vs-dark" : "light"}
                    value={editorValue}
                    onChange={handleYamlChange}
                    options={{ minimap: { enabled: false }, fontSize: 12, wordWrap: 'on', padding: { top: 16 } }}
                 />
            </TabsContent>
          </div>
        </Tabs>
      </div>

      <div className="border-t border-border/50 p-4 bg-background/80 backdrop-blur-sm shrink-0 sticky bottom-0 z-10 shadow-[0_-4px_12px_rgba(0,0,0,0.1)]">
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 10, height: 0 }}
              animate={{ opacity: 1, y: 0, height: 'auto' }}
              exit={{ opacity: 0, y: 10, height: 0 }}
              className="mb-4 text-[12px] bg-red-500/10 text-red-500 p-3 rounded-md flex gap-2 items-start border border-red-500/20"
            >
              <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
              <div className="font-medium leading-relaxed">{error}</div>
            </motion.div>
          )}
        </AnimatePresence>
        <div className="flex gap-2">
          <Button variant="outline" className="flex-1 h-9 text-xs font-medium" onClick={onClose}>
            Cancel
          </Button>
          <Button 
            className="flex-1 h-9 text-xs font-medium bg-primary text-primary-foreground hover:bg-primary/90"
            onClick={handleApply}
            disabled={isRunning || (activeTab === 'config' && !isFormValid) || (activeTab === 'config' && !hasUnsavedChanges && !error && Object.keys(node?.data?.config || {}).length > 0)}
          >
            {hasUnsavedChanges || Object.keys(node?.data?.config || {}).length === 0 ? 'Apply Changes' : 'Applied'}
          </Button>
        </div>
      </div>
    </motion.div>
  );
};
