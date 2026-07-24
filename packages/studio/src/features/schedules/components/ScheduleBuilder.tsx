import React, { useState } from 'react';
import { ScheduleType } from '../../../types/schedule';
import { Input } from '../../../components/ui/input';
import { Button } from '../../../components/ui/button';

interface ScheduleBuilderProps {
  value: string;
  type: ScheduleType;
  onChange: (value: string, type: ScheduleType) => void;
  maxRetries?: number;
  onMaxRetriesChange?: (val: number) => void;
  retryDelaySeconds?: number;
  onRetryDelaySecondsChange?: (val: number) => void;
  holidayCalendar?: string;
  onHolidayCalendarChange?: (val: string) => void;
  blackoutWindows?: any[];
  onBlackoutWindowsChange?: (val: any[]) => void;
}

export const ScheduleBuilder: React.FC<ScheduleBuilderProps> = ({ 
  value, type, onChange,
  maxRetries = 0, onMaxRetriesChange,
  retryDelaySeconds = 300, onRetryDelaySecondsChange,
  holidayCalendar = '', onHolidayCalendarChange,
  blackoutWindows = [], onBlackoutWindowsChange
}) => {
  const [cronExpression, setCronExpression] = useState(type === ScheduleType.CRON ? value : '* * * * *');
  const [intervalMinutes, setIntervalMinutes] = useState(type === ScheduleType.INTERVAL ? String(Number(value) / 60) : '60');
  
  const handleTypeChange = (newType: ScheduleType) => {
    if (newType === ScheduleType.CRON) {
      onChange(cronExpression, newType);
    } else if (newType === ScheduleType.INTERVAL) {
      onChange(String(Number(intervalMinutes) * 60), newType);
    } else {
      onChange('', newType);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex gap-2 p-1 bg-zinc-900 border border-white/5 rounded-lg w-fit">
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={() => handleTypeChange(ScheduleType.CRON)}
          className={type === ScheduleType.CRON ? 'bg-zinc-800 text-white' : 'text-zinc-500'}
        >
          Cron
        </Button>
        <Button 
          variant="ghost" 
          size="sm"
          onClick={() => handleTypeChange(ScheduleType.INTERVAL)}
          className={type === ScheduleType.INTERVAL ? 'bg-zinc-800 text-white' : 'text-zinc-500'}
        >
          Interval
        </Button>
        <Button 
          variant="ghost" 
          size="sm"
          onClick={() => handleTypeChange(ScheduleType.MANUAL)}
          className={type === ScheduleType.MANUAL ? 'bg-zinc-800 text-white' : 'text-zinc-500'}
        >
          Manual
        </Button>
      </div>

      <div className="p-4 bg-zinc-950/50 border border-white/5 rounded-xl">
        {type === ScheduleType.CRON && (
          <div className="space-y-4">
            <div>
              <label className="text-sm text-zinc-400 mb-1 block">Cron Expression</label>
              <Input 
                value={cronExpression} 
                onChange={(e) => {
                  setCronExpression(e.target.value);
                  onChange(e.target.value, ScheduleType.CRON);
                }}
                className="bg-zinc-900 border-white/10 font-mono"
              />
            </div>
            <div className="text-sm text-emerald-500 bg-emerald-500/10 p-3 rounded-lg border border-emerald-500/20">
              {/* Normally we'd use cronstrue to generate human readable string here */}
              Runs according to standard cron syntax (minute hour day month day_of_week)
            </div>
          </div>
        )}

        {type === ScheduleType.INTERVAL && (
          <div className="space-y-4">
            <div>
              <label className="text-sm text-zinc-400 mb-1 block">Interval (Minutes)</label>
              <Input 
                type="number"
                value={intervalMinutes} 
                onChange={(e) => {
                  setIntervalMinutes(e.target.value);
                  onChange(String(Number(e.target.value) * 60), ScheduleType.INTERVAL);
                }}
                className="bg-zinc-900 border-white/10"
              />
            </div>
          </div>
        )}

        {type === ScheduleType.MANUAL && (
          <div className="text-sm text-zinc-500 py-4 text-center">
            This schedule will only run when triggered manually via API or Studio.
          </div>
        )}
      </div>

      <div className="p-4 bg-zinc-950/50 border border-white/5 rounded-xl space-y-6">
        <h3 className="text-sm font-medium text-white mb-2">Advanced Configuration</h3>
        
        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="block text-sm text-zinc-400 mb-1">Max Retries</label>
            <Input 
              type="number"
              value={maxRetries} 
              onChange={e => onMaxRetriesChange?.(Number(e.target.value))} 
              className="bg-zinc-900 border-white/10"
              min="0"
              max="10"
            />
          </div>
          <div>
            <label className="block text-sm text-zinc-400 mb-1">Retry Delay (Seconds)</label>
            <Input 
              type="number"
              value={retryDelaySeconds} 
              onChange={e => onRetryDelaySecondsChange?.(Number(e.target.value))} 
              className="bg-zinc-900 border-white/10"
              min="0"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm text-zinc-400 mb-1">Holiday Calendar To Skip</label>
          <select 
            value={holidayCalendar}
            onChange={e => onHolidayCalendarChange?.(e.target.value)}
            className="w-full h-10 px-3 rounded-md bg-zinc-900 border border-white/10 text-sm text-white focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">None (Run on Holidays)</option>
            <option value="US">United States (US)</option>
            <option value="UK">United Kingdom (UK)</option>
            <option value="IN">India (IN)</option>
            <option value="CA">Canada (CA)</option>
            <option value="AU">Australia (AU)</option>
          </select>
          <p className="text-xs text-zinc-500 mt-1">Runs will be skipped if they fall on a public holiday in the selected calendar.</p>
        </div>

        <div>
          <label className="block text-sm text-zinc-400 mb-1">Blackout Windows</label>
          <div className="text-sm text-zinc-500 bg-zinc-900 p-3 rounded-md border border-white/5">
            {blackoutWindows.length === 0 ? "No blackout windows configured." : `${blackoutWindows.length} windows active.`}
            {/* Real implementation would have an Add/Remove list for time ranges here */}
          </div>
        </div>
      </div>
    </div>
  );
};
