import React, { useMemo, useState, useRef, useEffect } from 'react';
import { ExecutionResponse } from '../../../api/executions';
import { useVirtualizer } from '@tanstack/react-virtual';
import { Search, Download, Copy, Play, Pause, Info, Filter, Check } from 'lucide-react';
import { Input } from '../../../components/ui/input';
import { Button } from '../../../components/ui/button';
import { toast } from 'sonner';
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator } from '../../../components/ui/dropdown-menu';

interface ExecutionLogsProps {
  run: ExecutionResponse;
}

type LogLevel = 'INFO' | 'WARN' | 'ERROR' | 'DEBUG' | 'UNKNOWN';

interface ParsedLog {
  timestamp: string;
  level: LogLevel;
  text: string;
  step: string;
  raw: string;
}

export const ExecutionLogs: React.FC<ExecutionLogsProps> = ({ run }) => {
  const [search, setSearch] = useState('');
  const [autoScroll, setAutoScroll] = useState(true);
  const [levels, setLevels] = useState<Record<LogLevel, boolean>>({
    INFO: true,
    WARN: true,
    ERROR: true,
    DEBUG: true,
    UNKNOWN: true
  });
  
  const parentRef = useRef<HTMLDivElement>(null);

  const allLogs = useMemo(() => {
    const logsList: ParsedLog[] = [];
    
    if (run.steps) {
      Object.entries(run.steps).forEach(([stepId, stepRun]) => {
        if (stepRun.logs && stepRun.logs.length > 0) {
          stepRun.logs.forEach(logLine => {
            let level: LogLevel = 'UNKNOWN';
            const upperLine = logLine.toUpperCase();
            if (upperLine.includes('ERROR') || upperLine.includes('CRITICAL')) level = 'ERROR';
            else if (upperLine.includes('WARN')) level = 'WARN';
            else if (upperLine.includes('INFO')) level = 'INFO';
            else if (upperLine.includes('DEBUG')) level = 'DEBUG';
            
            // basic timestamp extraction if present, e.g. [2026-08-01 12:00:00]
            const timeMatch = logLine.match(/\[(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\]/);
            const timestamp = timeMatch ? timeMatch[1] : '';

            logsList.push({
              timestamp,
              level,
              text: logLine,
              step: stepId,
              raw: logLine
            });
          });
        }
      });
    }
    
    // Sort chronologically by timestamp if available, else retain order
    return logsList.sort((a, b) => {
       if (a.timestamp && b.timestamp) return new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
       return 0;
    });
  }, [run.steps]);

  const filteredLogs = useMemo(() => {
    return allLogs.filter(log => {
      if (!levels[log.level]) return false;
      if (search && !log.raw.toLowerCase().includes(search.toLowerCase()) && !log.step.toLowerCase().includes(search.toLowerCase())) return false;
      return true;
    });
  }, [allLogs, search, levels]);

  const rowVirtualizer = useVirtualizer({
    count: filteredLogs.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 24, // 24px height per line
    overscan: 20,
  });

  useEffect(() => {
    if (autoScroll && filteredLogs.length > 0) {
      rowVirtualizer.scrollToIndex(filteredLogs.length - 1, { align: 'end' });
    }
  }, [filteredLogs.length, autoScroll, rowVirtualizer]);

  const handleCopy = () => {
    const text = filteredLogs.map(l => l.raw).join('\n');
    navigator.clipboard.writeText(text);
    toast.success('Logs copied to clipboard');
  };

  const handleDownload = () => {
    const text = filteredLogs.map(l => l.raw).join('\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `logs-${run.run_id}.txt`;
    a.click();
  };

  const getLevelColor = (level: LogLevel) => {
    switch (level) {
      case 'ERROR': return 'text-red-500';
      case 'WARN': return 'text-amber-500';
      case 'INFO': return 'text-blue-400';
      case 'DEBUG': return 'text-gray-400';
      default: return 'text-green-400';
    }
  };

  return (
    <div className="h-full flex flex-col min-h-[500px] border-b bg-black/95 text-gray-300 font-mono text-sm relative">
      <div className="flex items-center justify-between p-2 bg-black border-b border-white/10 shrink-0">
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-2 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <Input 
              placeholder="Search logs..." 
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="pl-8 h-8 w-64 bg-white/5 border-white/10 text-white placeholder:text-gray-500 text-xs font-sans"
            />
          </div>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="h-8 gap-2 bg-white/5 border-white/10 text-white hover:bg-white/10 hover:text-white font-sans text-xs">
                <Filter className="w-3.5 h-3.5" /> Levels
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-40">
              <DropdownMenuLabel>Severity</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {(Object.keys(levels) as LogLevel[]).map(level => (
                <DropdownMenuItem 
                  key={level}
                  onClick={(e) => {
                    e.preventDefault();
                    setLevels(prev => ({ ...prev, [level]: !prev[level] }));
                  }}
                  className="flex items-center gap-2 cursor-pointer"
                >
                  <div className="w-4 h-4 border rounded flex items-center justify-center">
                    {levels[level] && <Check className="w-3 h-3" />}
                  </div>
                  {level}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        
        <div className="flex items-center gap-2">
          <Button 
            onClick={() => setAutoScroll(!autoScroll)} 
            size="sm" 
            variant="outline"
            className={`h-8 gap-2 bg-white/5 border-white/10 text-white hover:bg-white/10 hover:text-white font-sans text-xs ${autoScroll ? 'bg-primary/20 text-primary border-primary/50' : ''}`}
          >
            {autoScroll ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            Auto-scroll
          </Button>
          
          <div className="w-px h-4 bg-white/10 mx-1" />
          
          <Button variant="ghost" size="icon" className="h-8 w-8 text-gray-400 hover:text-white hover:bg-white/10" onClick={handleCopy} title="Copy logs">
            <Copy className="w-3.5 h-3.5" />
          </Button>
          <Button variant="ghost" size="icon" className="h-8 w-8 text-gray-400 hover:text-white hover:bg-white/10" onClick={handleDownload} title="Download logs">
            <Download className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>
      
      <div 
        ref={parentRef} 
        className="flex-1 overflow-auto custom-scrollbar p-2"
        onScroll={(e) => {
          const target = e.target as HTMLDivElement;
          const isAtBottom = Math.abs(target.scrollHeight - target.clientHeight - target.scrollTop) < 5;
          if (autoScroll && !isAtBottom) setAutoScroll(false);
          else if (!autoScroll && isAtBottom) setAutoScroll(true);
        }}
      >
        {filteredLogs.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-500 font-sans">
            <Info className="w-6 h-6 mb-2 opacity-50" />
            <p>No logs found.</p>
          </div>
        ) : (
          <div
            style={{
              height: `${rowVirtualizer.getTotalSize()}px`,
              width: '100%',
              position: 'relative',
            }}
          >
            {rowVirtualizer.getVirtualItems().map((virtualRow) => {
              const log = filteredLogs[virtualRow.index];
              return (
                <div
                  key={virtualRow.index}
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: `${virtualRow.size}px`,
                    transform: `translateY(${virtualRow.start}px)`,
                  }}
                  className="flex items-center hover:bg-white/5 px-2 group whitespace-nowrap overflow-hidden text-[13px] leading-[24px]"
                >
                  <span className="text-gray-500 w-12 shrink-0 inline-block text-right pr-4 select-none border-r border-white/10 mr-4">
                    {virtualRow.index + 1}
                  </span>
                  
                  {log.timestamp && (
                    <span className="text-gray-500 mr-3 shrink-0">
                      {log.timestamp}
                    </span>
                  )}
                  
                  <span className={`w-14 shrink-0 font-bold ${getLevelColor(log.level)} mr-3`}>
                    {log.level}
                  </span>
                  
                  <span className="text-purple-400 mr-3 shrink-0">
                    [{log.step}]
                  </span>
                  
                  <span className="text-gray-300 group-hover:text-white truncate">
                    {log.raw}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
