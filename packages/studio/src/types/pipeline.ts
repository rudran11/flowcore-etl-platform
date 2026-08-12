export interface Pipeline {
  id: string;
  name: string;
  owner: string;
  description?: string;
  tags: string[];
  is_favorite?: boolean;
  is_archived?: boolean;
  folder_id?: string;
}

export interface PipelineVersion {
  id: string;
  pipeline_id: string;
  version: string;
  version_tag?: string;
  steps?: any[];
  dsl_definition?: any;
  graph_definition?: any;
  created_at?: string;
}

export interface PipelinePaginatedResponse {
  items: Pipeline[];
  total: number;
  skip: number;
  limit: number;
}

export interface PipelineDetailResponse {
  pipeline: Pipeline;
  versions: PipelineVersion[];
  recent_runs: any[]; // Or ExecutionRun interface
}

export interface PipelineMetadata {
  trigger: {
    type: string;
    schedule?: string;
  };
  steps: Record<string, any>;
}
