import React, { useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { usePipeline } from '../hooks/usePipeline';
import { PipelineCanvas } from '../components/PipelineCanvas';
import { usePipelineBuilderStore } from '../../../stores/pipelineBuilderStore';
import yaml from 'yaml';
import { Skeleton } from '../../../components/ui/skeleton';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../../../components/ui/dialog';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { useState } from 'react';
import { useBlocker } from 'react-router-dom';

const TemplateDialog = () => {
  const { isTemplateDialogOpen, templateNodeToSave, closeTemplateDialog } = usePipelineBuilderStore();
  const [name, setName] = useState('');
  const [category, setCategory] = useState('Custom');
  
  const handleSave = () => {
    if (!name.trim() || !templateNodeToSave) return;
    
    const templates = JSON.parse(localStorage.getItem('flowcore_templates') || '[]');
    templates.push({
      id: `template_${Date.now()}`,
      name,
      category,
      plugin_id: templateNodeToSave.data.plugin_id,
      config: templateNodeToSave.data.config
    });
    localStorage.setItem('flowcore_templates', JSON.stringify(templates));
    toast.success(`Template ${name} saved successfully!`);
    
    // Dispatch a custom event to notify PluginPalette to refresh templates
    window.dispatchEvent(new Event('flowcore_templates_updated'));
    
    closeTemplateDialog();
    setName('');
  };
  
  return (
    <Dialog open={isTemplateDialogOpen} onOpenChange={(open) => !open && closeTemplateDialog()}>
      <DialogContent className="bg-zinc-950 border-white/10 text-white">
        <DialogHeader>
          <DialogTitle>Save Node as Template</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div>
            <label className="block text-sm text-zinc-400 mb-1">Template Name</label>
            <Input 
              value={name} 
              onChange={e => setName(e.target.value)} 
              placeholder="e.g. Postgres Staging Connection" 
              className="bg-zinc-900 border-white/10"
            />
          </div>
          <div>
            <label className="block text-sm text-zinc-400 mb-1">Category</label>
            <select 
              value={category}
              onChange={e => setCategory(e.target.value)}
              className="w-full h-10 px-3 rounded-md bg-zinc-900 border border-white/10 text-sm text-white focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="Database">Database</option>
              <option value="File">File</option>
              <option value="API">API</option>
              <option value="Messaging">Messaging</option>
              <option value="AI/ML">AI/ML</option>
              <option value="Custom">Custom</option>
            </select>
          </div>
        </div>
        <DialogFooter>
          <Button variant="ghost" onClick={closeTemplateDialog}>Cancel</Button>
          <Button className="bg-emerald-600 hover:bg-emerald-700 text-white" onClick={handleSave} disabled={!name.trim()}>Save Template</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export const PipelineDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const isNew = id === 'new';
  const { data, isLoading } = usePipeline(isNew ? '' : id!);
  
  const { 
    setPipeline, 
    undo, redo, 
    copySelected, pasteClipboard, duplicateSelected, deleteSelected,
    saveDraftToStorage, loadDraftFromStorage, clearDraft, isDirty
  } = usePipelineBuilderStore();

  const [draftPromptOpen, setDraftPromptOpen] = useState(false);

  // Unsaved changes blocker
  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) =>
      isDirty && currentLocation.pathname !== nextLocation.pathname
  );

  // Initialize Pipeline
  useEffect(() => {
    if (isNew) {
      setPipeline({ id: 'new', name: 'Untitled Pipeline', description: 'Unsaved Pipeline' } as any, yaml.stringify({ trigger: { type: 'manual' }, steps: {} }));
    } else if (data && data.pipeline && id) {
      const draft = localStorage.getItem(`flowcore_pipeline_draft_${id}`);
      if (draft) {
        setDraftPromptOpen(true);
      }

      const latestVersion = data.versions && data.versions.length > 0 ? data.versions[0] : null;
      if (latestVersion && latestVersion.dsl_definition) {
         setPipeline(data.pipeline, yaml.stringify(latestVersion.dsl_definition));
         
         if (latestVersion.graph_definition && latestVersion.graph_definition.nodes) {
           usePipelineBuilderStore.setState({
             nodes: latestVersion.graph_definition.nodes,
             edges: latestVersion.graph_definition.edges
           });
           usePipelineBuilderStore.getState().validatePipeline();
         }
      } else {
         setPipeline(data.pipeline, yaml.stringify({ trigger: { type: 'manual' }, steps: {} }));
      }
    }
  }, [data, id, isNew, setPipeline]);

  // Unsaved changes warning for tab close
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (usePipelineBuilderStore.getState().isDirty) {
        e.preventDefault();
        e.returnValue = '';
      }
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, []);

  // Autosave Draft every 30s
  useEffect(() => {
    const timer = setInterval(() => {
      if (id && usePipelineBuilderStore.getState().isDirty) {
        saveDraftToStorage(id);
      }
    }, 30000);
    return () => clearInterval(timer);
  }, [id, saveDraftToStorage]);

  // Global Keyboard Shortcuts
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    // Avoid triggering shortcuts when typing in an input/textarea
    if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
      return;
    }

    if (e.ctrlKey || e.metaKey) {
      switch (e.key.toLowerCase()) {
        case 's':
          e.preventDefault();
          toast.success('Pipeline saved (Shortcut)');
          usePipelineBuilderStore.setState({ isDirty: false });
          break;
        case 'z':
          e.preventDefault();
          if (e.shiftKey) redo();
          else undo();
          break;
        case 'y':
          e.preventDefault();
          redo();
          break;
        case 'c':
          copySelected();
          break;
        case 'v':
          pasteClipboard();
          break;
        case 'd':
          e.preventDefault();
          duplicateSelected();
          break;
      }
    } else if (e.key === 'Delete' || e.key === 'Backspace') {
      deleteSelected();
    }
  }, [undo, redo, copySelected, pasteClipboard, duplicateSelected, deleteSelected]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  if (isLoading) {
    return (
      <div className="flex-1 flex flex-col p-6 bg-zinc-950">
        <Skeleton className="h-10 w-64 mb-4 bg-white/5" />
        <Skeleton className="flex-1 bg-white/5" />
      </div>
    );
  }

  if (!isNew && (!data || !data.pipeline)) {
    return (
      <div className="flex-1 flex items-center justify-center bg-zinc-950">
        <div className="text-zinc-500">Pipeline not found.</div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden">
      <PipelineCanvas />
      <TemplateDialog />
      <Dialog open={draftPromptOpen} onOpenChange={setDraftPromptOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Unsaved Draft Found</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <p className="text-sm text-muted-foreground">
              We found an unsaved draft of this pipeline. Would you like to restore it or discard it?
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              if (id) clearDraft(id);
              setDraftPromptOpen(false);
            }}>
              Discard
            </Button>
            <Button onClick={() => {
              if (id && data?.pipeline) {
                loadDraftFromStorage(id, data.pipeline);
                toast.success('Draft restored');
              }
              setDraftPromptOpen(false);
            }}>
              Restore Draft
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={blocker.state === "blocked"} onOpenChange={(open) => !open && blocker.state === "blocked" && blocker.reset?.()}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Unsaved Changes</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <p className="text-sm text-muted-foreground">
              You have unsaved changes. Are you sure you want to leave this page? Your changes will be saved as a draft.
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => blocker.reset?.()}>
              Stay
            </Button>
            <Button variant="destructive" onClick={() => blocker.proceed?.()}>
              Leave
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
