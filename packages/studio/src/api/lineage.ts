import { apiClient as api } from './client';

export interface Dataset {
  id: string;
  workspace_id: string;
  environment_id?: string;
  name: string;
  type: string;
  description?: string;
  owner?: string;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface LineageNode {
  id: string;
  type: string;
  name: string;
  data?: any;
}

export interface LineageEdge {
  upstream_id: string;
  downstream_id: string;
  pipeline_id?: string;
  execution_id?: string;
  confidence_level: string;
}

export interface LineageGraph {
  nodes: LineageNode[];
  edges: LineageEdge[];
}

export const lineageApi = {
  // Datasets
  getDatasets: async (): Promise<Dataset[]> => {
    const response = await api.get('/datasets');
    return response.data;
  },
  
  getDataset: async (id: string): Promise<Dataset> => {
    const response = await api.get(`/datasets/${id}`);
    return response.data;
  },
  
  createDataset: async (data: Partial<Dataset>): Promise<Dataset> => {
    const response = await api.post('/datasets', data);
    return response.data;
  },
  
  // Lineage
  getDatasetLineage: async (id: string): Promise<LineageGraph> => {
    const response = await api.get(`/lineage/${id}`);
    return response.data;
  },
  
  getDatasetImpact: async (id: string): Promise<any> => {
    const response = await api.get(`/lineage/impact/${id}`);
    return response.data;
  }
};
