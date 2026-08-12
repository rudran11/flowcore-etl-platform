import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { pipelinesApi } from '../../../api/pipelines';
import { useAuthStore } from '../../../stores/authStore';

interface UsePipelinesParams {
  skip?: number;
  limit?: number;
  search?: string;
  tags?: string[];
  folder_id?: string;
  is_archived?: boolean;
  is_favorite?: boolean;
  sort_by?: string;
  sort_order?: 'asc'|'desc';
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

export const useToggleFavorite = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, is_favorite }: { id: string; is_favorite: boolean }) => 
      pipelinesApi.toggleFavorite(id, is_favorite),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pipelines'] });
    }
  });
};

export const useBulkAction = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { action: 'delete' | 'archive' | 'move'; pipeline_ids: string[]; folder_id?: string; archive?: boolean; }) => 
      pipelinesApi.bulkAction(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pipelines'] });
      queryClient.invalidateQueries({ queryKey: ['folders'] }); // Folders pipeline counts might change
    }
  });
};
