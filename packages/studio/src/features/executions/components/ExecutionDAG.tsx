import React, { useMemo, useEffect } from 'react';
import { ReactFlow, MiniMap, Controls, Background, useNodesState, useEdgesState } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { ExecutionResponse } from '../../../api/executions';
import { usePipeline } from '../../pipelines/hooks/usePipeline';

interface ExecutionDAGProps {
  run: ExecutionResponse;
}

const statusColors: Record<string, string> = {
  PENDING: '#94a3b8',
  QUEUED: '#94a3b8',
  RUNNING: '#3b82f6',
  COMPLETED: '#22c55e',
  FAILED: '#ef4444',
  CANCELLED: '#f59e0b',
  SKIPPED: '#64748b'
};

export const ExecutionDAG: React.FC<ExecutionDAGProps> = ({ run }) => {
  const { data: pipeline } = usePipeline(run.pipeline_id);

  const currentVersion = useMemo(() => {
    return pipeline?.versions?.find(v => v.id === run.pipeline_version) || pipeline?.versions?.[0];
  }, [pipeline, run.pipeline_version]);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    if (!currentVersion?.steps) {
      setNodes([]);
      setEdges([]);
      return;
    }

    const newNodes = currentVersion.steps.map((step: any, index: number) => {
      const stepRun = run.steps?.[step.step_id];
      const status = stepRun?.status || 'PENDING';
      const bgColor = statusColors[status] || '#94a3b8';
      
      return {
        id: step.step_id,
        position: { x: 250 * (index % 3), y: 100 * Math.floor(index / 3) }, // Basic auto layout
        data: { 
          label: (
            <div 
              className="flex flex-col items-center group relative"
              title={`Status: ${status}\nRetries: ${stepRun?.retry_count || 0}\nDuration: ${stepRun?.duration_ms ? (stepRun.duration_ms / 1000).toFixed(1) + 's' : 'N/A'}`}
            >
              <span className="font-semibold text-sm">{step.step_id}</span>
              <span className="text-xs mt-1 px-2 py-0.5 rounded-full bg-white/20 text-white">
                {status}
              </span>
            </div>
          )
        },
        style: {
          background: bgColor,
          color: '#fff',
          border: 'none',
          borderRadius: '8px',
          padding: '10px',
          width: 150,
          boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
        }
      };
    });

    const newEdges: any[] = [];
    currentVersion.steps.forEach((step: any) => {
      if (step.depends_on) {
        step.depends_on.forEach((dep: string) => {
          newEdges.push({
            id: `e-${dep}-${step.step_id}`,
            source: dep,
            target: step.step_id,
            animated: run.steps?.[step.step_id]?.status === 'RUNNING' || run.status === 'RUNNING',
            style: { stroke: '#94a3b8', strokeWidth: 2 }
          });
        });
      }
    });

    setNodes(newNodes);
    setEdges(newEdges);
  }, [currentVersion, run, setNodes, setEdges]);

  if (!pipeline) {
    return <div className="h-full flex items-center justify-center text-muted-foreground">Loading DAG...</div>;
  }

  return (
    <div className="w-full h-[500px] border rounded-xl overflow-hidden bg-muted/10 relative">
      <div className="absolute top-2 right-2 z-10 bg-background/80 p-2 rounded text-xs text-muted-foreground border">
        Nodes: {nodes.length} | Edges: {edges.length} | Version steps: {currentVersion?.steps?.length || 0}
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Controls />
        <MiniMap />
        <Background gap={12} size={1} />
      </ReactFlow>
    </div>
  );
};
