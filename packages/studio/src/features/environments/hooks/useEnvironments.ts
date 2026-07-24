import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../../../api/client';
import { Environment, EnvironmentCreate, EnvironmentUpdate, EnvironmentVariableCreate, EnvironmentVariableUpdate, EnvironmentType } from '../types';

export const useEnvironments = () => {
  return useQuery({
    queryKey: ['environments'],
    queryFn: async () => {
      const { data } = await apiClient.get<Environment[]>('/environments');
      return data;
    },
  });
};

export const useEnvironment = (id: string) => {
  return useQuery({
    queryKey: ['environments', id],
    queryFn: async () => {
      const { data } = await apiClient.get<Environment>(`/environments/${id}`);
      return data;
    },
    enabled: !!id,
  });
};

export const useCreateEnvironment = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: EnvironmentCreate) => {
      const { data } = await apiClient.post<Environment>('/environments', payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['environments'] });
    },
  });
};

export const useUpdateEnvironment = (id: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: EnvironmentUpdate) => {
      const { data } = await apiClient.put<Environment>(`/environments/${id}`, payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['environments'] });
    },
  });
};

export const useDeleteEnvironment = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/environments/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['environments'] });
    },
  });
};

export const useAddVariable = (environmentId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: EnvironmentVariableCreate) => {
      await apiClient.post(`/environments/${environmentId}/variables`, payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['environments', environmentId] });
    },
  });
};

export const useUpdateVariable = (environmentId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ variableId, payload }: { variableId: string, payload: EnvironmentVariableUpdate }) => {
      await apiClient.put(`/environments/${environmentId}/variables/${variableId}`, payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['environments', environmentId] });
    },
  });
};

export const useDeleteVariable = (environmentId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (variableId: string) => {
      await apiClient.delete(`/environments/${environmentId}/variables/${variableId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['environments', environmentId] });
    },
  });
};

export const useCloneEnvironment = (environmentId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ newName, newType }: { newName: string, newType: EnvironmentType }) => {
      const { data } = await apiClient.post<Environment>(`/environments/${environmentId}/clone`, {
        new_name: newName,
        new_type: newType
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['environments'] });
    },
  });
};

export const useImportEnv = (environmentId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (content: string) => {
      await apiClient.post(`/environments/${environmentId}/import`, { content });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['environments', environmentId] });
    },
  });
};
