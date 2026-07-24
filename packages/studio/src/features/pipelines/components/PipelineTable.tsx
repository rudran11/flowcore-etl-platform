import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Skeleton } from '../../../components/ui/skeleton';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../../components/ui/table';
import { Badge } from '../../../components/ui/badge';
import { Database, User } from 'lucide-react';

interface Pipeline {
  id: string;
  name: string;
  owner: string;
  description?: string;
  tags: string[];
}

interface PipelineTableProps {
  pipelines: Pipeline[];
  loading?: boolean;
}

export const PipelineTable: React.FC<PipelineTableProps> = ({ pipelines, loading = false }) => {
  const navigate = useNavigate();

  return (
    <Table>
      <TableHeader>
        <TableRow className="bg-muted/30">
          <TableHead className="w-[300px] font-semibold">Name</TableHead>
          <TableHead className="font-semibold">Owner</TableHead>
          <TableHead className="font-semibold">Description</TableHead>
          <TableHead className="font-semibold">Tags</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {loading ? (
          Array.from({ length: 5 }).map((_, i) => (
            <TableRow key={i}>
              <TableCell><Skeleton className="h-4 w-40" /></TableCell>
              <TableCell><Skeleton className="h-4 w-24" /></TableCell>
              <TableCell><Skeleton className="h-4 w-64" /></TableCell>
              <TableCell><Skeleton className="h-5 w-20 rounded-full" /></TableCell>
            </TableRow>
          ))
        ) : pipelines.length === 0 ? (
          <TableRow>
            <TableCell colSpan={4} className="h-48 text-center text-muted-foreground">
              <div className="flex flex-col items-center justify-center space-y-3">
                <Database className="h-10 w-10 text-muted-foreground/30" />
                <div className="text-lg font-medium text-foreground">No pipelines found</div>
                <div className="text-sm">We couldn't find any pipelines matching your criteria.</div>
              </div>
            </TableCell>
          </TableRow>
        ) : (
          pipelines.map((pipeline) => (
            <TableRow 
              key={pipeline.id} 
              className="cursor-pointer group hover:bg-muted/50 transition-colors"
              onClick={() => navigate(`/pipelines/${pipeline.id}`)}
            >
              <TableCell className="font-medium text-foreground/90 group-hover:text-foreground">
                {pipeline.name}
              </TableCell>
              <TableCell className="text-muted-foreground">
                <div className="flex items-center gap-2">
                  <User className="h-3 w-3" />
                  {pipeline.owner}
                </div>
              </TableCell>
              <TableCell className="text-muted-foreground truncate max-w-xs">
                {pipeline.description || '-'}
              </TableCell>
              <TableCell>
                <div className="flex gap-1.5 flex-wrap">
                  {pipeline.tags && pipeline.tags.length > 0 ? (
                    pipeline.tags.map(tag => (
                      <Badge variant="secondary" key={tag} className="font-normal text-xs">
                        {tag}
                      </Badge>
                    ))
                  ) : (
                    <span className="text-muted-foreground">-</span>
                  )}
                </div>
              </TableCell>
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  );
};
