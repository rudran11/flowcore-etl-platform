import { useQuery } from '@tanstack/react-query';
import { fetchExecutions } from '../../../api/executions';

export const useExecutionMetrics = () => {
  return useQuery({
    queryKey: ['executions', 'metrics'],
    queryFn: () => fetchExecutions(100, 0),
    select: (data) => {
      const runs = data.items || [];
      const total = data.total;
      
      let running = 0;
      let queued = 0;
      let completed = 0;
      let failed = 0;
      let totalDuration = 0;
      let durationCount = 0;
      let longestDuration = 0;
      
      let lastSuccess: string | null = null;
      let lastFailure: string | null = null;

      // Runs are assumed to be sorted by submitted_at descending (latest first)
      for (const run of runs) {
        if (run.status === 'RUNNING') running++;
        if (run.status === 'QUEUED' || run.status === 'PENDING') queued++;
        if (run.status === 'COMPLETED') {
          completed++;
          if (!lastSuccess && run.finished_at) lastSuccess = run.finished_at;
        }
        if (run.status === 'FAILED') {
          failed++;
          if (!lastFailure && run.finished_at) lastFailure = run.finished_at;
        }

        if (run.duration_ms) {
          totalDuration += run.duration_ms;
          durationCount++;
          if (run.duration_ms > longestDuration) {
            longestDuration = run.duration_ms;
          }
        }
      }

      const resolvedTotal = total > 0 ? total : runs.length;
      const successRate = resolvedTotal > 0 ? Math.round((completed / resolvedTotal) * 100) : 0;
      const failureRate = resolvedTotal > 0 ? Math.round((failed / resolvedTotal) * 100) : 0;
      const avgDuration = durationCount > 0 ? Math.round(totalDuration / durationCount) : 0;

      return {
        total: resolvedTotal,
        running,
        queued,
        successRate,
        failureRate,
        avgDuration,
        longestDuration,
        lastSuccess,
        lastFailure
      };
    },
    refetchInterval: 10000, // Refresh metrics every 10 seconds
  });
};
