import { useQuery } from '@tanstack/react-query';
import { pipelinesApi } from '../../../api/pipelines';

interface UsePipelinesParams {
  skip?: number;
  limit?: number;
  search?: string;
  tags?: string[];
}

export const usePipelines = (params: UsePipelinesParams = {}) => {
  return useQuery({
    queryKey: ['pipelines', params],
    queryFn: () => pipelinesApi.getPipelines(params),
    staleTime: 30000,
  });
};
