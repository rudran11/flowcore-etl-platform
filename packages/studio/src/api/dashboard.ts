import { apiClient } from './client';
import { DashboardResponse } from '../types/dashboard';

export const dashboardApi = {
  getDashboard: async (): Promise<DashboardResponse> => {
    const response = await apiClient.get('/dashboard/');
    return response.data;
  },
};
