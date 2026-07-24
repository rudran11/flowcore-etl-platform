export type EnvironmentType = 'DEVELOPMENT' | 'QA' | 'STAGING' | 'PRODUCTION' | 'CUSTOM';

export interface EnvironmentVariable {
  id: string;
  key: string;
  value: string;
  is_secret: boolean;
}

export interface Environment {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  type: EnvironmentType;
  variables: EnvironmentVariable[];
  created_at: string;
  updated_at: string;
}

export interface EnvironmentCreate {
  name: string;
  description?: string;
  type: EnvironmentType;
}

export interface EnvironmentUpdate {
  name?: string;
  description?: string;
  type?: EnvironmentType;
}

export interface EnvironmentVariableCreate {
  key: string;
  value: string;
  is_secret: boolean;
}

export interface EnvironmentVariableUpdate {
  key?: string;
  value?: string;
  is_secret?: boolean;
}
