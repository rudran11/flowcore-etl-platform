import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '../../../components/ui/dialog';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { toast } from 'sonner';
import { pipelinesApi } from '../../../api/pipelines';
import { useQueryClient } from '@tanstack/react-query';

interface DuplicatePipelineDialogProps {
  pipelineId: string;
  initialName: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const DuplicatePipelineDialog: React.FC<DuplicatePipelineDialogProps> = ({ 
  pipelineId, initialName, open, onOpenChange 
}) => {
  const [name, setName] = useState(`${initialName} Copy`);
  const [loading, setLoading] = useState(false);
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  useEffect(() => {
    if (open) {
      setName(`${initialName} Copy`);
    }
  }, [open, initialName]);

  const handleDuplicate = async (andOpen: boolean) => {
    if (!name.trim()) return;
    setLoading(true);
    try {
      // 1. Fetch original pipeline details to get the latest version
      const original = await pipelinesApi.getPipelineDetails(pipelineId);
      const latestVersion = original.versions?.[0];
      
      // 2. Create the new pipeline
      const newPipeline = await pipelinesApi.createPipeline({
        name,
        description: original.pipeline.description,
        tags: original.pipeline.tags
      });

      // 3. Save the version data into the new pipeline
      if (latestVersion) {
        await pipelinesApi.savePipelineVersion(newPipeline.id, {
          version_tag: `v${Date.now()}`,
          dsl_definition: latestVersion.dsl_definition || {},
          graph_definition: latestVersion.graph_definition || { nodes: [], edges: [] }
        });
      }

      await queryClient.invalidateQueries({ queryKey: ['pipelines'] });
      toast.success('Pipeline duplicated successfully');
      onOpenChange(false);
      
      if (andOpen) {
        navigate(`/pipelines/${newPipeline.id}`);
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to duplicate pipeline');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Duplicate Pipeline</DialogTitle>
          <DialogDescription>
            Create a copy of this pipeline. You can provide a custom name.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="space-y-2">
            <label className="text-sm font-medium leading-none">New Name</label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
            />
          </div>
        </div>
        <DialogFooter className="flex-col sm:flex-row gap-2">
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={loading}>
            Cancel
          </Button>
          <Button variant="secondary" onClick={() => handleDuplicate(false)} disabled={!name.trim() || loading}>
            Duplicate as Draft
          </Button>
          <Button onClick={() => handleDuplicate(true)} disabled={!name.trim() || loading}>
            Duplicate & Open
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
