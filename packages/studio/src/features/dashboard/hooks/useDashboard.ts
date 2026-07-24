import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../../api/client';
import { useAuthStore } from '../../../stores/authStore';

export const useDashboard = () => {
  const { activeWorkspaceId } = useAuthStore();
  return useQuery({
    queryKey: ['dashboard', activeWorkspaceId],
    queryFn: async () => {
      const response = await apiClient.get('/dashboard/');
      return response.data;
    },
    enabled: !!activeWorkspaceId,
    refetchInterval: 30000, // Poll every 30 seconds
    staleTime: 30000,
    gcTime: 300000,
  });
};
