import { useQuery, useMutation } from '@tanstack/react-query';
import { pluginsApi } from '../../../api/plugins';
import { PluginValidationRequest } from '../../../types/plugin';

export const usePlugins = () => {
  return useQuery({
    queryKey: ['plugins'],
    queryFn: pluginsApi.getPlugins,
  });
};

export const usePlugin = (pluginId: string) => {
  return useQuery({
    queryKey: ['plugins', pluginId],
    queryFn: () => pluginsApi.getPlugin(pluginId),
    enabled: !!pluginId,
  });
};

export const usePluginCategories = () => {
  return useQuery({
    queryKey: ['plugins', 'categories'],
    queryFn: pluginsApi.getCategories,
  });
};

export const usePluginStats = () => {
  return useQuery({
    queryKey: ['plugins', 'stats'],
    queryFn: pluginsApi.getStats,
  });
};

export const usePluginHealth = (pluginId: string) => {
  return useQuery({
    queryKey: ['plugins', pluginId, 'health'],
    queryFn: () => pluginsApi.getPluginHealth(pluginId),
    enabled: !!pluginId,
    refetchInterval: 60000,
  });
};

export const useValidatePlugin = () => {
  return useMutation({
    mutationFn: (request: PluginValidationRequest) => pluginsApi.validatePlugin(request),
  });
};
