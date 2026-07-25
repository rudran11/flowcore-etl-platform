import React, { useRef } from 'react';
import { Button } from '../../../components/ui/button';
import { Save, Play, Download, Upload, Undo, Redo, LayoutTemplate, Copy } from 'lucide-react';
import yaml from 'yaml';
import { usePipelineBuilderStore } from '../../../stores/pipelineBuilderStore';
import { toast } from 'sonner';
import { usePipeline } from '../hooks/usePipeline';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '../../../components/ui/dropdown-menu';
import { useParams } from 'react-router-dom';
import { History } from 'lucide-react';
import { EnvironmentSelector } from '../../environments/components/EnvironmentSelector';
import { apiClient } from '../../../api/client';
import { useQueryClient } from '@tanstack/react-query';

export const BuilderToolbar: React.FC = () => {
  const { 
    undo, redo, isDirty, historyIndex, history, autoLayout, 
    rawYaml, updateFromYaml, isValid 
  } = usePipelineBuilderStore();
  
  const { id } = useParams<{ id: string }>();
  const { data } = usePipeline(id || '');
  const queryClient = useQueryClient();
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSave = async () => {
    if (!isValid) {
      toast.error('Cannot save invalid pipeline');
      return;
    }
    const { nodes, edges, rawYaml: latestYaml, clearDraft } = usePipelineBuilderStore.getState();
    if (!id) return;

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

    const runPromise = apiClient.post(`/pipelines/${id}/versions/${versionToRun}/execute`, {
      parameters: {}
    });

    toast.promise(runPromise, {
      loading: 'Compiling and starting pipeline...',
      success: 'Execution started successfully!',
      error: (err: any) => {
        const detail = err.response?.data?.detail;
        const msg = typeof detail === 'string' ? detail : (detail ? JSON.stringify(detail) : err.message);
        return `Failed to start execution: ${msg}`;
      },
    });
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

  const handleCopyYaml = () => {
    navigator.clipboard.writeText(rawYaml);
    toast.success('YAML copied to clipboard');
  };

  const canUndo = historyIndex > 0;
  const canRedo = historyIndex < history.length - 1;

  return (
    <div className="h-14 bg-zinc-950/80 border-b border-white/5 flex items-center justify-between px-4 backdrop-blur-md">
      <div className="flex items-center gap-1.5">
        <Button variant="ghost" size="sm" onClick={undo} disabled={!canUndo} className="h-8 w-8 p-0 text-zinc-400">
          <Undo className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="sm" onClick={redo} disabled={!canRedo} className="h-8 w-8 p-0 text-zinc-400">
          <Redo className="w-4 h-4" />
        </Button>
        
        <div className="w-px h-4 bg-white/10 mx-2" />
        
        <Button variant="ghost" size="sm" onClick={() => autoLayout('TB')} className="h-8 text-zinc-400 gap-2">
          <LayoutTemplate className="w-4 h-4" />
          Auto Layout
        </Button>
      </div>

      <div className="flex items-center gap-2">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="h-8 text-zinc-400 gap-2">
              <History className="w-4 h-4" /> Versions
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48 bg-zinc-900 border-white/10 text-zinc-300">
            {data?.versions?.length === 0 && (
              <div className="px-2 py-1 text-xs text-zinc-500">No versions saved</div>
            )}
            {data?.versions?.map(v => (
              <DropdownMenuItem 
                key={v.id}
                className="hover:bg-white/5 cursor-pointer flex justify-between"
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
                <span className="text-xs text-zinc-500">{v.created_at ? new Date(v.created_at).toLocaleDateString() : ''}</span>
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>

        <div className="w-px h-4 bg-white/10 mx-2" />

        <input 
          type="file" 
          accept=".yml,.yaml" 
          className="hidden" 
          ref={fileInputRef} 
          onChange={handleImport}
        />
        <Button variant="ghost" size="sm" className="h-8 text-zinc-400 gap-2" onClick={() => fileInputRef.current?.click()}>
          <Upload className="w-4 h-4" /> Import
        </Button>
        <Button variant="ghost" size="sm" className="h-8 text-zinc-400 gap-2" onClick={handleExport}>
          <Download className="w-4 h-4" /> Export
        </Button>
        <Button variant="ghost" size="sm" className="h-8 text-zinc-400 gap-2" onClick={handleCopyYaml}>
          <Copy className="w-4 h-4" /> Copy YAML
        </Button>
        
        <div className="w-px h-4 bg-white/10 mx-2" />
        
        <Button 
          variant={isDirty ? 'default' : 'outline'} 
          size="sm" 
          className={`h-8 gap-2 ${isDirty ? 'bg-primary text-primary-foreground' : 'bg-zinc-900 border-white/10 text-white'}`}
          onClick={handleSave}
        >
          <Save className="w-4 h-4" />
          {isDirty ? 'Save Draft' : 'Saved'}
        </Button>
        <div className="w-px h-4 bg-white/10 mx-2" />
        {id && <EnvironmentSelector pipelineId={id} />}
        <Button 
          variant="default" 
          size="sm" 
          disabled={!isValid}
          className="h-8 gap-2 bg-emerald-600 hover:bg-emerald-700 text-white disabled:opacity-50" 
          onClick={handleRun}
        >
          <Play className="w-4 h-4" />
          Run
        </Button>
      </div>
    </div>
  );
};
