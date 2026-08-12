import React, { useCallback, useEffect, useRef, useState } from 'react';
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
import { ValidationPanel } from './ValidationPanel';
import { ExecutionMonitorPanel } from './ExecutionMonitorPanel';
import { CanvasEmptyState } from './CanvasEmptyState';
import { AnimatedEdge } from './AnimatedEdge';
import { useTheme } from 'next-themes';

const nodeTypes = {
  triggerNode: TriggerNode,
  stepNode: StepNode,
};

const edgeTypes = {
  animated: AnimatedEdge,
};

const PipelineCanvasInner: React.FC = () => {
  const { 
    nodes, edges, 
    onNodesChange, onEdgesChange, onConnect,
    setNodes,
    saveHistory,
    syncToYaml,
    autoLayout,
    deleteSelected, duplicateSelected, pasteClipboard,
    validatePipeline
  } = usePipelineBuilderStore();
  
  const reactFlowInstance = useReactFlow();
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const { theme } = useTheme();
  const isDark = theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
  
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  
  // Context Menu State
  const [contextMenu, setContextMenu] = useState<{
    show: boolean;
    x: number;
    y: number;
    type: 'pane' | 'node';
    nodeId?: string;
  }>({ show: false, x: 0, y: 0, type: 'pane' });

  // Close context menu on any click outside
  useEffect(() => {
    const handleClick = () => setContextMenu({ ...contextMenu, show: false });
    document.addEventListener('click', handleClick);
    return () => document.removeEventListener('click', handleClick);
  }, [contextMenu]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger if user is typing in an input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement || e.target instanceof HTMLDivElement && e.target.isContentEditable) {
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key === 'c') {
        const selected = nodes.filter(n => n.selected);
        if (selected.length > 0) {
          usePipelineBuilderStore.getState().copySelected();
        }
      } else if ((e.ctrlKey || e.metaKey) && e.key === 'v') {
        usePipelineBuilderStore.getState().pasteClipboard();
      } else if (e.key === 'Delete' || e.key === 'Backspace') {
        // React Flow handles deletion natively if elements are selected, 
        // but we'll call our store method to ensure state sync.
        usePipelineBuilderStore.getState().deleteSelected();
      } else if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
        e.preventDefault();
        setNodes(nodes.map(n => ({ ...n, selected: true })));
      } else if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        usePipelineBuilderStore.getState().duplicateSelected();
      } else if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'v') {
        e.preventDefault();
        validatePipeline();
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [nodes, setNodes]);

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

  const onPaneContextMenu = useCallback((event: React.MouseEvent | MouseEvent) => {
    event.preventDefault();
    setContextMenu({ show: true, x: event.clientX, y: event.clientY, type: 'pane' });
  }, []);

  const onNodeContextMenu = useCallback((event: React.MouseEvent | MouseEvent, node: any) => {
    event.preventDefault();
    setSelectedNodeId(node.id);
    setNodes(nodes.map(n => ({ ...n, selected: n.id === node.id })));
    setContextMenu({ show: true, x: event.clientX, y: event.clientY, type: 'node', nodeId: node.id });
  }, [nodes, setNodes]);

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden relative" ref={reactFlowWrapper}>
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
            edgeTypes={edgeTypes}
            defaultEdgeOptions={{ type: 'animated' }}
            onDragOver={onDragOver}
            onDrop={onDrop}
            onNodeClick={(_, node) => setSelectedNodeId(node.id)}
            onPaneClick={() => { setSelectedNodeId(null); setContextMenu({ ...contextMenu, show: false }); }}
            onPaneContextMenu={onPaneContextMenu}
            onNodeContextMenu={onNodeContextMenu}
            fitView
            className="bg-background"
            colorMode={isDark ? "dark" : "light"}
          >
            <Background color={isDark ? "#ffffff" : "#000000"} gap={24} size={1.5} variant={BackgroundVariant.Dots} className={isDark ? "opacity-5" : "opacity-[0.03]"} />
            
            <Controls 
              className="bg-card/80 backdrop-blur-md border-border/50 shadow-sm rounded-md overflow-hidden fill-foreground !flex !flex-col" 
              showInteractive={false}
            />
            
            <MiniMap 
              nodeColor={(n) => {
                if (n.type === 'triggerNode') return isDark ? '#10b981' : '#059669';
                if (n.data?.error) return isDark ? '#f43f5e' : '#e11d48';
                return isDark ? '#a1a1aa' : '#71717a';
              }}
              maskColor={isDark ? "rgba(0, 0, 0, 0.7)" : "rgba(255, 255, 255, 0.7)"}
              className="bg-card/80 backdrop-blur-md border border-border/50 shadow-sm rounded-md overflow-hidden"
              style={{ width: 150, height: 100 }}
              pannable
              zoomable
            />
            
            {nodes.length === 0 && <CanvasEmptyState />}
          </ReactFlow>

          {contextMenu.show && (
            <div 
              className="fixed z-50 bg-card border border-border/50 shadow-xl rounded-xl py-1.5 w-48 text-sm text-foreground backdrop-blur-xl"
              style={{ top: contextMenu.y, left: contextMenu.x }}
              onClick={(e) => e.stopPropagation()}
            >
              {contextMenu.type === 'node' && (
                <>
                  <button className="w-full text-left px-3 py-1.5 hover:bg-accent hover:text-foreground transition-colors flex items-center gap-2" onClick={() => { duplicateSelected(); setContextMenu({ ...contextMenu, show: false }); }}>
                    <span>Duplicate</span>
                    <span className="text-[10px] text-muted-foreground ml-auto border border-border/50 px-1 rounded bg-background">Ctrl D</span>
                  </button>
                  <button className="w-full text-left px-3 py-1.5 hover:bg-destructive/10 hover:text-destructive transition-colors text-destructive flex items-center gap-2" onClick={() => { deleteSelected(); setContextMenu({ ...contextMenu, show: false }); }}>
                    <span>Delete</span>
                    <span className="text-[10px] text-muted-foreground ml-auto border border-border/50 px-1 rounded bg-background">Del</span>
                  </button>
                </>
              )}
              {contextMenu.type === 'pane' && (
                <>
                  <button className="w-full text-left px-3 py-1.5 hover:bg-accent hover:text-foreground transition-colors flex items-center gap-2" onClick={() => { pasteClipboard(); setContextMenu({ ...contextMenu, show: false }); }}>
                    <span>Paste</span>
                    <span className="text-[10px] text-muted-foreground ml-auto border border-border/50 px-1 rounded bg-background">Ctrl V</span>
                  </button>
                  <button className="w-full text-left px-3 py-1.5 hover:bg-accent hover:text-foreground transition-colors flex items-center gap-2" onClick={() => { autoLayout('TB'); setContextMenu({ ...contextMenu, show: false }); }}>
                    <span>Auto Layout</span>
                  </button>
                </>
              )}
            </div>
          )}

          <ValidationPanel />
          <ExecutionMonitorPanel />

          {selectedNodeId && (
            <ConfigPanel 
              nodeId={selectedNodeId} 
              onClose={() => {
                setSelectedNodeId(null);
                const currentNodes = usePipelineBuilderStore.getState().nodes;
                setNodes(currentNodes.map(n => ({ ...n, selected: false })));
              }} 
            />
          )}

          {/* Context Menu */}
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
