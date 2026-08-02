import { create } from 'zustand';
import { 
  Connection, 
  Edge, 
  EdgeChange, 
  Node, 
  NodeChange, 
  addEdge, 
  OnNodesChange, 
  OnEdgesChange, 
  OnConnect, 
  applyNodeChanges, 
  applyEdgeChanges 
} from '@xyflow/react';
import yaml from 'yaml';
import dagre from 'dagre';
import { Pipeline } from '../types/pipeline';
import { toast } from 'sonner';

export interface PipelineBuilderState {
  nodes: Node[];
  edges: Edge[];
  pipeline: Pipeline | null;
  rawYaml: string;
  isDirty: boolean;
  isValid: boolean;
  validationErrors: string[];
  clipboard: Node[];
  
  // Templates
  isTemplateDialogOpen: boolean;
  templateNodeToSave: Node | null;
  openTemplateDialog: (node: Node) => void;
  closeTemplateDialog: () => void;
  
  // Actions
  setPipeline: (pipeline: Pipeline, yamlString: string) => void;
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;
  
  setNodes: (nodes: Node[]) => void;
  setEdges: (edges: Edge[]) => void;
  
  // Sync
  updateFromYaml: (yamlString: string) => void;
  syncToYaml: () => void;
  
  // Undo/Redo
  undo: () => void;
  redo: () => void;
  history: { nodes: Node[]; edges: Edge[]; rawYaml: string }[];
  historyIndex: number;
  saveHistory: () => void;

  // Features
  autoLayout: (direction?: 'TB' | 'LR') => void;
  validatePipeline: () => void;
  simulateExecution: () => void;
  
  // Clipboard
  copySelected: () => void;
  pasteClipboard: () => void;
  duplicateSelected: () => void;
  deleteSelected: () => void;

  // Persistence
  saveDraftToStorage: (id: string) => void;
  loadDraftFromStorage: (id: string, pipeline: Pipeline) => boolean;
  clearDraft: (id: string) => void;
}

const STORAGE_KEY_PREFIX = 'flowcore_draft_';

const generateYamlFromGraph = (nodes: Node[], edges: Edge[], basePipeline: Pipeline | null) => {
  if (!basePipeline) return '';
  const triggerNode = nodes.find(n => n.type === 'triggerNode');
  
  const steps: Record<string, any> = {};
  
  nodes.filter(n => n.type === 'stepNode').forEach(node => {
    // Find dependencies (edges targeting this node)
    const depends_on = edges.filter(e => e.target === node.id).map(e => e.source).filter(src => src !== 'trigger');
    
    steps[node.id] = {
      plugin_id: node.data.plugin_id,
      config: node.data.config || {},
      ...(depends_on.length > 0 ? { depends_on } : {})
    };
  });

  const obj = {
    description: basePipeline.description || '',
    trigger: triggerNode ? {
      type: triggerNode.data.type || 'schedule',
      schedule: triggerNode.data.schedule || '0 0 * * *'
    } : { type: 'manual' },
    steps
  };
  
  return yaml.stringify(obj);
};

const buildGraphFromYaml = (yamlString: string) => {
  const parsed = yaml.parse(yamlString);
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  
  const triggerData = parsed.trigger || { type: 'manual', schedule: '0 0 * * *' };
  
  nodes.push({
    id: 'trigger',
    type: 'triggerNode',
    position: { x: 0, y: 0 },
    data: { label: 'Trigger', type: triggerData.type, schedule: triggerData.schedule }
  });

  if (parsed.steps) {
    Object.entries(parsed.steps).forEach(([stepId, step]: [string, any]) => {
      nodes.push({
        id: stepId,
        type: 'stepNode',
        position: { x: 0, y: 0 },
        data: { label: stepId, plugin_id: step.plugin_id, config: step.config }
      });
      
      if (step.depends_on) {
        step.depends_on.forEach((dep: string) => {
          edges.push({
            id: `e-${dep}-${stepId}`,
            source: dep,
            target: stepId,
            type: 'animated',
          });
        });
      } else {
        edges.push({
          id: `e-trigger-${stepId}`,
          source: 'trigger',
          target: stepId,
          type: 'animated',
        });
      }
    });
  }
  
  return { nodes, edges };
};

export const usePipelineBuilderStore = create<PipelineBuilderState>((set, get) => ({
  nodes: [],
  edges: [],
  pipeline: null,
  rawYaml: '',
  isDirty: false,
  isValid: true,
  validationErrors: [],
  clipboard: [],
  isTemplateDialogOpen: false,
  templateNodeToSave: null,
  
  openTemplateDialog: (node) => set({ isTemplateDialogOpen: true, templateNodeToSave: node }),
  closeTemplateDialog: () => set({ isTemplateDialogOpen: false, templateNodeToSave: null }),
  
  history: [],
  historyIndex: -1,

  saveHistory: () => {
    const { nodes, edges, rawYaml, history, historyIndex } = get();
    const newHistory = history.slice(0, historyIndex + 1);
    newHistory.push({ nodes, edges, rawYaml });
    
    if (newHistory.length > 50) newHistory.shift();
    
    set({ history: newHistory, historyIndex: newHistory.length - 1, isDirty: true });
    get().validatePipeline();
  },

  setPipeline: (pipeline, yamlString) => {
    const { nodes, edges } = buildGraphFromYaml(yamlString);
    
    set({ 
      pipeline, 
      rawYaml: yamlString, 
      nodes, 
      edges,
      isDirty: false,
      history: [{ nodes, edges, rawYaml: yamlString }],
      historyIndex: 0
    });
    
    // Apply layout initially
    get().autoLayout('TB');
  },

  onNodesChange: (changes: NodeChange[]) => {
    set({ nodes: applyNodeChanges(changes, get().nodes) });
    // Note: Do not auto-sync to YAML on position changes, only on data/connection changes
    const isStructureChange = changes.some(c => c.type === 'remove' || c.type === 'add');
    if (isStructureChange) {
      get().syncToYaml();
      get().saveHistory();
    }
  },

  onEdgesChange: (changes: EdgeChange[]) => {
    set({ edges: applyEdgeChanges(changes, get().edges) });
    const isStructureChange = changes.some(c => c.type === 'remove' || c.type === 'add');
    if (isStructureChange) {
      get().syncToYaml();
      get().saveHistory();
    }
  },

  onConnect: (connection: Connection) => {
    // Prevent cycles
    const { edges } = get();
    const newEdges = addEdge({ ...connection, type: 'animated' }, edges);
    set({ edges: newEdges });
    get().syncToYaml();
    get().saveHistory();
  },

  setNodes: (nodes: Node[]) => {
    set({ nodes });
    get().syncToYaml();
    get().saveHistory();
  },

  setEdges: (edges: Edge[]) => {
    set({ edges });
    get().syncToYaml();
    get().saveHistory();
  },

  updateFromYaml: (yamlString: string) => {
    try {
      const { nodes: newNodes, edges: newEdges } = buildGraphFromYaml(yamlString);
      
      // Merge positions from existing nodes to avoid jumping
      const { nodes: existingNodes } = get();
      const posMap = new Map(existingNodes.map(n => [n.id, n.position]));
      
      const mergedNodes = newNodes.map(n => ({
        ...n,
        position: posMap.get(n.id) || n.position
      }));

      set({ rawYaml: yamlString, nodes: mergedNodes, edges: newEdges, isDirty: true });
      get().validatePipeline();
      get().saveHistory();
    } catch (e) {
      set({ rawYaml: yamlString, isDirty: true, isValid: false, validationErrors: ['Invalid YAML syntax'] });
    }
  },

  syncToYaml: () => {
    const { nodes, edges, pipeline } = get();
    const yamlString = generateYamlFromGraph(nodes, edges, pipeline);
    set({ rawYaml: yamlString, isDirty: true });
    get().validatePipeline();
  },

  autoLayout: (direction = 'TB') => {
    const { nodes, edges } = get();
    const dagreGraph = new dagre.graphlib.Graph();
    dagreGraph.setDefaultEdgeLabel(() => ({}));
    
    const nodeWidth = 250;
    const nodeHeight = 80;

    dagreGraph.setGraph({ rankdir: direction, ranksep: 100, nodesep: 100 });

    nodes.forEach((node) => {
      dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
    });

    edges.forEach((edge) => {
      dagreGraph.setEdge(edge.source, edge.target);
    });

    dagre.layout(dagreGraph);

    const layoutedNodes = nodes.map((node) => {
      const nodeWithPosition = dagreGraph.node(node.id);
      return {
        ...node,
        position: {
          x: nodeWithPosition.x - nodeWidth / 2,
          y: nodeWithPosition.y - nodeHeight / 2,
        },
      };
    });

    set({ nodes: layoutedNodes });
    get().saveHistory();
  },

  validatePipeline: () => {
    const { nodes, edges } = get();
    const errors: string[] = [];
    
    // Cycle detection
    const dagreGraph = new dagre.graphlib.Graph();
    nodes.forEach(n => dagreGraph.setNode(n.id, {}));
    edges.forEach(e => dagreGraph.setEdge(e.source, e.target));
    
    if (!dagre.graphlib.alg.isAcyclic(dagreGraph)) {
      errors.push('Cycle detected in pipeline graph');
    }

    nodes.forEach(n => {
      if (n.id !== 'trigger') {
        const hasIncoming = edges.some(e => e.target === n.id);
        if (!hasIncoming) {
          errors.push(`Node '${n.id}' is disconnected`);
          n.data = { ...n.data, error: true };
        } else if (n.type === 'stepNode' && (!n.data.config || Object.keys(n.data.config).length === 0)) {
          errors.push(`Node '${n.id}' has missing configuration`);
          n.data = { ...n.data, error: true };
        } else {
          n.data = { ...n.data, error: false }; // clear old error
        }
      }
    });

    set({ 
      isValid: errors.length === 0, 
      validationErrors: errors,
      nodes: [...nodes] // Trigger re-render with new data.error states
    });
  },

  simulateExecution: () => {
    const { nodes, edges } = get();
    set({
      nodes: nodes.map(n => ({ ...n, data: { ...n.data, status: 'running' } })),
      edges: edges.map(e => ({ ...e, data: { ...e.data, status: 'running' } }))
    });
    
    setTimeout(() => {
      const { nodes: currentNodes, edges: currentEdges } = get();
      set({
        nodes: currentNodes.map(n => ({ ...n, data: { ...n.data, status: 'success' } })),
        edges: currentEdges.map(e => ({ ...e, data: { ...e.data, status: 'success' } }))
      });
      
      setTimeout(() => {
        const { nodes: finalNodes, edges: finalEdges } = get();
        set({
          nodes: finalNodes.map(n => {
            // eslint-disable-next-line @typescript-eslint/no-unused-vars
            const { status: _status, ...restData } = n.data;
            return { ...n, data: restData };
          }),
          edges: finalEdges.map(e => {
            // eslint-disable-next-line @typescript-eslint/no-unused-vars
            const { status: _status, ...restData } = e.data || {};
            return { ...e, data: restData };
          })
        });
      }, 3000);
    }, 4000);
  },

  undo: () => {
    const { history, historyIndex } = get();
    if (historyIndex > 0) {
      const prev = history[historyIndex - 1];
      set({ nodes: prev.nodes, edges: prev.edges, rawYaml: prev.rawYaml, historyIndex: historyIndex - 1, isDirty: true });
    }
  },

  redo: () => {
    const { history, historyIndex } = get();
    if (historyIndex < history.length - 1) {
      const next = history[historyIndex + 1];
      set({ nodes: next.nodes, edges: next.edges, rawYaml: next.rawYaml, historyIndex: historyIndex + 1, isDirty: true });
    }
  },

  copySelected: () => {
    const { nodes } = get();
    const selected = nodes.filter(n => n.selected);
    if (selected.length > 0) {
      set({ clipboard: JSON.parse(JSON.stringify(selected)) });
      toast.success(`${selected.length} nodes copied`);
    }
  },

  pasteClipboard: () => {
    const { clipboard, nodes } = get();
    if (clipboard.length === 0) return;
    
    const newNodes = clipboard.map(n => ({
      ...n,
      id: `${n.id}_copy_${Date.now()}`,
      selected: true,
      position: { x: n.position.x + 50, y: n.position.y + 50 }
    }));
    
    set({ nodes: [...nodes.map(n => ({...n, selected: false})), ...newNodes] });
    get().syncToYaml();
    get().saveHistory();
  },

  duplicateSelected: () => {
    get().copySelected();
    get().pasteClipboard();
  },

  deleteSelected: () => {
    const { nodes, edges } = get();
    const selectedIds = new Set(nodes.filter(n => n.selected).map(n => n.id));
    if (selectedIds.size === 0) return;
    
    set({
      nodes: nodes.filter(n => !selectedIds.has(n.id)),
      edges: edges.filter(e => !selectedIds.has(e.source) && !selectedIds.has(e.target))
    });
    get().syncToYaml();
    get().saveHistory();
  },

  saveDraftToStorage: (id: string) => {
    const { rawYaml, isDirty } = get();
    if (isDirty) {
      localStorage.setItem(`${STORAGE_KEY_PREFIX}${id}`, rawYaml);
    }
  },

  loadDraftFromStorage: (id: string, pipeline: Pipeline) => {
    const draft = localStorage.getItem(`${STORAGE_KEY_PREFIX}${id}`);
    if (draft) {
      const { nodes, edges } = buildGraphFromYaml(draft);
      set({ 
        pipeline,
        rawYaml: draft, 
        nodes, 
        edges, 
        isDirty: true,
        history: [{ nodes, edges, rawYaml: draft }],
        historyIndex: 0
      });
      get().autoLayout('TB');
      return true;
    }
    return false;
  },

  clearDraft: (id: string) => {
    localStorage.removeItem(`${STORAGE_KEY_PREFIX}${id}`);
  }
}));
