import { apiClient } from './client';
import { PluginResponse, PluginHealthResponse, PluginValidationRequest, PluginValidationResponse, PluginStatsResponse } from '../types/plugin';

export const pluginsApi = {
  getPlugins: async (): Promise<PluginResponse[]> => {
    const response = await apiClient.get('/plugins');
    return response.data;
  },

  getPlugin: async (pluginId: string): Promise<PluginResponse> => {
    const response = await apiClient.get(`/plugins/${pluginId}?_t=${Date.now()}`);
    return response.data;
  },

  getCategories: async (): Promise<string[]> => {
    const response = await apiClient.get('/plugins/categories');
    return response.data;
  },

  getStats: async (): Promise<PluginStatsResponse> => {
    const response = await apiClient.get('/plugins/stats');
    return response.data;
  },

  getPluginHealth: async (pluginId: string): Promise<PluginHealthResponse> => {
    const response = await apiClient.get(`/plugins/${pluginId}/health`);
    return response.data;
  },

  validatePlugin: async (request: PluginValidationRequest): Promise<PluginValidationResponse> => {
    const response = await apiClient.post('/plugins/validate', request);
    return response.data;
  },
};
