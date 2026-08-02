import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '../../../components/ui/dialog';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { toast } from 'sonner';
import { pipelinesApi } from '../../../api/pipelines';
import { useQueryClient } from '@tanstack/react-query';

interface RenamePipelineDialogProps {
  pipelineId: string;
  initialName: string;
  initialDescription: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const RenamePipelineDialog: React.FC<RenamePipelineDialogProps> = ({ 
  pipelineId, initialName, initialDescription, open, onOpenChange 
}) => {
  const [name, setName] = useState(initialName);
  const [description, setDescription] = useState(initialDescription);
  const [loading, setLoading] = useState(false);
  const queryClient = useQueryClient();

  useEffect(() => {
    if (open) {
      setName(initialName);
      setDescription(initialDescription);
    }
  }, [open, initialName, initialDescription]);

  const handleRename = async () => {
    if (!name.trim()) return;
    setLoading(true);
    try {
      await pipelinesApi.updatePipeline(pipelineId, {
        name,
        description
      });
      await queryClient.invalidateQueries({ queryKey: ['pipeline', pipelineId] });
      await queryClient.invalidateQueries({ queryKey: ['pipelines'] });
      toast.success('Pipeline updated successfully');
      onOpenChange(false);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to update pipeline');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Edit Pipeline</DialogTitle>
          <DialogDescription>
            Update the name and description of this pipeline.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="space-y-2">
            <label className="text-sm font-medium leading-none">Name</label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium leading-none">Description</label>
            <Input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleRename} disabled={!name.trim() || loading || (name === initialName && description === initialDescription)}>
            Save Changes
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
