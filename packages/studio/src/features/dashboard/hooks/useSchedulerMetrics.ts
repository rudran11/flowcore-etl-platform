import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../../api/client';
import { useAuthStore } from '../../../stores/authStore';

export interface SchedulerMetrics {
  queue_length: number;
  avg_execution_delay_seconds: number;
  success_rate: number;
  failure_rate: number;
  last_heartbeat: string;
  missed_schedules: number;
}

export const useSchedulerMetrics = () => {
  const { activeWorkspaceId } = useAuthStore();
  return useQuery({
    queryKey: ['scheduler', 'metrics', activeWorkspaceId],
    queryFn: async () => {
      const response = await apiClient.get<SchedulerMetrics>('/schedules/metrics');
      return response.data;
    },
    refetchInterval: 10000, // Poll every 10 seconds for metrics
    enabled: !!activeWorkspaceId,
  });
};
