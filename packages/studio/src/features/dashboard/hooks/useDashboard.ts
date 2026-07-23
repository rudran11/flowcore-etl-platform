import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '../../../api/dashboard';

export const useDashboard = () => {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardApi.getDashboard,
    refetchInterval: 30000, // Poll every 30 seconds
    staleTime: 30000,
    gcTime: 300000,
  });
};
