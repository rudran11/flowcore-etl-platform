import { apiClient } from './client';
import { PipelinePaginatedResponse, PipelineDetailResponse } from '../types/pipeline';

export const pipelinesApi = {
  getPipelines: async (params: { skip?: number; limit?: number; search?: string; tags?: string[] }) => {
    const { data } = await apiClient.get<PipelinePaginatedResponse>('/pipelines', { params });
    return data;
  },

  getPipelineDetails: async (pipelineId: string) => {
    const { data } = await apiClient.get<PipelineDetailResponse>(`/pipelines/${pipelineId}`);
    return data;
  },

  createPipeline: async (payload: { name: string; description?: string; tags?: string[] }) => {
    const { data } = await apiClient.post('/pipelines', payload);
    return data;
  },

  updatePipeline: async (pipelineId: string, payload: { name?: string; description?: string; tags?: string[] }) => {
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
  }
};
