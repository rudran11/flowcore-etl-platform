import { apiClient } from './client';

export interface Folder {
  id: string;
  name: string;
  parent_id?: string;
  color?: string;
  created_at: string;
  updated_at: string;
}

export interface FolderResponse {
  folder: Folder;
  pipeline_count: number;
  last_updated: string | null;
}

export const foldersApi = {
  list: async () => {
    const { data } = await apiClient.get<FolderResponse[]>('/folders');
    return data;
  },
  
  create: async (payload: { name: string; parent_id?: string; color?: string }) => {
    const { data } = await apiClient.post<Folder>('/folders', payload);
    return data;
  },
  
  update: async (id: string, payload: { name?: string; parent_id?: string; color?: string }) => {
    const { data } = await apiClient.put<Folder>(`/folders/${id}`, payload);
    return data;
  },
  
  delete: async (id: string) => {
    await apiClient.delete(`/folders/${id}`);
  }
};
