import React, { useRef } from 'react';
import { Button } from '../../../components/ui/button';
import { Save, Play, Download, Upload, Undo, Redo, LayoutTemplate } from 'lucide-react';
import yaml from 'yaml';
import { usePipelineBuilderStore } from '../../../stores/pipelineBuilderStore';
import { toast } from 'sonner';
import { usePipeline } from '../hooks/usePipeline';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '../../../components/ui/dropdown-menu';
import { useParams, useNavigate } from 'react-router-dom';
import { History, Maximize, Check, MoreHorizontal, Edit, Copy as CopyIcon, Trash } from 'lucide-react';
import { EnvironmentSelector } from '../../environments/components/EnvironmentSelector';
import { apiClient } from '../../../api/client';
import { pipelinesApi } from '../../../api/pipelines';
import { useQueryClient } from '@tanstack/react-query';
import { RenamePipelineDialog } from './RenamePipelineDialog';

export const BuilderToolbar: React.FC = () => {
  const { 
    undo, redo, isDirty, historyIndex, history, autoLayout, 
    rawYaml, updateFromYaml, isValid 
  } = usePipelineBuilderStore();
  
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data } = usePipeline(id || '');
  const queryClient = useQueryClient();
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [renameDialogOpen, setRenameDialogOpen] = React.useState(false);

  const handleSave = async () => {
    if (!isValid) {
      toast.error('Cannot save invalid pipeline');
      return;
    }
    const { nodes, edges, rawYaml: latestYaml, clearDraft } = usePipelineBuilderStore.getState();
    if (!id) return;
    
    if (id === 'new') {
      toast.info('This is an unsaved local pipeline. Backend creation is not yet implemented.');
      usePipelineBuilderStore.setState({ isDirty: false });
      return;
    }

    try {
      await apiClient.post(`/pipelines/${id}/versions`, {
        version_tag: `v${Date.now()}`,
        dsl_definition: yaml.parse(latestYaml) || {},
        graph_definition: { nodes, edges }
      });

      await queryClient.invalidateQueries({ queryKey: ['pipeline', id] });
      toast.success('Pipeline saved successfully');
      usePipelineBuilderStore.setState({ isDirty: false });
      clearDraft(id);
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      const msg = typeof detail === 'string' ? detail : (detail ? JSON.stringify(detail) : err.message);
      toast.error('Failed to save: ' + msg);
    }
  };

  const handleRun = async () => {
    if (!isValid) {
      toast.error('Cannot run invalid pipeline');
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
        const detail = err.response?.data?.detail;
        const msg = typeof detail === 'string' ? detail : (detail ? JSON.stringify(detail) : err.message);
        toast.error('Failed to save before running: ' + msg);
        return;
      }
    }

    toast.promise(
      apiClient.post(`/pipelines/${id}/versions/${versionToRun}/execute`, { parameters: {} }),
      {
        loading: 'Compiling and starting pipeline...',
        success: (response: any) => {
          const runId = response.data.run_id;
          setTimeout(() => navigate(`/runs/${runId}`), 500);
          return 'Execution started successfully!';
        },
        error: (err: any) => {
          const detail = err.response?.data?.detail;
          const msg = typeof detail === 'string' ? detail : (detail ? JSON.stringify(detail) : err.message);
          return `Failed to start execution: ${msg}`;
        },
      }
    );
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

  const handleDelete = async () => {
    if (!id || id === 'new') return;
    if (window.confirm('Are you sure you want to delete this pipeline? This cannot be undone.')) {
      try {
        await pipelinesApi.deletePipeline(id);
        toast.success('Pipeline deleted');
        navigate('/pipelines');
      } catch (err: any) {
        toast.error(err.response?.data?.detail || 'Failed to delete pipeline');
      }
    }
  };

  const handleDuplicate = async () => {
    if (!id || id === 'new') return;
    if (!data?.pipeline) return;
    try {
      const newPipeline = await pipelinesApi.createPipeline({
        name: `${data.pipeline.name} (Copy)`,
        description: data.pipeline.description,
        tags: data.pipeline.tags
      });
      const { nodes, edges, rawYaml: latestYaml } = usePipelineBuilderStore.getState();
      await pipelinesApi.savePipelineVersion(newPipeline.id, {
        version_tag: `v${Date.now()}`,
        dsl_definition: yaml.parse(latestYaml) || {},
        graph_definition: { nodes, edges }
      });
      toast.success('Pipeline duplicated');
      navigate(`/pipelines/${newPipeline.id}`);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to duplicate pipeline');
    }
  };

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
        
        <Button variant="ghost" size="sm" onClick={() => autoLayout('TB')} className="h-8 text-muted-foreground hover:text-foreground gap-2">
          <LayoutTemplate className="w-4 h-4" />
          Auto Layout
        </Button>

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
                  if (v.dsl_definition) {
                    updateFromYaml(yaml.stringify(v.dsl_definition));
                    toast.success(`Restored version ${v.version}`);
                  } else {
                    toast.error("Version doesn't contain DSL definitions");
                  }
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
        
        <Button 
          variant={isDirty ? 'default' : 'outline'} 
          size="sm" 
          className={`h-8 gap-2 transition-all ${isDirty ? 'bg-primary text-primary-foreground shadow-sm hover:bg-primary/90' : 'bg-transparent border-transparent hover:bg-accent text-muted-foreground hover:text-foreground'}`}
          onClick={handleSave}
          disabled={!isDirty}
        >
          {isDirty ? (
            <>
              <Save className="w-4 h-4" />
              Save Draft
            </>
          ) : (
            <>
              <Check className="w-4 h-4 text-emerald-500" />
              <span className="text-muted-foreground">Saved just now</span>
            </>
          )}
        </Button>
        <div className="w-px h-4 bg-border/50 mx-2" />
        {id && <EnvironmentSelector pipelineId={id} />}
        <Button 
          variant="default" 
          size="sm" 
          disabled={!isValid}
          className="h-8 gap-2 bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm disabled:opacity-50 transition-colors" 
          onClick={handleRun}
        >
          <Play className="w-4 h-4" />
          Run
        </Button>
        
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
        <RenamePipelineDialog 
          pipelineId={id} 
          initialName={data.pipeline.name} 
          initialDescription={data.pipeline.description || ''} 
          open={renameDialogOpen} 
          onOpenChange={setRenameDialogOpen} 
        />
      )}
    </div>
  );
};
