import React, { useRef } from 'react';
import { Button } from '../../../components/ui/button';
import { Save, Play, Download, Upload, Undo, Redo, LayoutTemplate, ChevronDown } from 'lucide-react';
import yaml from 'yaml';
import { usePipelineBuilderStore } from '../../../stores/pipelineBuilderStore';
import { toast } from 'sonner';
import { usePipeline } from '../hooks/usePipeline';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '../../../components/ui/dropdown-menu';
import { useParams } from 'react-router-dom';
import { History, Maximize, Check, MoreHorizontal, Edit, Copy as CopyIcon, Trash, AlertCircle, AlertTriangle, CheckCircle2, Info } from 'lucide-react';
import { apiClient } from '../../../api/client';
import { useQueryClient } from '@tanstack/react-query';
import { RenamePipelineDialog } from './RenamePipelineDialog';
import { DeletePipelineDialog } from './DeletePipelineDialog';
import { DuplicatePipelineDialog } from './DuplicatePipelineDialog';
import { CompareVersionsDialog } from './CompareVersionsDialog';
import { ExecutionHistoryDrawer } from './ExecutionHistoryDrawer';
import { PipelineVersion } from '../../../types/pipeline';

export const BuilderToolbar: React.FC = () => {
  const { 
    undo, redo, isDirty, historyIndex, history, autoLayout, 
    rawYaml, updateFromYaml, isValid, validationIssues, healthScore,
    isValidationPanelOpen, setValidationPanelOpen,
    isSaving, isExecuting, lastSavedAt, setExecutionMonitorOpen
  } = usePipelineBuilderStore();

  const errorsCount = validationIssues.filter(i => i.severity === 'error').length;
  const warningsCount = validationIssues.filter(i => i.severity === 'warning').length;
  const suggestionsCount = validationIssues.filter(i => i.severity === 'suggestion').length;
  
  const { id } = useParams<{ id: string }>();
  const { data } = usePipeline(id || '');
  const queryClient = useQueryClient();
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [renameDialogOpen, setRenameDialogOpen] = React.useState(false);
  const [duplicateDialogOpen, setDuplicateDialogOpen] = React.useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false);
  const [compareVersion, setCompareVersion] = React.useState<PipelineVersion | null>(null);
  const [compareDialogOpen, setCompareDialogOpen] = React.useState(false);
  const [historyDrawerOpen, setHistoryDrawerOpen] = React.useState(false);

  const handleSave = async () => {
    const criticalErrors = validationIssues.filter(i => ['empty_pipeline', 'missing_trigger', 'multiple_trigger'].some(id => i.id.startsWith(id)));
    if (criticalErrors.length > 0) {
      toast.error('Cannot save: Pipeline has critical structural errors.');
      return;
    }
    const { nodes, edges, rawYaml: latestYaml, clearDraft } = usePipelineBuilderStore.getState();
    if (!id) return;
    
    if (id === 'new') {
      toast.info('This is an unsaved local pipeline. Backend creation is not yet implemented.');
      usePipelineBuilderStore.setState({ isDirty: false });
      return;
    }

    if (isSaving) return;
    usePipelineBuilderStore.setState({ isSaving: true });

    try {
      await apiClient.post(`/pipelines/${id}/versions`, {
        version_tag: `v${Date.now()}`,
        dsl_definition: yaml.parse(latestYaml) || {},
        graph_definition: { nodes, edges }
      });

      await queryClient.invalidateQueries({ queryKey: ['pipeline', id] });
      toast.success('Pipeline Saved');
      usePipelineBuilderStore.setState({ isDirty: false, isSaving: false, lastSavedAt: new Date() });
      clearDraft(id);
    } catch (err: any) {
      usePipelineBuilderStore.setState({ isSaving: false });
      const detail = err.response?.data?.detail;
      const msg = typeof detail === 'string' ? detail : (detail ? JSON.stringify(detail) : err.message);
      toast.error('Failed to save: ' + msg);
    }
  };

  const handleRun = async () => {
    if (!isValid) {
      toast.error('Cannot run pipeline with unresolved errors.');
      return;
    }
    
    if (!id) return;
    
    if (id === 'new') {
      toast.info('Cannot run an unsaved local pipeline. Backend creation is not yet implemented.');
      return;
    }
    
    const { nodes, edges, rawYaml: latestYaml, clearDraft } = usePipelineBuilderStore.getState();
    let versionToRun = data?.versions?.[0]?.version;
    
    if (isDirty || !versionToRun) {
      versionToRun = `v${Date.now()}`;
      try {
        await apiClient.post(`/pipelines/${id}/versions`, {
          version_tag: versionToRun,
          dsl_definition: yaml.parse(latestYaml) || {},
          graph_definition: { nodes, edges }
        });
        await queryClient.invalidateQueries({ queryKey: ['pipeline', id] });
        usePipelineBuilderStore.setState({ isDirty: false });
        clearDraft(id);
        toast.success('Pipeline saved successfully');
      } catch (err: any) {
        usePipelineBuilderStore.setState({ isExecuting: false });
        const detail = err.response?.data?.detail;
        const msg = typeof detail === 'string' ? detail : (detail ? JSON.stringify(detail) : err.message);
        toast.error('Failed to save before execution: ' + msg);
        return;
      }
    }
    
    usePipelineBuilderStore.setState({ isExecuting: true });
    try {
      const resp = await apiClient.post(`/pipelines/${id}/versions/${versionToRun}/execute`, {
        environment_id: 'default'
      });
      
      toast.success('Execution Started');
      setExecutionMonitorOpen(true, resp.data.run_id);
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      const msg = typeof detail === 'string' ? detail : (detail ? JSON.stringify(detail) : err.message);
      toast.error('Failed to trigger execution: ' + msg);
    } finally {
      usePipelineBuilderStore.setState({ isExecuting: false });
    }
  };

  const handleExport = () => {
    const blob = new Blob([rawYaml], { type: 'text/yaml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'pipeline.yml';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('YAML exported');
  };

  const handleImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (evt) => {
      const content = evt.target?.result as string;
      updateFromYaml(content);
      toast.success('YAML imported successfully');
    };
    reader.readAsText(file);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };



  const handleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(err => {
        toast.error(`Error attempting to enable fullscreen mode: ${err.message}`);
      });
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  };

  const handleDelete = () => setDeleteDialogOpen(true);
  const handleDuplicate = () => setDuplicateDialogOpen(true);

  const canUndo = historyIndex > 0;
  const canRedo = historyIndex < history.length - 1;

  return (
    <div className="h-14 bg-card border-b border-border/50 flex items-center justify-between px-4 z-20 relative shadow-sm">
      <div className="flex items-center gap-1.5">
        <Button variant="ghost" size="icon" onClick={undo} disabled={!canUndo} className="h-8 w-8 text-muted-foreground hover:text-foreground">
          <Undo className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon" onClick={redo} disabled={!canRedo} className="h-8 w-8 text-muted-foreground hover:text-foreground">
          <Redo className="w-4 h-4" />
        </Button>
        
        <div className="w-px h-4 bg-border/50 mx-2" />
        
        <Button 
          variant="ghost" 
          size="sm" 
          className="h-8 gap-2 text-muted-foreground hover:text-foreground"
          onClick={() => setHistoryDrawerOpen(true)}
        >
          <History className="w-4 h-4" /> History
        </Button>

        <div className="w-px h-4 bg-border/50 mx-2" />
        
        <Button variant="ghost" size="sm" onClick={() => autoLayout('TB')} className="h-8 text-muted-foreground hover:text-foreground gap-2">
          <LayoutTemplate className="w-4 h-4" />
          Auto Layout
        </Button>

        <div className="w-px h-4 bg-border/50 mx-2" />
        
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={() => setValidationPanelOpen(!isValidationPanelOpen)} 
          className="h-8 gap-3 font-medium text-muted-foreground hover:text-foreground"
        >
          {validationIssues.length === 0 ? (
            <div className="flex items-center gap-1.5 text-emerald-500">
              <CheckCircle2 className="w-4 h-4" />
              <span>Ready</span>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              {errorsCount > 0 && (
                <div className="flex items-center gap-1 text-destructive">
                  <AlertCircle className="w-3.5 h-3.5" />
                  <span>{errorsCount} {errorsCount === 1 ? 'Error' : 'Errors'}</span>
                </div>
              )}
              {warningsCount > 0 && (
                <div className="flex items-center gap-1 text-amber-500">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>{warningsCount} {warningsCount === 1 ? 'Warning' : 'Warnings'}</span>
                </div>
              )}
              {suggestionsCount > 0 && (
                <div className="flex items-center gap-1 text-blue-400">
                  <Info className="w-3.5 h-3.5" />
                  <span>{suggestionsCount} {suggestionsCount === 1 ? 'Suggestion' : 'Suggestions'}</span>
                </div>
              )}
            </div>
          )}
        </Button>
        
        <div 
          className="flex items-center justify-center w-7 h-7 rounded-full border-[2.5px] mx-1 relative cursor-pointer" 
          style={{ borderColor: `hsl(${healthScore * 1.2}, 70%, 45%)` }}
          title={`Health Score: ${healthScore}/100`}
          onClick={() => setValidationPanelOpen(!isValidationPanelOpen)}
        >
          <span className="text-[9px] font-bold" style={{ color: `hsl(${healthScore * 1.2}, 70%, 45%)` }}>{healthScore}</span>
        </div>

        <div className="w-px h-4 bg-border/50 mx-2" />
        
        <Button variant="ghost" size="icon" onClick={handleFullscreen} className="h-8 w-8 text-muted-foreground hover:text-foreground" title="Toggle Fullscreen">
          <Maximize className="w-4 h-4" />
        </Button>
      </div>

      <div className="flex items-center gap-2">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="h-8 text-muted-foreground hover:text-foreground gap-2">
              <History className="w-4 h-4" /> Versions
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48 bg-card border-border/50 text-foreground shadow-lg rounded-xl">
            {data?.versions?.length === 0 && (
              <div className="px-2 py-1 text-xs text-muted-foreground">No versions saved</div>
            )}
            {data?.versions?.map(v => (
              <DropdownMenuItem 
                key={v.id}
                className="hover:bg-accent cursor-pointer flex justify-between rounded-md"
                onClick={() => {
                  setCompareVersion(v as PipelineVersion);
                  setCompareDialogOpen(true);
                }}
              >
                <span>{v.version}</span>
                <span className="text-[10px] text-muted-foreground">{v.created_at ? new Date(v.created_at).toLocaleDateString() : ''}</span>
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>

        <div className="w-px h-4 bg-border/50 mx-2" />

        <input 
          type="file" 
          accept=".yml,.yaml" 
          className="hidden" 
          ref={fileInputRef} 
          onChange={handleImport}
        />
        <Button variant="ghost" size="sm" className="h-8 text-muted-foreground hover:text-foreground gap-2" onClick={() => fileInputRef.current?.click()}>
          <Upload className="w-4 h-4" /> Import
        </Button>
        <Button variant="ghost" size="sm" className="h-8 text-muted-foreground hover:text-foreground gap-2" onClick={handleExport}>
          <Download className="w-4 h-4" /> Export
        </Button>
        
        <div className="w-px h-4 bg-border/50 mx-2" />
        
        <div className="flex flex-col items-end mx-2">
          {isSaving ? (
            <span className="text-[10px] text-muted-foreground animate-pulse flex items-center gap-1">Saving...</span>
          ) : isDirty ? (
            <span className="text-[10px] text-amber-500/80">Unsaved changes</span>
          ) : lastSavedAt ? (
            <span className="text-[10px] text-emerald-500/80">Saved {lastSavedAt.toLocaleTimeString()}</span>
          ) : (
            <span className="text-[10px] text-muted-foreground">Up to date</span>
          )}
        </div>

        <Button 
          variant={isDirty ? 'default' : 'outline'} 
          size="sm" 
          className={`h-8 gap-2 transition-all ${isDirty ? 'bg-primary text-primary-foreground shadow-sm hover:bg-primary/90' : 'bg-transparent border-transparent hover:bg-accent text-muted-foreground hover:text-foreground'}`}
          onClick={handleSave}
          disabled={!isDirty || isSaving}
        >
          {isDirty ? (
            <>
              <Save className="w-4 h-4" /> Save
            </>
          ) : (
            <>
              <Check className="w-4 h-4" /> Saved
            </>
          )}
        </Button>
        
        <div className="flex bg-emerald-600 text-white rounded-md shadow-sm h-8 ml-2 items-center">
          <Button 
            size="sm" 
            className="h-8 rounded-r-none gap-2 bg-emerald-600 hover:bg-emerald-700 px-3 border-r border-emerald-700/50"
            onClick={handleRun}
            disabled={isExecuting || !isValid}
          >
            {isExecuting ? <div className="w-3.5 h-3.5 border-2 border-white/20 border-t-white rounded-full animate-spin" /> : <Play className="w-3.5 h-3.5" />}
            {isExecuting ? 'Starting...' : 'Quick Run'}
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button size="icon" className="h-8 w-6 rounded-l-none bg-emerald-600 hover:bg-emerald-700">
                <ChevronDown className="w-3.5 h-3.5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48 bg-card border-border/50 text-foreground shadow-lg rounded-xl">
              <DropdownMenuItem onClick={handleRun} disabled={!isValid} className="gap-2 cursor-pointer">
                <Play className="w-4 h-4 text-emerald-500" /> Quick Run
              </DropdownMenuItem>
              <DropdownMenuItem disabled className="gap-2 cursor-pointer text-muted-foreground">
                <Maximize className="w-4 h-4" /> Open Full Details
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        {id && id !== 'new' && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground">
                <MoreHorizontal className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48 bg-card border-border/50">
              <DropdownMenuItem onClick={() => setRenameDialogOpen(true)} className="gap-2 cursor-pointer">
                <Edit className="w-4 h-4" /> Rename
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleDuplicate} className="gap-2 cursor-pointer">
                <CopyIcon className="w-4 h-4" /> Duplicate
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-border/50" />
              <DropdownMenuItem onClick={handleDelete} className="gap-2 text-destructive focus:bg-destructive/10 cursor-pointer">
                <Trash className="w-4 h-4" /> Delete Pipeline
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>

      {id && data?.pipeline && (
        <>
          <RenamePipelineDialog 
            pipelineId={id}
            initialName={data.pipeline.name}
            initialDescription={data.pipeline.description || ''}
            open={renameDialogOpen}
            onOpenChange={setRenameDialogOpen}
          />
          <DeletePipelineDialog
            pipelineId={id}
            pipelineName={data.pipeline.name}
            open={deleteDialogOpen}
            onOpenChange={setDeleteDialogOpen}
            onSuccess={() => {}}
          />
          <DuplicatePipelineDialog
            pipelineId={id}
            initialName={data.pipeline.name}
            open={duplicateDialogOpen}
            onOpenChange={setDuplicateDialogOpen}
          />
          <CompareVersionsDialog
            version={compareVersion}
            open={compareDialogOpen}
            onOpenChange={setCompareDialogOpen}
          />
          <ExecutionHistoryDrawer
            pipelineId={id}
            isOpen={historyDrawerOpen}
            onClose={() => setHistoryDrawerOpen(false)}
          />
        </>
      )}
    </div>
  );
};
