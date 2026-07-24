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
  max_retries?: number;
  retry_delay_seconds?: number;
  holiday_calendar?: string;
  blackout_windows?: any[];
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
