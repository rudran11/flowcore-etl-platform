import React, { useMemo } from 'react';
import { 
  ReactFlow, 
  MiniMap, 
  Controls, 
  Background, 
  useNodesState, 
  useEdgesState,
  MarkerType,
  Handle,
  Position
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Database, Activity, Cloud, File } from 'lucide-react';
import { useDatasetLineage } from './hooks/useDatasets'; // reuse hook or move it

// Custom Node Component
const DatasetNode = ({ data }: any) => {
  const getIcon = () => {
    switch (data.type) {
      case 'DATABASE_TABLE': return <Database className="w-4 h-4 text-blue-400" />;
      case 'FILE': return <File className="w-4 h-4 text-green-400" />;
      case 'API': return <Cloud className="w-4 h-4 text-purple-400" />;
      case 'PIPELINE': return <Activity className="w-4 h-4 text-primary" />;
      default: return <Database className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="px-4 py-3 shadow-lg rounded-xl bg-slate-900 border border-slate-700 min-w-[200px]">
      <Handle type="target" position={Position.Left} className="w-2 h-2 bg-slate-500 border-none" />
      <div className="flex items-center gap-3">
        <div className="p-2 bg-slate-800 rounded-lg">
          {getIcon()}
        </div>
        <div>
          <div className="text-sm font-semibold text-white">{data.label}</div>
          <div className="text-xs text-slate-400 mt-0.5 uppercase tracking-wider">{data.type?.replace('_', ' ')}</div>
        </div>
      </div>
      <Handle type="source" position={Position.Right} className="w-2 h-2 bg-primary border-none" />
    </div>
  );
};

const nodeTypes = {
  dataset: DatasetNode,
};

interface LineageExplorerProps {
  datasetId: string;
}

import dagre from 'dagre';

const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

const getLayoutedElements = (nodes: any[], edges: any[], direction = 'LR') => {
  const isHorizontal = direction === 'LR';
  dagreGraph.setGraph({ rankdir: direction });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: 250, height: 80 });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  nodes.forEach((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    node.targetPosition = isHorizontal ? 'left' : 'top';
    node.sourcePosition = isHorizontal ? 'right' : 'bottom';
    
    node.position = {
      x: nodeWithPosition.x - 125,
      y: nodeWithPosition.y - 40,
    };
  });

  return { nodes, edges };
};

export const LineageExplorer: React.FC<LineageExplorerProps> = ({ datasetId }) => {
  const { data: lineageData, isLoading } = useDatasetLineage(datasetId);

  const { initialNodes, initialEdges } = useMemo(() => {
    if (!lineageData || lineageData.nodes.length === 0) {
      return { initialNodes: [], initialEdges: [] };
    }
    
    const rawNodes = lineageData.nodes.map((n) => ({
      id: n.id,
      type: 'dataset',
      position: { x: 0, y: 0 },
      data: { label: n.name, type: n.type }
    }));

    const rawEdges = lineageData.edges.map(e => ({
      id: `${e.upstream_id}-${e.downstream_id}`,
      source: e.upstream_id,
      target: e.downstream_id,
      animated: true,
      style: { stroke: '#3b82f6' },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#3b82f6' }
    }));

    const layouted = getLayoutedElements(rawNodes, rawEdges);
    return { initialNodes: layouted.nodes, initialEdges: layouted.edges };
  }, [lineageData]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Update when data changes
  React.useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  if (isLoading) {
    return <div className="h-[500px] w-full flex items-center justify-center bg-slate-950 rounded-xl border border-white/10">Loading lineage...</div>;
  }

  return (
    <div className="h-[600px] w-full bg-slate-950 rounded-xl border border-white/10 overflow-hidden relative">
      <div className="absolute top-4 left-4 z-10 bg-slate-900/80 backdrop-blur border border-white/10 p-3 rounded-lg shadow-xl">
        <h3 className="text-white font-medium mb-2 text-sm">Legend</h3>
        <div className="flex flex-col gap-2 text-xs text-slate-300">
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-blue-500"></div> Database Table</div>
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-green-500"></div> File</div>
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-primary"></div> Pipeline</div>
        </div>
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        className="bg-slate-950"
      >
        <Background color="#1e293b" gap={16} />
        <Controls className="bg-slate-900 border-white/10 fill-white" />
        <MiniMap 
          nodeColor={(node) => {
            switch (node.data?.type) {
              case 'DATABASE_TABLE': return '#3b82f6';
              case 'PIPELINE': return '#0ea5e9';
              default: return '#475569';
            }
          }}
          maskColor="rgba(15, 23, 42, 0.7)"
          className="bg-slate-900 border-white/10"
        />
      </ReactFlow>
    </div>
  );
};
