import React, { useMemo, useEffect } from 'react';
import { ReactFlow, MiniMap, Controls, Background, useNodesState, useEdgesState, BackgroundVariant } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { ExecutionResponse } from '../../../api/executions';
import { usePipeline } from '../../pipelines/hooks/usePipeline';
import dagre from 'dagre';
import { TriggerNode, StepNode } from '../../pipelines/components/CustomNodes';
import { AnimatedEdge } from '../../pipelines/components/AnimatedEdge';
import { useTheme } from 'next-themes';
import { NodeInspectionPanel } from './NodeInspectionPanel';

interface ExecutionDAGProps {
  run: ExecutionResponse;
}

const nodeTypes = {
  triggerNode: TriggerNode,
  stepNode: StepNode,
};

const edgeTypes = {
  animated: AnimatedEdge,
};

export const ExecutionDAG: React.FC<ExecutionDAGProps> = ({ run }) => {
  const { data: pipeline } = usePipeline(run.pipeline_id);

  const currentVersion = useMemo(() => {
    return pipeline?.versions?.find(v => v.id === run.pipeline_version) || pipeline?.versions?.[0];
  }, [pipeline, run.pipeline_version]);

  const [nodes, setNodes, onNodesChange] = useNodesState<any>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<any>([]);
  const [selectedNodeId, setSelectedNodeId] = React.useState<string | null>(null);

  const { theme } = useTheme();
  const isDark = theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);

  useEffect(() => {
    if (!currentVersion?.dsl_definition) {
      setNodes([]);
      setEdges([]);
      return;
    }
    
    const dsl = currentVersion.dsl_definition;
    const triggerData = dsl.trigger || { type: 'manual' };
    
    let newNodes: any[] = [];
    let newEdges: any[] = [];

    // Add Trigger Node
    newNodes.push({
      id: 'trigger',
      type: 'triggerNode',
      position: { x: 0, y: 0 },
      data: { 
        label: 'Trigger', 
        type: triggerData.type, 
        schedule: triggerData.schedule,
        status: run.status.toLowerCase(), // mapping to custom nodes status format
      }
    });

    if (dsl.steps) {
      Object.entries(dsl.steps).forEach(([stepId, step]: [string, any]) => {
        const stepRun = run.steps?.[stepId];
        const status = stepRun?.status?.toLowerCase() || 'pending';
        
        newNodes.push({
          id: stepId,
          type: 'stepNode',
          position: { x: 0, y: 0 },
          data: { 
            label: stepId, 
            plugin_id: step.plugin_id, 
            config: step.config,
            status: status,
            duration: stepRun?.duration_ms ? `${(stepRun.duration_ms / 1000).toFixed(1)}s` : undefined,
            error: stepRun?.error_message ? true : false,
          }
        });
        
        if (step.depends_on && step.depends_on.length > 0) {
          step.depends_on.forEach((dep: string) => {
            if (dep === 'trigger' || dep === 'Trigger') {
              newEdges.push({
                id: `e-trigger-${stepId}`,
                source: 'trigger',
                target: stepId,
                type: 'animated',
                data: { status: status }
              });
            } else {
              newEdges.push({
                id: `e-${dep}-${stepId}`,
                source: dep,
                target: stepId,
                type: 'animated',
                data: { status: status }
              });
            }
          });
        } else {
          newEdges.push({
            id: `e-trigger-${stepId}`,
            source: 'trigger',
            target: stepId,
            type: 'animated',
            data: { status: status }
          });
        }
      });
    }

    // Auto Layout with Dagre
    const dagreGraph = new dagre.graphlib.Graph();
    dagreGraph.setDefaultEdgeLabel(() => ({}));
    dagreGraph.setGraph({ rankdir: 'TB', ranksep: 100, nodesep: 100 });
    
    newNodes.forEach((node) => {
      dagreGraph.setNode(node.id, { width: 250, height: 80 });
    });
    newEdges.forEach((edge) => {
      dagreGraph.setEdge(edge.source, edge.target);
    });
    dagre.layout(dagreGraph);
    
    newNodes = newNodes.map((node) => {
      const nodeWithPosition = dagreGraph.node(node.id);
      return {
        ...node,
        position: {
          x: nodeWithPosition.x - 250 / 2,
          y: nodeWithPosition.y - 80 / 2,
        },
      };
    });

    setNodes(newNodes);
    setEdges(newEdges);
  }, [currentVersion, run, setNodes, setEdges]);

  if (!pipeline) {
    return <div className="h-full flex items-center justify-center text-muted-foreground">Loading DAG...</div>;
  }

  return (
    <div className="w-full h-[600px] border-b bg-background relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={(_, node) => setSelectedNodeId(node.id)}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        colorMode={isDark ? "dark" : "light"}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={true}
      >
        <Controls className="bg-card/80 backdrop-blur-md border-border/50 shadow-sm rounded-md overflow-hidden fill-foreground !flex !flex-col" showInteractive={false} />
        <MiniMap 
          nodeColor={(n) => {
            if (n.type === 'triggerNode') return isDark ? '#10b981' : '#059669';
            if (n.data?.error || n.data?.status === 'failed') return isDark ? '#f43f5e' : '#e11d48';
            if (n.data?.status === 'completed') return isDark ? '#10b981' : '#059669';
            if (n.data?.status === 'running') return isDark ? '#3b82f6' : '#2563eb';
            return isDark ? '#a1a1aa' : '#71717a';
          }}
          maskColor={isDark ? "rgba(0, 0, 0, 0.7)" : "rgba(255, 255, 255, 0.7)"}
          className="bg-card/80 backdrop-blur-md border border-border/50 shadow-sm rounded-md overflow-hidden"
          style={{ width: 150, height: 100 }}
          pannable
          zoomable
        />
        <Background color={isDark ? "#ffffff" : "#000000"} gap={24} size={1.5} variant={BackgroundVariant.Dots} className={isDark ? "opacity-5" : "opacity-[0.03]"} />
      </ReactFlow>
      
      {selectedNodeId && (
        <NodeInspectionPanel
          nodeId={selectedNodeId}
          run={run}
          onClose={() => setSelectedNodeId(null)}
        />
      )}
    </div>
  );
};
