export interface PluginResponse {
  plugin_id: string;
  name: string;
  version: string;
  plugin_type: string;
  author?: string;
  description?: string;
  category: string;
  capabilities: string[];
  supported_operations: string[];
  example_yaml?: string;
  documentation?: string;
  compatibility: string;
  dependencies: string[];
  config_schema?: Record<string, any>;
}

export interface PluginValidationRequest {
  plugin_id: string;
  config: Record<string, any>;
}

export interface PluginValidationResponse {
  success: boolean;
  warnings: string[];
  errors: string[];
}

export interface PluginHealthResponse {
  status: string;
  diagnostics: string[];
}

export interface PluginStatsResponse {
  total: number;
  healthy: number;
  unhealthy: number;
  disabled: number;
}
