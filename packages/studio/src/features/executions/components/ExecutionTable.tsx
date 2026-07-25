import React from 'react';
import { useNavigate } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { PipelineStatusBadge } from '../../pipelines/components/PipelineStatusBadge';
import { Skeleton } from '../../../components/ui/skeleton';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../../components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../../components/ui/table';
import { ExecutionResponse } from '../../../api/executions';
import { Progress } from '../../../components/ui/progress';

interface ExecutionTableProps {
  runs: ExecutionResponse[];
  title?: string;
  description?: string;
  loading?: boolean;
}

export const ExecutionTable: React.FC<ExecutionTableProps> = ({ 
  runs, 
  title = "Recent Executions", 
  description = "The latest pipeline runs", 
  loading = false 
}) => {
  const navigate = useNavigate();

  const calculateProgress = (run: ExecutionResponse) => {
    if (run.status === 'COMPLETED') return 100;
    if (['FAILED', 'CANCELLED'].includes(run.status)) return 100; // or 0? 
    const totalSteps = Object.keys(run.steps || {}).length;
    if (totalSteps === 0) return 0;
    const completedSteps = Object.values(run.steps || {}).filter(
      s => s.status === 'COMPLETED'
    ).length;
    return Math.round((completedSteps / totalSteps) * 100);
  };

  return (
    <Card className="col-span-3 border-muted bg-card shadow-sm h-full">
      {(title || description) && (
        <CardHeader className="pb-3 border-b border-border/40">
          {title && <CardTitle className="text-lg">{title}</CardTitle>}
          {description && <CardDescription>{description}</CardDescription>}
        </CardHeader>
      )}
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow className="bg-muted/30">
              <TableHead className="font-semibold">Pipeline ID</TableHead>
              <TableHead className="font-semibold">Status</TableHead>
              <TableHead className="font-semibold">Progress</TableHead>
              <TableHead className="font-semibold">Duration</TableHead>
              <TableHead className="font-semibold">Started</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-20 rounded-full" /></TableCell>
                  <TableCell><Skeleton className="h-2 w-24" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-28" /></TableCell>
                </TableRow>
              ))
            ) : runs.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="h-32 text-center text-muted-foreground">
                  <div className="flex flex-col items-center justify-center space-y-2">
                    <span className="text-sm">No executions found</span>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              runs.map((run, i) => {
                const progress = calculateProgress(run);
                return (
                  <TableRow 
                    key={i} 
                    className="cursor-pointer group hover:bg-muted/50 transition-colors"
                    onClick={() => navigate(`/runs/${(run as any).id || run.run_id}`)}
                  >
                    <TableCell className="font-medium text-foreground/90 group-hover:text-foreground">
                      {run.pipeline_id}
                    </TableCell>
                    <TableCell>
                      <PipelineStatusBadge status={run.status} />
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Progress value={progress} className="h-2 w-24" />
                        <span className="text-xs text-muted-foreground">{progress}%</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {run.duration_ms ? `${(run.duration_ms / 1000).toFixed(1)}s` : '-'}
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {run.started_at 
                        ? formatDistanceToNow(new Date(run.started_at), { addSuffix: true }) 
                        : (run.submitted_at ? formatDistanceToNow(new Date(run.submitted_at), { addSuffix: true }) : 'N/A')}
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
};
