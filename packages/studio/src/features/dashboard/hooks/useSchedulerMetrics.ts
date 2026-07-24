import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

export interface SchedulerMetrics {
  queue_length: number;
  avg_execution_delay_seconds: number;
  success_rate: number;
  failure_rate: number;
  last_heartbeat: string;
  missed_schedules: number;
}

export const useSchedulerMetrics = () => {
  return useQuery({
    queryKey: ['scheduler', 'metrics'],
    queryFn: async () => {
      const response = await axios.get<SchedulerMetrics>('http://localhost:8000/api/v1/schedules/metrics');
      return response.data;
    },
    refetchInterval: 10000, // Poll every 10 seconds for metrics
  });
};
