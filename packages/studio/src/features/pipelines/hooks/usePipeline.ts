import { useQuery } from '@tanstack/react-query';
import { pipelinesApi } from '../../../api/pipelines';

export const usePipeline = (pipelineId: string) => {
  return useQuery({
    queryKey: ['pipelines', pipelineId],
    queryFn: () => pipelinesApi.getPipelineDetails(pipelineId),
    staleTime: 30000,
  });
};
