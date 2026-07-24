import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { schedulesApi } from '../../../api/schedules';
import { Schedule } from '../../../types/schedule';
import { toast } from 'sonner';
import { useAuthStore } from '../../../stores/authStore';

export const useSchedules = (params?: { skip?: number; limit?: number }) => {
  const { activeWorkspaceId } = useAuthStore();
  return useQuery({
    queryKey: ['schedules', params, activeWorkspaceId],
    queryFn: () => schedulesApi.getSchedules(params),
    enabled: !!activeWorkspaceId,
  });
};

export const useSchedule = (id: string) => {
  const { activeWorkspaceId } = useAuthStore();
  return useQuery({
    queryKey: ['schedules', id, activeWorkspaceId],
    queryFn: () => schedulesApi.getSchedule(id),
    enabled: !!id && !!activeWorkspaceId,
  });
};

export const useCreateSchedule = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: Partial<Schedule>) => schedulesApi.createSchedule(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] });
      toast.success('Schedule created successfully');
    },
    onError: () => {
      toast.error('Failed to create schedule');
    }
  });
};

export const useUpdateSchedule = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string, payload: Partial<Schedule> }) => schedulesApi.updateSchedule(id, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] });
      queryClient.invalidateQueries({ queryKey: ['schedules', variables.id] });
      toast.success('Schedule updated successfully');
    },
    onError: () => {
      toast.error('Failed to update schedule');
    }
  });
};

export const usePauseSchedule = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => schedulesApi.pauseSchedule(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] });
      queryClient.invalidateQueries({ queryKey: ['schedules', id] });
      toast.info('Schedule paused');
    },
    onError: () => {
      toast.error('Failed to pause schedule');
    }
  });
};

export const useResumeSchedule = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => schedulesApi.resumeSchedule(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] });
      queryClient.invalidateQueries({ queryKey: ['schedules', id] });
      toast.success('Schedule resumed');
    },
    onError: () => {
      toast.error('Failed to resume schedule');
    }
  });
};

export const useTriggerSchedule = () => {
  return useMutation({
    mutationFn: (id: string) => schedulesApi.triggerSchedule(id),
    onSuccess: () => {
      toast.success('Trigger executed manually');
    },
    onError: () => {
      toast.error('Failed to trigger schedule');
    }
  });
};

export const useDeleteSchedule = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => schedulesApi.deleteSchedule(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] });
      toast.success('Schedule deleted');
    },
    onError: () => {
      toast.error('Failed to delete schedule');
    }
  });
};
