import { apiClient } from './client';
import { PipelinePaginatedResponse, PipelineDetailResponse } from '../types/pipeline';

export const pipelinesApi = {
  getPipelines: async (params: { 
    skip?: number; limit?: number; search?: string; tags?: string[];
    folder_id?: string; is_archived?: boolean; is_favorite?: boolean;
    sort_by?: string; sort_order?: 'asc'|'desc';
  }) => {
    const { data } = await apiClient.get<PipelinePaginatedResponse>('/pipelines', { params });
    return data;
  },

  getPipelineDetails: async (pipelineId: string) => {
    const { data } = await apiClient.get<PipelineDetailResponse>(`/pipelines/${pipelineId}`);
    return data;
  },

  createPipeline: async (payload: { name: string; description?: string; tags?: string[]; folder_id?: string; icon?: string; color?: string; }) => {
    const { data } = await apiClient.post('/pipelines', payload);
    return data;
  },

  updatePipeline: async (pipelineId: string, payload: { name?: string; description?: string; tags?: string[]; folder_id?: string; is_archived?: boolean; icon?: string; color?: string; }) => {
    const { data } = await apiClient.put(`/pipelines/${pipelineId}`, payload);
    return data;
  },

  deletePipeline: async (pipelineId: string) => {
    await apiClient.delete(`/pipelines/${pipelineId}`);
  },
  
  savePipelineVersion: async (pipelineId: string, payload: { version_tag: string; steps?: any[]; dsl_definition?: any; graph_definition?: any }) => {
    const { data } = await apiClient.post(`/pipelines/${pipelineId}/versions`, payload);
    return data;
  },

  executePipeline: async (pipelineId: string, version: string, payload: { parameters?: Record<string, any>; dry_run?: boolean }) => {
    const { data } = await apiClient.post(`/pipelines/${pipelineId}/versions/${version}/execute`, payload);
    return data;
  },

  previewPipeline: async (payload: { pipeline: any; preview_node_id: string; limit: number }) => {
    const { data } = await apiClient.post(`/pipelines/preview`, payload);
    return data;
  },

  toggleFavorite: async (pipelineId: string, is_favorite: boolean) => {
    const { data } = await apiClient.post(`/pipelines/${pipelineId}/favorite`, null, {
      params: { is_favorite }
    });
    return data;
  },

  bulkAction: async (payload: { action: 'delete' | 'archive' | 'move'; pipeline_ids: string[]; folder_id?: string; archive?: boolean; }) => {
    const { data } = await apiClient.post('/pipelines/bulk', payload);
    return data;
  }
};
