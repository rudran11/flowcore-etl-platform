import { Node, Edge } from '@xyflow/react';

export type ValidationSeverity = 'error' | 'warning' | 'suggestion';

export interface ValidationIssue {
  id: string;
  severity: ValidationSeverity;
  title: string;
  description: string;
  nodeId?: string;
  edgeId?: string;
  quickFix?: 'open_config' | 'delete_node';
}

export interface ValidationResult {
  isValid: boolean;
  issues: ValidationIssue[];
  healthScore: number;
}

export const validatePipelineGraph = (nodes: Node[], edges: Edge[]): ValidationResult => {
  const issues: ValidationIssue[] = [];

  // 1. Empty Pipeline
  if (nodes.length === 0) {
    issues.push({
      id: 'empty_pipeline',
      severity: 'error',
      title: 'Empty Pipeline',
      description: 'The pipeline must contain at least a trigger and a destination.',
    });
  } else {
    // 2. Trigger Node Validation
    const triggerNodes = nodes.filter(n => n.type === 'triggerNode');
    if (triggerNodes.length === 0) {
      issues.push({
        id: 'missing_trigger',
        severity: 'error',
        title: 'Missing Trigger',
        description: 'Pipeline must start with a Trigger node.',
      });
    } else if (triggerNodes.length > 1) {
      triggerNodes.forEach(t => {
        issues.push({
          id: `multiple_trigger_${t.id}`,
          severity: 'error',
          title: 'Multiple Triggers',
          description: 'A pipeline can only have one Trigger node.',
          nodeId: t.id,
          quickFix: 'delete_node'
        });
      });
    }

    // 3. Duplicate Node Names
    const nameCounts = new Map<string, string[]>();
    nodes.forEach(n => {
      const name = n.data.label as string || n.id;
      if (!nameCounts.has(name)) nameCounts.set(name, []);
      nameCounts.get(name)!.push(n.id);
    });
    
    nameCounts.forEach((ids, name) => {
      if (ids.length > 1) {
        ids.forEach(id => {
          issues.push({
            id: `duplicate_name_${id}`,
            severity: 'error',
            title: 'Duplicate Name',
            description: `Multiple nodes share the name "${name}". Names must be unique.`,
            nodeId: id,
            quickFix: 'open_config'
          });
        });
      }
    });

    // 4. Missing Configuration (Removed to allow plugins with no config like test-source)

    // 5. Connectivity & Unused Nodes (Orphaned/Disconnected)
    nodes.forEach(n => {
      if (n.type !== 'triggerNode') {
        const hasIncoming = edges.some(e => e.target === n.id);
        const hasOutgoing = edges.some(e => e.source === n.id);
        
        if (!hasIncoming && !hasOutgoing) {
          issues.push({
            id: `orphan_node_${n.id}`,
            severity: 'warning',
            title: 'Orphaned Node',
            description: 'This node is completely disconnected from the pipeline.',
            nodeId: n.id,
            quickFix: 'delete_node'
          });
        } else if (!hasIncoming) {
          issues.push({
            id: `unreachable_node_${n.id}`,
            severity: 'error',
            title: 'Unreachable Node',
            description: 'This node has no incoming connections and will never execute.',
            nodeId: n.id,
          });
        }
      }
    });

    // 6. Cycle Detection using DFS
    const graph = new Map<string, string[]>();
    nodes.forEach(n => graph.set(n.id, []));
    edges.forEach(e => {
      if (graph.has(e.source)) {
        graph.get(e.source)!.push(e.target);
      }
    });

    const visited = new Set<string>();
    const recStack = new Set<string>();
    const cycleNodes = new Set<string>();

    const detectCycle = (nodeId: string): boolean => {
      if (recStack.has(nodeId)) return true;
      if (visited.has(nodeId)) return false;

      visited.add(nodeId);
      recStack.add(nodeId);

      const neighbors = graph.get(nodeId) || [];
      for (const neighbor of neighbors) {
        if (detectCycle(neighbor)) {
          cycleNodes.add(nodeId);
          cycleNodes.add(neighbor);
          return true;
        }
      }

      recStack.delete(nodeId);
      return false;
    };

    nodes.forEach(n => {
      if (!visited.has(n.id)) {
        detectCycle(n.id);
      }
    });

    cycleNodes.forEach(nodeId => {
      issues.push({
        id: `cycle_${nodeId}`,
        severity: 'error',
        title: 'Circular Dependency',
        description: 'This node is part of a cycle, which prevents execution.',
        nodeId: nodeId
      });
    });

    edges.forEach(e => {
      if (cycleNodes.has(e.source) && cycleNodes.has(e.target)) {
        issues.push({
          id: `cycle_edge_${e.id}`,
          severity: 'error',
          title: 'Circular Edge',
          description: 'This edge forms a cycle.',
          edgeId: e.id
        });
      }
    });
    
    // 7. Suggestions
    if (nodes.length > 0 && !nodes.some(n => (n.data.description || '').toString().length > 0)) {
      issues.push({
        id: 'missing_descriptions',
        severity: 'suggestion',
        title: 'Add Descriptions',
        description: 'Consider adding descriptions or notes to your nodes for better maintainability.',
      });
    }
  }

  // Calculate Health Score
  let healthScore = 100;
  issues.forEach(issue => {
    if (issue.severity === 'error') healthScore -= 20;
    else if (issue.severity === 'warning') healthScore -= 5;
    else if (issue.severity === 'suggestion') healthScore -= 1;
  });

  healthScore = Math.max(0, healthScore);
  const isValid = !issues.some(i => i.severity === 'error');

  return { isValid, issues, healthScore };
};
