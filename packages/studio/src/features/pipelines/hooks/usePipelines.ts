import { useQuery } from '@tanstack/react-query';
import { pipelinesApi } from '../../../api/pipelines';
import { useAuthStore } from '../../../stores/authStore';

interface UsePipelinesParams {
  skip?: number;
  limit?: number;
  search?: string;
  tags?: string[];
}

export const usePipelines = (params: UsePipelinesParams = {}) => {
  const { activeWorkspaceId } = useAuthStore();
  return useQuery({
    queryKey: ['pipelines', params, activeWorkspaceId],
    queryFn: () => pipelinesApi.getPipelines(params),
    staleTime: 30000,
    enabled: !!activeWorkspaceId,
    throwOnError: true,
  });
};
