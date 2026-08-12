import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { usePipelines, useBulkAction, useToggleFavorite } from '../hooks/usePipelines';
import { PipelineTable } from '../components/PipelineTable';
import { PipelineSearch } from '../components/PipelineSearch';
import { WorkspaceSidebar } from '../components/WorkspaceSidebar';
import { PageTransition } from '../../../components/ui/PageTransition';
import { Button } from '../../../components/ui/button';
import { ChevronLeft, ChevronRight, Filter, GitMerge, Plus, LayoutGrid, List } from 'lucide-react';
import { PageHeader } from '../../../components/ui/page-header';
import { EmptyState } from '../../../components/ui/empty-state';
import { toast } from 'sonner';
import { Skeleton } from '../../../components/ui/skeleton';
import { CreatePipelineDialog } from '../components/CreatePipelineDialog';
import { RenamePipelineDialog } from '../components/RenamePipelineDialog';
import { DuplicatePipelineDialog } from '../components/DuplicatePipelineDialog';
import { DeletePipelineDialog } from '../components/DeletePipelineDialog';
import { Pipeline } from '../../../types/pipeline';
import { Card, CardContent } from '../../../components/ui/card';

export const PipelinesPage: React.FC = () => {
  const [search, setSearch] = useState('');
  const [skip, setSkip] = useState(0);
  const [limit] = useState(25);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [selectedPipeline, setSelectedPipeline] = useState<Pipeline | null>(null);
  const [renameDialogOpen, setRenameDialogOpen] = useState(false);
  const [duplicateDialogOpen, setDuplicateDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  const [currentView, setCurrentView] = useState<'all' | 'favorites' | 'recent' | 'archived'>('all');
  const [selectedFolderId, setSelectedFolderId] = useState<string | undefined>();
  const [createFolderId, setCreateFolderId] = useState<string | undefined>();
  const [displayMode, setDisplayMode] = useState<'list' | 'grid'>('list');

  const toggleFavorite = useToggleFavorite();
  const bulkAction = useBulkAction();

  const { data, isLoading, error } = usePipelines({ 
    skip, 
    limit, 
    search: search ? search : undefined,
    folder_id: currentView === 'all' ? selectedFolderId : undefined,
    is_favorite: currentView === 'favorites' ? true : undefined,
    is_archived: currentView === 'archived' ? true : false,
    sort_by: currentView === 'recent' ? 'updated_at' : 'created_at'
  });

  useEffect(() => {
    if (error) {
      toast.error('Failed to load pipelines data');
    }
  }, [error]);

  const handleNext = () => setSkip(prev => prev + limit);
  const handlePrev = () => setSkip(prev => Math.max(0, prev - limit));

  const getBreadcrumbTitle = () => {
    if (currentView === 'favorites') return 'Favorites';
    if (currentView === 'recent') return 'Recent';
    if (currentView === 'archived') return 'Archived';
    if (selectedFolderId) return 'Folder';
    return 'All Pipelines';
  };

  return (
    <PageTransition className="flex w-full h-[calc(100vh-4rem)] overflow-hidden">
      <WorkspaceSidebar 
        currentView={currentView}
        onViewChange={(v) => { setCurrentView(v); setSkip(0); }}
        selectedFolderId={selectedFolderId}
        onSelectFolder={(id) => { setSelectedFolderId(id); setSkip(0); }}
        onCreatePipelineInFolder={(folderId) => {
          setCreateFolderId(folderId);
          setCreateDialogOpen(true);
        }}
      />
      
      <div className="flex-1 flex flex-col overflow-y-auto bg-background p-6 md:p-8 space-y-6">
        <PageHeader
          title={getBreadcrumbTitle()}
          subtitle="Manage and monitor all your data pipelines in one place."
          icon={GitMerge}
          actions={
            <div className="flex items-center gap-2">
              <div className="flex items-center bg-muted/50 rounded-md p-1 mr-2 border">
                <Button 
                  variant={displayMode === 'list' ? 'secondary' : 'ghost'} 
                  size="icon" 
                  className="h-8 w-8"
                  onClick={() => setDisplayMode('list')}
                >
                  <List className="h-4 w-4" />
                </Button>
                <Button 
                  variant={displayMode === 'grid' ? 'secondary' : 'ghost'} 
                  size="icon" 
                  className="h-8 w-8"
                  onClick={() => setDisplayMode('grid')}
                >
                  <LayoutGrid className="h-4 w-4" />
                </Button>
              </div>
              <Button className="shadow-md" onClick={() => setCreateDialogOpen(true)}>
                <Plus className="mr-2 h-4 w-4" /> New Pipeline
              </Button>
            </div>
          }
        />

        {currentView === 'all' && !selectedFolderId && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardContent className="p-4 flex flex-col">
                <span className="text-sm font-medium text-muted-foreground">Total Pipelines</span>
                <span className="text-2xl font-bold mt-1">{data?.total || 0}</span>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex flex-col">
                <span className="text-sm font-medium text-muted-foreground">Active Schedules</span>
                <span className="text-2xl font-bold mt-1">--</span>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex flex-col">
                <span className="text-sm font-medium text-muted-foreground">Executions Today</span>
                <span className="text-2xl font-bold mt-1">--</span>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex flex-col">
                <span className="text-sm font-medium text-muted-foreground">Success Rate</span>
                <span className="text-2xl font-bold mt-1">--%</span>
              </CardContent>
            </Card>
          </div>
        )}

        <div className="flex items-center gap-4">
          <div className="flex-1 max-w-md">
            <PipelineSearch value={search} onChange={(val) => { setSearch(val); setSkip(0); }} placeholder="Search pipelines by name or description..." />
          </div>
          <Button variant="outline" className="flex items-center gap-2">
            <Filter className="h-4 w-4" />
            Filter
          </Button>
        </div>

        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full flex-1"
        >
          {isLoading ? (
            <div className="p-6 space-y-4 border rounded-md shadow-sm bg-card/50">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="flex gap-4">
                  <Skeleton className="h-6 w-1/4" />
                  <Skeleton className="h-6 w-1/4" />
                  <Skeleton className="h-6 w-1/2" />
                </div>
              ))}
            </div>
          ) : data?.items?.length === 0 ? (
            <EmptyState
              icon={GitMerge}
              title="No pipelines found"
              description="You don't have any data pipelines matching your query in this view."
              action={
                <Button variant="outline" onClick={() => { setSearch(''); setSkip(0); }}>Clear filters</Button>
              }
            />
          ) : displayMode === 'list' ? (
            <PipelineTable 
              pipelines={data?.items || []} 
              loading={isLoading} 
              onRename={(p) => { setSelectedPipeline(p); setRenameDialogOpen(true); }}
              onDuplicate={(p) => { setSelectedPipeline(p); setDuplicateDialogOpen(true); }}
              onDelete={(p) => { setSelectedPipeline(p); setDeleteDialogOpen(true); }}
              onFavorite={(p, fav) => {
                toggleFavorite.mutateAsync({ id: p.id, is_favorite: fav });
              }}
              onArchive={(p, arch) => {
                bulkAction.mutateAsync({ action: 'archive', pipeline_ids: [p.id], archive: arch });
              }}
              onMove={(p, folder_id) => {
                bulkAction.mutateAsync({ action: 'move', pipeline_ids: [p.id], folder_id: folder_id || undefined });
              }}
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {/* Basic grid view placeholder to fulfill requirements */}
              {data?.items?.map(pipeline => (
                <Card key={pipeline.id} className="cursor-pointer hover:shadow-md transition-shadow group">
                  <CardContent className="p-5">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 bg-primary/10 rounded-md flex items-center justify-center text-primary">
                          <GitMerge className="h-5 w-5" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-base leading-none tracking-tight">{pipeline.name}</h3>
                          <p className="text-sm text-muted-foreground mt-1 line-clamp-1">{pipeline.description || 'No description'}</p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </motion.div>
        
        {data && data.total > 0 && (
          <div className="flex items-center justify-between px-2 pt-2 pb-6">
            <div className="text-sm text-muted-foreground font-medium">
              Showing {data.skip + 1} to {Math.min(data.skip + data.limit, data.total)} of {data.total} pipelines
            </div>
            <div className="flex space-x-2">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handlePrev} 
                disabled={skip === 0}
                className="w-24"
              >
                <ChevronLeft className="mr-2 h-4 w-4" />
                Previous
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleNext} 
                disabled={skip + limit >= data.total}
                className="w-24"
              >
                Next
                <ChevronRight className="ml-2 h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </div>

      <CreatePipelineDialog 
        open={createDialogOpen} 
        onOpenChange={(open) => {
          setCreateDialogOpen(open);
          if (!open) setCreateFolderId(undefined);
        }}
        folderId={createFolderId || selectedFolderId}
      />
      
      {selectedPipeline && (
        <>
          <RenamePipelineDialog
            pipelineId={selectedPipeline.id}
            initialName={selectedPipeline.name}
            initialDescription={selectedPipeline.description || ''}
            open={renameDialogOpen}
            onOpenChange={setRenameDialogOpen}
          />
          <DuplicatePipelineDialog
            pipelineId={selectedPipeline.id}
            initialName={selectedPipeline.name}
            open={duplicateDialogOpen}
            onOpenChange={setDuplicateDialogOpen}
          />
          <DeletePipelineDialog
            pipelineId={selectedPipeline.id}
            pipelineName={selectedPipeline.name}
            open={deleteDialogOpen}
            onOpenChange={setDeleteDialogOpen}
          />
        </>
      )}
    </PageTransition>
  );
};
