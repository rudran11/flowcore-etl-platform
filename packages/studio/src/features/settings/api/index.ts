import { apiClient } from '../../../api/client';
import { Workspace, Role, WorkspaceMember, ApiKey, ApiKeyCreate, ApiKeyCreateResponse, WorkspaceUpdate } from '../types';

export const settingsApi = {
  getWorkspace: () => 
    apiClient.get<Workspace>('/settings/workspace').then(res => res.data),
  
  updateWorkspace: (data: WorkspaceUpdate) => 
    apiClient.put<Workspace>('/settings/workspace', data).then(res => res.data),
    
  getRoles: () => 
    apiClient.get<Role[]>('/settings/roles').then(res => res.data),
    
  getMembers: () => 
    apiClient.get<WorkspaceMember[]>('/settings/members').then(res => res.data),
    
  updateMemberRole: (userId: string, roleId: string) => 
    apiClient.patch(`/settings/members/${userId}`, { role_id: roleId }).then(res => res.data),
    
  removeMember: (userId: string) => 
    apiClient.delete(`/settings/members/${userId}`).then(res => res.data),
    
  getApiKeys: () => 
    apiClient.get<ApiKey[]>('/settings/api-keys').then(res => res.data),
    
  createApiKey: (data: ApiKeyCreate) => 
    apiClient.post<ApiKeyCreateResponse>('/settings/api-keys', data).then(res => res.data),
    
  revokeApiKey: (keyId: string) => 
    apiClient.delete(`/settings/api-keys/${keyId}`).then(res => res.data),
};
