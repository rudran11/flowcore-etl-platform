import { useQuery } from '@tanstack/react-query';
import { lineageApi } from '../../../api/lineage';

export const useDatasets = () => {
  return useQuery({
    queryKey: ['datasets'],
    queryFn: lineageApi.getDatasets,
    throwOnError: true,
  });
};

export const useDataset = (id: string) => {
  return useQuery({
    queryKey: ['datasets', id],
    queryFn: () => lineageApi.getDataset(id),
    enabled: !!id,
    throwOnError: true,
  });
};

export const useDatasetLineage = (id: string) => {
  return useQuery({
    queryKey: ['lineage', id],
    queryFn: () => lineageApi.getDatasetLineage(id),
    enabled: !!id,
    throwOnError: true,
  });
};

export const useDatasetImpact = (id: string) => {
  return useQuery({
    queryKey: ['impact', id],
    queryFn: () => lineageApi.getDatasetImpact(id),
    enabled: !!id,
    throwOnError: true,
  });
};
