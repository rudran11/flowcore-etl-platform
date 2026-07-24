import React, { useMemo } from 'react';
import { ExecutionResponse } from '../../../api/executions';
import { ScrollArea } from '../../../components/ui/scroll-area';

interface ExecutionLogsProps {
  run: ExecutionResponse;
}

export const ExecutionLogs: React.FC<ExecutionLogsProps> = ({ run }) => {
  const allLogs = useMemo(() => {
    const logsList: { timestamp: number, text: string, step: string }[] = [];
    
    if (run.steps) {
      Object.entries(run.steps).forEach(([stepId, stepRun]) => {
        if (stepRun.logs && stepRun.logs.length > 0) {
          stepRun.logs.forEach(logLine => {
            // Very simple parsing of timestamp if logLine is a JSON string or has a prefix
            // For now just assume they are raw lines and sort them if they have timestamps
            logsList.push({
              timestamp: Date.now(), // dummy fallback
              text: logLine,
              step: stepId
            });
          });
        }
      });
    }
    
    // Sort logic would go here if timestamps existed
    return logsList;
  }, [run.steps]);

  if (allLogs.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-muted-foreground p-12 bg-black/90 rounded-xl">
        <span className="font-mono">Waiting for logs...</span>
      </div>
    );
  }

  return (
    <div className="h-full w-full min-h-[500px] bg-black/95 text-green-400 font-mono text-sm rounded-xl overflow-hidden border">
      <ScrollArea className="h-full w-full p-4">
        {allLogs.map((log, index) => (
          <div key={index} className="mb-1 opacity-90 hover:opacity-100 transition-opacity">
            <span className="text-blue-400 mr-2">[{log.step}]</span>
            <span>{log.text}</span>
          </div>
        ))}
      </ScrollArea>
    </div>
  );
};
