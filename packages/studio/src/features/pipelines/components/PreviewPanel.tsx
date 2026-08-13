import React, { useState } from 'react';
import { usePipelineBuilderStore } from '../../../stores/pipelineBuilderStore';
import { pipelinesApi } from '../../../api/pipelines';
import { Button } from '../../../components/ui/button';
import { Loader2, Play, AlertTriangle, ArrowRight, Table as TableIcon } from 'lucide-react';
import { ScrollArea } from '../../../components/ui/scroll-area';

interface PreviewPanelProps {
  nodeId: string;
  isActive: boolean;
}

export const PreviewPanel: React.FC<PreviewPanelProps> = ({ nodeId, isActive }) => {
  const { nodes, edges } = usePipelineBuilderStore();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePreview = async () => {
    try {
      setLoading(true);
      setError(null);
      setResult(null);

      const pipelineDef = {
        name: "Preview",
        version_tag: "v-preview",
        steps: nodes.map(n => ({
          step_id: n.id,
          plugin_id: n.data.plugin_id || (n.type === 'triggerNode' ? 'test-source' : ''), // Fallback for trigger
          depends_on: edges.filter(e => e.target === n.id).map(e => e.source),
          parameters: n.data.config || {},
          retry_policy: { max_attempts: 0 }
        })).filter(s => s.plugin_id), // Skip nodes without plugin ID
        dsl_definition: {},
        graph_definition: {}
      };

      const res = await pipelinesApi.previewPipeline({
        pipeline: pipelineDef,
        preview_node_id: nodeId,
        limit: 50
      });

      if (res.success) {
        setResult(res);
      } else {
        setError(res.error_message || "Preview failed");
      }
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred during preview");
    } finally {
      setLoading(false);
    }
  };

  if (!isActive) return null;

  return (
    <div className="flex flex-col h-full bg-zinc-950 text-zinc-300 text-sm">
      <div className="p-4 border-b border-white/10 flex justify-between items-center">
        <div>
          <h4 className="font-medium text-white flex items-center gap-2">
            <TableIcon className="w-4 h-4 text-primary" /> Data Preview
          </h4>
          <p className="text-xs text-zinc-500 mt-1">Preview up to 50 records up to this node.</p>
        </div>
        <Button 
          size="sm" 
          onClick={handlePreview} 
          disabled={loading}
          className="bg-primary hover:bg-primary/90 text-primary-foreground text-xs h-8"
        >
          {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
          Run Preview
        </Button>
      </div>

      <ScrollArea className="flex-1 p-4">
        {error && (
          <div className="mb-4 bg-red-500/10 text-red-500 p-3 rounded-md flex gap-2 items-start border border-red-500/20 text-xs">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
            <div className="whitespace-pre-wrap">{error}</div>
          </div>
        )}

        {!result && !loading && !error && (
          <div className="flex flex-col items-center justify-center h-48 text-zinc-600">
            <Play className="w-8 h-8 mb-2 opacity-50" />
            <p>Click "Run Preview" to execute the pipeline up to this node.</p>
          </div>
        )}

        {loading && (
          <div className="flex flex-col items-center justify-center h-48 text-primary">
            <Loader2 className="w-8 h-8 mb-2 animate-spin" />
            <p className="text-xs text-zinc-400">Executing partial DAG...</p>
          </div>
        )}

        {result && (
          <div className="space-y-6">
            {/* Metrics */}
            {Object.keys(result.metrics || {}).length > 0 && (
              <div className="bg-zinc-900/50 rounded-md border border-white/5 p-3">
                <h5 className="text-xs font-semibold text-zinc-400 mb-2 uppercase tracking-wider">Metrics</h5>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(result.metrics).map(([k, v]) => (
                    <div key={k} className="flex flex-col">
                      <span className="text-[10px] text-zinc-500">{k}</span>
                      <span className="text-sm text-white font-medium">{String(v)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Input vs Output Records */}
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col border border-white/10 rounded-md overflow-hidden bg-zinc-900/30">
                <div className="bg-zinc-900 p-2 text-xs font-medium border-b border-white/5 text-zinc-400 flex justify-between">
                  <span>Input Records</span>
                  <span className="text-zinc-500">{result.input_records?.length || 0}</span>
                </div>
                <div className="p-3 text-xs font-mono overflow-auto max-h-64 whitespace-pre-wrap">
                  {result.input_records && result.input_records.length > 0 
                    ? JSON.stringify(result.input_records.slice(0, 5), null, 2)
                    : <span className="text-zinc-600">No input records</span>}
                  {result.input_records?.length > 5 && (
                    <div className="text-zinc-500 mt-2 italic">... {result.input_records.length - 5} more records</div>
                  )}
                </div>
              </div>

              <div className="flex flex-col border border-white/10 rounded-md overflow-hidden bg-zinc-900/30 relative">
                <div className="absolute left-[-10px] top-1/2 transform -translate-y-1/2 bg-zinc-800 rounded-full p-1 border border-white/10 z-10">
                  <ArrowRight className="w-3 h-3 text-primary" />
                </div>
                <div className="bg-zinc-900 p-2 text-xs font-medium border-b border-white/5 text-primary flex justify-between">
                  <span>Output Records</span>
                  <span className="text-primary/70">{result.output_records?.length || 0}</span>
                </div>
                <div className="p-3 text-xs font-mono overflow-auto max-h-64 whitespace-pre-wrap">
                  {result.output_records && result.output_records.length > 0 
                    ? JSON.stringify(result.output_records.slice(0, 5), null, 2)
                    : <span className="text-zinc-600">No output records</span>}
                  {result.output_records?.length > 5 && (
                    <div className="text-zinc-500 mt-2 italic">... {result.output_records.length - 5} more records</div>
                  )}
                </div>
              </div>
            </div>

            {/* Transformation Errors */}
            {result.errors && result.errors.length > 0 && (
              <div className="bg-orange-500/10 border border-orange-500/20 rounded-md p-3">
                <h5 className="text-xs font-semibold text-orange-500 mb-2 uppercase tracking-wider flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3" /> Data Errors
                </h5>
                <ul className="list-disc pl-4 text-xs text-orange-400/80 space-y-1">
                  {result.errors.map((e: string, i: number) => (
                    <li key={i}>{e}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </ScrollArea>
    </div>
  );
};
