import React, { useState } from 'react';
import { useCreateSchedule } from '../hooks/useSchedules';
import { ScheduleType } from '../../../types/schedule';
import { ScheduleBuilder } from './ScheduleBuilder';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { usePipelines } from '../../pipelines/hooks/usePipelines';

interface ScheduleFormDialogProps {
  onClose: () => void;
  initialData?: any;
}

export const ScheduleFormDialog: React.FC<ScheduleFormDialogProps> = ({ onClose, initialData }) => {
  const [name, setName] = useState(initialData ? `Copy of ${initialData.name}` : '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [pipelineId, setPipelineId] = useState(initialData?.pipeline_id || '');
  const [type, setType] = useState<ScheduleType>(initialData?.type || ScheduleType.CRON);
  const [expression, setExpression] = useState(initialData?.type === ScheduleType.CRON ? initialData.expression : '0 * * * *');
  const [maxRetries, setMaxRetries] = useState(initialData?.max_retries || 0);
  const [retryDelaySeconds, setRetryDelaySeconds] = useState(initialData?.retry_delay_seconds || 300);
  const [holidayCalendar, setHolidayCalendar] = useState<string>(initialData?.holiday_calendar || '');
  const [blackoutWindows] = useState<any[]>(initialData?.blackout_windows || []);
  const [timezone, setTimezone] = useState(initialData?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC');
  
  const createMutation = useCreateSchedule();
  const { data: pipelines } = usePipelines();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(
      {
        name,
        description,
        pipeline_id: pipelineId,
        type,
        expression,
        timezone,
        max_retries: maxRetries,
        retry_delay_seconds: retryDelaySeconds,
        holiday_calendar: holidayCalendar || undefined,
        blackout_windows: blackoutWindows
      },
      {
        onSuccess: () => {
          onClose();
        }
      }
    );
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-zinc-950 border border-white/10 rounded-xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl">
        <div className="p-6 border-b border-white/5 shrink-0">
          <h2 className="text-xl font-semibold text-white">Create Schedule</h2>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-6 overflow-y-auto flex-1 custom-scrollbar">
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-4 col-span-2 md:col-span-1">
              <div>
                <label className="block text-sm text-zinc-400 mb-1">Name</label>
                <Input 
                  required 
                  value={name} 
                  onChange={e => setName(e.target.value)} 
                  className="bg-zinc-900 border-white/10"
                  placeholder="Daily ETL Run"
                />
              </div>
              <div>
                <label className="block text-sm text-zinc-400 mb-1">Pipeline</label>
                <select 
                  required
                  value={pipelineId}
                  onChange={e => setPipelineId(e.target.value)}
                  className="w-full h-10 px-3 rounded-md bg-zinc-900 border border-white/10 text-sm text-white focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="" disabled>Select a pipeline</option>
                  {pipelines?.items?.map(p => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                  {/* Fallback if it's an array */}
                  {Array.isArray(pipelines) && pipelines.map(p => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="space-y-4 col-span-2 md:col-span-1">
              <div>
                <label className="block text-sm text-zinc-400 mb-1">Description (Optional)</label>
                <Input 
                  value={description} 
                  onChange={e => setDescription(e.target.value)} 
                  className="bg-zinc-900 border-white/10"
                />
              </div>
              <div>
                <label className="block text-sm text-zinc-400 mb-1">Timezone</label>
                <select
                  required
                  value={timezone}
                  onChange={e => setTimezone(e.target.value)}
                  className="w-full h-10 px-3 rounded-md bg-zinc-900 border border-white/10 text-sm text-white focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="UTC">UTC (Coordinated Universal Time)</option>
                  <option value="America/New_York">Eastern Time (US & Canada)</option>
                  <option value="America/Chicago">Central Time (US & Canada)</option>
                  <option value="America/Denver">Mountain Time (US & Canada)</option>
                  <option value="America/Los_Angeles">Pacific Time (US & Canada)</option>
                  <option value="Europe/London">London (GMT/BST)</option>
                  <option value="Europe/Paris">Central European Time (CET/CEST)</option>
                  <option value="Asia/Tokyo">Japan Standard Time (JST)</option>
                  <option value="Asia/Kolkata">India Standard Time (IST)</option>
                  <option value="Australia/Sydney">Australian Eastern Time (AET)</option>
                  <option value={Intl.DateTimeFormat().resolvedOptions().timeZone}>
                    Local Time ({Intl.DateTimeFormat().resolvedOptions().timeZone})
                  </option>
                </select>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-white mb-3">Schedule Configuration</label>
            <ScheduleBuilder 
              type={type} 
              value={expression} 
              onChange={(val, newType) => {
                setExpression(val);
                setType(newType);
              }} 
              maxRetries={maxRetries}
              onMaxRetriesChange={setMaxRetries}
              retryDelaySeconds={retryDelaySeconds}
              onRetryDelaySecondsChange={setRetryDelaySeconds}
              holidayCalendar={holidayCalendar}
              onHolidayCalendarChange={setHolidayCalendar}
              blackoutWindows={blackoutWindows}
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-white/5 shrink-0 mt-auto">
            <Button type="button" variant="ghost" onClick={onClose}>Cancel</Button>
            <Button 
              type="submit" 
              className="bg-emerald-600 hover:bg-emerald-700 text-white"
              disabled={createMutation.isPending || !pipelineId}
            >
              {createMutation.isPending ? 'Creating...' : 'Create Schedule'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
