export interface DashboardStatistics {
  total_pipelines: number;
  total_runs: number;
  success_rate: number;
  avg_duration_ms: number;
}

export interface ExecutionSummary {
  completed: number;
  failed: number;
  running: number;
  cancelled: number;
  queued: number;
}

export interface ExecutionTrend {
  date: string;
  completed: number;
  failed: number;
  running: number;
  cancelled: number;
  queued: number;
}

export interface SystemHealth {
  server: string;
  database: string;
  engine: string;
  api: string;
  version: string;
}

export interface DashboardResponse {
  statistics: DashboardStatistics;
  execution_summary: ExecutionSummary;
  trends: ExecutionTrend[];
  recent_runs: any[]; // using any[] for now, or import ExecutionRun from elsewhere
  health: SystemHealth;
  generated_at: string;
}
