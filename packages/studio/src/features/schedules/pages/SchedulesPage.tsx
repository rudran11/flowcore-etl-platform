import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Plus, Clock, Search, Play, Pause, Trash2, CalendarClock, MoreVertical } from 'lucide-react';
import { useSchedules, usePauseSchedule, useResumeSchedule, useTriggerSchedule, useDeleteSchedule } from '../hooks/useSchedules';
import { ScheduleStatus, ScheduleType } from '../../../types/schedule';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Badge } from '../../../components/ui/badge';
import { Skeleton } from '../../../components/ui/skeleton';
import { formatDistanceToNow } from 'date-fns';
import { ScheduleFormDialog } from '../components/ScheduleFormDialog';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '../../../components/ui/dropdown-menu';
import { PageHeader } from '../../../components/ui/page-header';
import { StatCard } from '../../../components/ui/stat-card';
import { EmptyState } from '../../../components/ui/empty-state';

export const SchedulesPage: React.FC = () => {
  const { data: schedules, isLoading } = useSchedules();
  const [search, setSearch] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [viewMode, setViewMode] = useState<'list' | 'calendar'>('list');
  const [cloneData, setCloneData] = useState<any>(null);

  const pauseMutation = usePauseSchedule();
  const resumeMutation = useResumeSchedule();
  const triggerMutation = useTriggerSchedule();
  const deleteMutation = useDeleteSchedule();

  const filteredSchedules = schedules?.filter((s: any) => 
    s.name.toLowerCase().includes(search.toLowerCase())
  ) || [];

  const getStatusColor = (status: ScheduleStatus) => {
    switch (status) {
      case ScheduleStatus.ACTIVE: return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20';
      case ScheduleStatus.PAUSED: return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
      case ScheduleStatus.COMPLETED: return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
      case ScheduleStatus.FAILED: return 'bg-rose-500/10 text-rose-500 border-rose-500/20';
      default: return 'bg-zinc-500/10 text-zinc-500 border-zinc-500/20';
    }
  };

  return (
    <div className="flex-1 flex flex-col p-6 md:p-8 max-w-[1400px] mx-auto w-full space-y-8 animate-in fade-in duration-500">
      <PageHeader
        title="Schedules"
        subtitle="Automate and monitor your pipeline executions."
        icon={CalendarClock}
        actions={
          <Button onClick={() => setIsCreateOpen(true)} className="shadow-md">
            <Plus className="mr-2 h-4 w-4" /> Create Schedule
          </Button>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard 
          title="Total Schedules" 
          value={schedules?.length || 0} 
          icon={<CalendarClock className="h-4 w-4" />}
          description="Configured in the system"
        />
        <StatCard 
          title="Active Schedules" 
          value={schedules?.filter((s: any) => s.status === ScheduleStatus.ACTIVE).length || 0} 
          icon={<Clock className="h-4 w-4" />}
          description="Currently running"
          trend="up"
          trendValue="Healthy"
        />
        <StatCard 
          title="Paused Schedules" 
          value={schedules?.filter((s: any) => s.status === ScheduleStatus.PAUSED).length || 0} 
          icon={<Pause className="h-4 w-4" />}
          description="Manually suspended"
        />
      </div>

      <div className="flex items-center justify-between mb-6">
        <div className="relative w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <Input 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search schedules..." 
            className="pl-9 bg-zinc-950/50 border-white/5"
          />
        </div>
        <div className="flex bg-zinc-950/50 border border-white/5 rounded-lg p-1">
          <button 
            onClick={() => setViewMode('list')}
            className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${viewMode === 'list' ? 'bg-zinc-800 text-white' : 'text-zinc-500 hover:text-zinc-300'}`}
          >
            List
          </button>
          <button 
            onClick={() => setViewMode('calendar')}
            className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${viewMode === 'calendar' ? 'bg-zinc-800 text-white' : 'text-zinc-500 hover:text-zinc-300'}`}
          >
            Calendar
          </button>
        </div>
      </div>

      {viewMode === 'calendar' && (
        <div className="bg-zinc-950/50 border border-white/5 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white">Execution Calendar (Current Month)</h3>
          </div>
          <div className="grid grid-cols-7 gap-px bg-white/5 border border-white/5 rounded-lg overflow-hidden">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
              <div key={day} className="bg-zinc-950 p-2 text-center text-xs font-medium text-zinc-500 uppercase tracking-wider">
                {day}
              </div>
            ))}
            {/* Generate simple 35 day grid for demo purposes */}
            {Array.from({ length: 35 }).map((_, i) => {
              const day = i - 2; // Offset for month start
              const isCurrentMonth = day > 0 && day <= 31;
              const hasRun = isCurrentMonth && (day % 3 === 0 || day === 15); // Mock runs
              
              return (
                <div key={i} className={`bg-zinc-950 min-h-[100px] p-2 border-t border-white/5 ${!isCurrentMonth ? 'opacity-30' : 'hover:bg-white/[0.02]'}`}>
                  <div className="text-sm text-zinc-500 mb-2">{isCurrentMonth ? day : ''}</div>
                  {hasRun && (
                    <div className="space-y-1">
                      {filteredSchedules.slice(0, (day % 2 === 0 ? 1 : 2)).map((s: any) => (
                        <div key={s.id} className="text-[10px] px-1.5 py-1 rounded bg-emerald-500/10 text-emerald-500 truncate border border-emerald-500/20">
                          {s.name}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {viewMode === 'list' && (
        <div className="bg-card/50 backdrop-blur-sm border border-border/50 rounded-xl overflow-hidden shadow-sm">
          {isLoading ? (
            <div className="p-4 space-y-4">
            {[1,2,3].map(i => <Skeleton key={i} className="h-16 w-full rounded-lg" />)}
          </div>
        ) : filteredSchedules.length === 0 ? (
          <EmptyState 
            icon={CalendarClock}
            title="No schedules found"
            description="Create a schedule to run your pipelines automatically."
            action={
              <Button onClick={() => setIsCreateOpen(true)} variant="outline">
                <Plus className="mr-2 h-4 w-4" /> Create your first schedule
              </Button>
            }
          />
        ) : (
          <div className="divide-y divide-white/5">
            {filteredSchedules.map((schedule: any) => (
              <motion.div 
                key={schedule.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center justify-between p-4 hover:bg-white/[0.02] transition-colors group"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-zinc-900 border border-white/5 flex items-center justify-center shrink-0">
                    <Clock className="w-5 h-5 text-zinc-400" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-white">{schedule.name}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="outline" className={`text-[10px] uppercase font-semibold tracking-wider ${getStatusColor(schedule.status)}`}>
                        {schedule.status}
                      </Badge>
                      <span className="text-xs text-zinc-500">•</span>
                      <span className="text-xs text-zinc-500 font-mono">{schedule.type === ScheduleType.CRON ? schedule.expression : schedule.type}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-8">
                  <div className="hidden md:block text-right">
                    <div className="text-xs text-zinc-500 mb-1">Last Run</div>
                    <div className="text-sm text-zinc-300">
                      {schedule.last_run_at ? formatDistanceToNow(new Date(schedule.last_run_at), { addSuffix: true }) : 'Never'}
                    </div>
                  </div>
                  
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-8 w-8 text-zinc-500 hover:text-white">
                        <MoreVertical className="w-4 h-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-48">
                      {schedule.status === ScheduleStatus.ACTIVE ? (
                        <DropdownMenuItem onClick={() => pauseMutation.mutate(schedule.id)}>
                          <Pause className="w-4 h-4 mr-2" /> Pause Schedule
                        </DropdownMenuItem>
                      ) : (
                        <DropdownMenuItem onClick={() => resumeMutation.mutate(schedule.id)}>
                          <Play className="w-4 h-4 mr-2" /> Resume Schedule
                        </DropdownMenuItem>
                      )}
                      <DropdownMenuItem onClick={() => triggerMutation.mutate(schedule.id)}>
                        <Play className="w-4 h-4 mr-2" /> Trigger Now
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => {
                        setCloneData(schedule);
                        setIsCreateOpen(true);
                      }}>
                        <Plus className="w-4 h-4 mr-2" /> Clone Schedule
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem className="text-rose-500 focus:text-rose-500" onClick={() => deleteMutation.mutate(schedule.id)}>
                        <Trash2 className="w-4 h-4 mr-2" /> Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
      )}

      {isCreateOpen && (
        <ScheduleFormDialog 
          onClose={() => {
            setIsCreateOpen(false);
            setCloneData(null);
          }} 
          initialData={cloneData}
        />
      )}
    </div>
  );
};
