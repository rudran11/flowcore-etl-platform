export interface Workspace {
  id: string;
  name: string;
  description?: string;
  organization_id: string;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceUpdate {
  name: string;
  description: string;
}

export interface Role {
  id: string;
  name: string;
  description?: string;
  permissions?: Permission[];
}

export interface Permission {
  id: string;
  name: string;
  description?: string;
}

export interface WorkspaceMember {
  user_id: string;
  email: string;
  full_name?: string;
  role_id: string;
  role_name: string;
  joined_at: string;
}

export interface ApiKey {
  id: string;
  workspace_id: string;
  name: string;
  prefix: string;
  scopes: string[];
  expires_at?: string;
  last_used_at?: string;
  revoked_at?: string;
  created_at: string;
}

export interface ApiKeyCreate {
  name: string;
  scopes: string[];
}

export interface ApiKeyCreateResponse extends ApiKey {
  key: string;
}
