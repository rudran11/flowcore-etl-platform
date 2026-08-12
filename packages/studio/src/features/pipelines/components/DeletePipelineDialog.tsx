import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '../../../components/ui/dialog';
import { Button } from '../../../components/ui/button';
import { toast } from 'sonner';
import { pipelinesApi } from '../../../api/pipelines';
import { useQueryClient } from '@tanstack/react-query';

interface DeletePipelineDialogProps {
  pipelineId: string;
  pipelineName: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export const DeletePipelineDialog: React.FC<DeletePipelineDialogProps> = ({ 
  pipelineId, pipelineName, open, onOpenChange, onSuccess 
}) => {
  const [loading, setLoading] = useState(false);
  const queryClient = useQueryClient();

  const handleDelete = async () => {
    setLoading(true);
    try {
      await pipelinesApi.deletePipeline(pipelineId);
      await queryClient.invalidateQueries({ queryKey: ['pipelines'] });
      toast.success('Pipeline deleted successfully');
      onOpenChange(false);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to delete pipeline');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="text-destructive">Delete Pipeline</DialogTitle>
          <DialogDescription>
            Are you sure you want to delete <span className="font-semibold text-foreground">{pipelineName}</span>? 
            This action cannot be undone and will permanently remove all versions and execution history.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="mt-4">
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={loading}>
            Cancel
          </Button>
          <Button variant="destructive" onClick={handleDelete} disabled={loading}>
            {loading ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
