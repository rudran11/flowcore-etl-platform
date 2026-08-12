import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Skeleton } from '../../../components/ui/skeleton';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../../components/ui/table';
import { Badge } from '../../../components/ui/badge';
import { Database, User, MoreHorizontal, Edit2, Copy, Trash2, Folder, Star, Archive as ArchiveIcon } from 'lucide-react';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator, DropdownMenuSub, DropdownMenuSubTrigger, DropdownMenuSubContent } from '../../../components/ui/dropdown-menu';
import { Button } from '../../../components/ui/button';
import { Pipeline } from '../../../types/pipeline';
import { useFolders } from '../hooks/useFolders';

interface PipelineTableProps {
  pipelines: Pipeline[];
  loading?: boolean;
  onRename?: (pipeline: Pipeline) => void;
  onDuplicate?: (pipeline: Pipeline) => void;
  onDelete?: (pipeline: Pipeline) => void;
  onFavorite?: (pipeline: Pipeline, is_favorite: boolean) => void;
  onArchive?: (pipeline: Pipeline, is_archived: boolean) => void;
  onMove?: (pipeline: Pipeline, folder_id: string | null) => void;
}

export const PipelineTable: React.FC<PipelineTableProps> = ({ pipelines, loading = false, onRename, onDuplicate, onDelete, onFavorite, onArchive, onMove }) => {
  const navigate = useNavigate();
  const { data: folders } = useFolders();

  return (
    <Table>
      <TableHeader>
        <TableRow className="bg-muted/30">
          <TableHead className="w-[300px] font-semibold">Name</TableHead>
          <TableHead className="font-semibold">Owner</TableHead>
          <TableHead className="font-semibold">Description</TableHead>
          <TableHead className="font-semibold">Tags</TableHead>
          <TableHead className="w-[50px]"></TableHead>
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
            <TableCell colSpan={5} className="h-48 text-center text-muted-foreground">
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
              <TableCell onClick={(e) => e.stopPropagation()}>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => onRename && onRename(pipeline as any)}>
                      <Edit2 className="h-4 w-4 mr-2" /> Rename
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => onDuplicate && onDuplicate(pipeline as any)}>
                      <Copy className="h-4 w-4 mr-2" /> Duplicate
                    </DropdownMenuItem>
                    
                    <DropdownMenuItem onClick={() => onFavorite && onFavorite(pipeline as any, !pipeline.is_favorite)}>
                      <Star className="h-4 w-4 mr-2" /> {pipeline.is_favorite ? 'Unfavorite' : 'Favorite'}
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => onArchive && onArchive(pipeline as any, !pipeline.is_archived)}>
                      <ArchiveIcon className="h-4 w-4 mr-2" /> {pipeline.is_archived ? 'Unarchive' : 'Archive'}
                    </DropdownMenuItem>

                    <DropdownMenuSub>
                      <DropdownMenuSubTrigger>
                        <Folder className="h-4 w-4 mr-2" /> Move to Folder
                      </DropdownMenuSubTrigger>
                      <DropdownMenuSubContent>
                        <DropdownMenuItem onClick={() => onMove && onMove(pipeline as any, null)}>
                          [Root - No Folder]
                        </DropdownMenuItem>
                        {folders?.map(f => (
                          <DropdownMenuItem key={f.folder.id} onClick={() => onMove && onMove(pipeline as any, f.folder.id)}>
                            <Folder className="h-4 w-4 mr-2" /> {f.folder.name}
                          </DropdownMenuItem>
                        ))}
                      </DropdownMenuSubContent>
                    </DropdownMenuSub>

                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="text-destructive focus:bg-destructive/10 focus:text-destructive" onClick={() => onDelete && onDelete(pipeline as any)}>
                      <Trash2 className="h-4 w-4 mr-2" /> Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </TableCell>
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  );
};
