import React, { useCallback, useRef, useState } from 'react';
import { 
  ReactFlow, 
  Background, 
  Controls, 
  MiniMap, 
  useReactFlow,
  ReactFlowProvider,
  BackgroundVariant
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { usePipelineBuilderStore } from '../../../stores/pipelineBuilderStore';
import { TriggerNode, StepNode } from './CustomNodes';
import { PluginPalette } from './PluginPalette';
import { BuilderToolbar } from './BuilderToolbar';
import { ConfigPanel } from './ConfigPanel';

const nodeTypes = {
  triggerNode: TriggerNode,
  stepNode: StepNode,
};

const PipelineCanvasInner: React.FC = () => {
  const { 
    nodes, edges, 
    onNodesChange, onEdgesChange, onConnect,
    setNodes,
    saveHistory,
    syncToYaml
  } = usePipelineBuilderStore();
  
  const reactFlowInstance = useReactFlow();
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      
      const draggedData = event.dataTransfer.getData('application/reactflow');
      if (!draggedData) return;
      
      let pluginId = draggedData;
      let config = {};
      
      try {
        const parsed = JSON.parse(draggedData);
        if (parsed.type) {
          pluginId = parsed.plugin_id;
          if (parsed.config) config = parsed.config;
        }
      } catch (e) {
        // Fallback for old simple string drag data
      }
      
      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const newNodeId = `step-${Math.random().toString(36).substr(2, 9)}`;
      
      const newNode = {
        id: newNodeId,
        type: 'stepNode',
        position,
        data: { label: pluginId, plugin_id: pluginId, config },
      };
      
      setNodes([...nodes, newNode]);
      saveHistory();
      syncToYaml();
    },
    [reactFlowInstance, nodes, setNodes, saveHistory, syncToYaml]
  );

  return (
    <div className="flex-1 flex flex-col bg-zinc-950 overflow-hidden relative" ref={reactFlowWrapper}>
      <BuilderToolbar />
      <div className="flex-1 flex overflow-hidden">
        <PluginPalette />
        
        <div className="flex-1 relative">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            onDragOver={onDragOver}
            onDrop={onDrop}
            onNodeClick={(_, node) => setSelectedNodeId(node.id)}
            onPaneClick={() => setSelectedNodeId(null)}
            fitView
            className="bg-zinc-950"
            colorMode="dark"
          >
            <Background color="#ffffff" gap={20} size={1} variant={BackgroundVariant.Dots} className="opacity-5" />
            <Controls className="bg-zinc-900 border-white/10 fill-white" />
            <MiniMap 
              nodeColor={(n) => {
                if (n.type === 'triggerNode') return '#10b981';
                if (n.data?.error) return '#f43f5e';
                return '#a1a1aa';
              }}
              maskColor="rgba(0, 0, 0, 0.5)"
              className="bg-zinc-950 border-white/10"
            />
          </ReactFlow>

          {selectedNodeId && (
            <ConfigPanel 
              nodeId={selectedNodeId} 
              onClose={() => setSelectedNodeId(null)} 
            />
          )}
        </div>
      </div>
    </div>
  );
};

export const PipelineCanvas: React.FC = () => (
  <ReactFlowProvider>
    <PipelineCanvasInner />
  </ReactFlowProvider>
);
