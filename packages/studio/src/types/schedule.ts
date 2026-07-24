export enum ScheduleStatus {
  ACTIVE = 'ACTIVE',
  PAUSED = 'PAUSED',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED'
}

export enum ScheduleType {
  CRON = 'CRON',
  INTERVAL = 'INTERVAL',
  ONE_TIME = 'ONE_TIME',
  MANUAL = 'MANUAL',
  EVENT = 'EVENT'
}

export interface Schedule {
  id: string;
  name: string;
  description?: string;
  pipeline_id: string;
  type: ScheduleType;
  expression?: string;
  timezone: string;
  status: ScheduleStatus;
  next_run_at?: string;
  last_run_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ScheduleRunHistory {
  id: string;
  schedule_id: string;
  execution_id: string;
  triggered_at: string;
  status: string;
}
