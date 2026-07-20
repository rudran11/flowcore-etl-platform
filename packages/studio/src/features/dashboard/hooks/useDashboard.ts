import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '../../../api/dashboard';

export const useDashboard = () => {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardApi.getDashboard,
    refetchInterval: 5000, // Poll every 5 seconds for live dashboard updates
  });
};
