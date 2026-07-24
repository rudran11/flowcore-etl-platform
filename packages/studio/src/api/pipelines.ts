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
  }
};
