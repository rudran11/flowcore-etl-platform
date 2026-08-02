import React from 'react';
import { useNavigate } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { PipelineStatusBadge } from '../../pipelines/components/PipelineStatusBadge';
import { Skeleton } from '../../../components/ui/skeleton';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../../components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../../components/ui/table';
import { ExecutionResponse } from '../../../api/executions';
import { Progress } from '../../../components/ui/progress';
import { Button } from '../../../components/ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from '../../../components/ui/dropdown-menu';
import { MoreHorizontal, Download, GitMerge, FileText, Play, Activity } from 'lucide-react';
import { toast } from 'sonner';

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
    <div className="w-full h-full">
      {(title || description) && (
        <div className="pb-3 mb-4 border-b border-border/40 px-2">
          {title && <h3 className="text-lg font-semibold">{title}</h3>}
          {description && <p className="text-sm text-muted-foreground">{description}</p>}
        </div>
      )}
      <div className="p-0">
        <Table>
          <TableHeader>
            <TableRow className="bg-muted/30">
              <TableHead className="font-semibold">Pipeline ID</TableHead>
              <TableHead className="font-semibold">Status</TableHead>
              <TableHead className="font-semibold">Progress</TableHead>
              <TableHead className="font-semibold">Duration</TableHead>
              <TableHead className="font-semibold">Started</TableHead>
              <TableHead className="w-[50px]"></TableHead>
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
                  <TableCell><Skeleton className="h-8 w-8 rounded-md" /></TableCell>
                </TableRow>
              ))
            ) : runs.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="h-48 text-center text-muted-foreground">
                  <div className="flex flex-col items-center justify-center space-y-3">
                    <Activity className="h-10 w-10 text-muted-foreground/30" />
                    <div className="text-lg font-medium text-foreground">No executions found</div>
                    <div className="text-sm">We couldn't find any executions matching your criteria.</div>
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
                    <TableCell onClick={(e) => e.stopPropagation()}>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" className="h-8 w-8 p-0">
                            <span className="sr-only">Open menu</span>
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => navigate(`/runs/${(run as any).id || run.run_id}?tab=dag`)}>
                            <GitMerge className="mr-2 h-4 w-4" /> View DAG
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => navigate(`/runs/${(run as any).id || run.run_id}?tab=logs`)}>
                            <FileText className="mr-2 h-4 w-4" /> View Logs
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem onClick={() => {
                            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(run, null, 2));
                            const a = document.createElement('a');
                            a.setAttribute("href", dataStr);
                            a.setAttribute("download", `execution-${run.run_id}.json`);
                            document.body.appendChild(a);
                            a.click();
                            a.remove();
                            toast.success('Execution JSON exported');
                          }}>
                            <Download className="mr-2 h-4 w-4" /> Export JSON
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => {
                             // Wait for milestone 12 for full re-run backend implementation
                             toast.info("Re-run capability is planned for the next backend release.");
                          }}>
                            <Play className="mr-2 h-4 w-4" /> Re-run Pipeline
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};
