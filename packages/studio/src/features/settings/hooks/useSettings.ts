import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { settingsApi } from '../api';

export const useWorkspace = () => {
  return useQuery({
    queryKey: ['workspace-settings'],
    queryFn: () => settingsApi.getWorkspace(),
  });
};

export const useUpdateWorkspace = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: settingsApi.updateWorkspace,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-settings'] });
    },
  });
};

export const useRoles = () => {
  return useQuery({
    queryKey: ['workspace-roles'],
    queryFn: () => settingsApi.getRoles(),
  });
};

export const useMembers = () => {
  return useQuery({
    queryKey: ['workspace-members'],
    queryFn: () => settingsApi.getMembers(),
  });
};

export const useUpdateMemberRole = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, roleId }: { userId: string; roleId: string }) => 
      settingsApi.updateMemberRole(userId, roleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-members'] });
    },
  });
};

export const useRemoveMember = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: settingsApi.removeMember,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-members'] });
    },
  });
};

export const useApiKeys = () => {
  return useQuery({
    queryKey: ['workspace-api-keys'],
    queryFn: () => settingsApi.getApiKeys(),
  });
};

export const useCreateApiKey = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: settingsApi.createApiKey,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-api-keys'] });
    },
  });
};

export const useRevokeApiKey = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: settingsApi.revokeApiKey,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-api-keys'] });
    },
  });
};
