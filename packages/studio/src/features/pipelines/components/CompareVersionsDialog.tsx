import React from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '../../../components/ui/dialog';
import { Button } from '../../../components/ui/button';
import { PipelineVersion } from '../../../types/pipeline';
import yaml from 'yaml';
import { usePipelineBuilderStore } from '../../../stores/pipelineBuilderStore';
import { toast } from 'sonner';

interface CompareVersionsDialogProps {
  version: PipelineVersion | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const CompareVersionsDialog: React.FC<CompareVersionsDialogProps> = ({ 
  version, open, onOpenChange 
}) => {
  const { updateFromYaml } = usePipelineBuilderStore();

  const handleRestore = () => {
    if (version?.dsl_definition) {
      updateFromYaml(yaml.stringify(version.dsl_definition));
      toast.success(`Restored version ${version.version}`);
      onOpenChange(false);
    } else {
      toast.error("Version doesn't contain DSL definitions");
    }
  };

  if (!version) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Compare Version: {version.version}</DialogTitle>
          <DialogDescription>
            Review the details of this version before restoring it to your canvas.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4 text-sm">
          <div className="grid grid-cols-3 gap-4">
            <span className="font-semibold text-muted-foreground">Version</span>
            <span className="col-span-2 font-mono">{version.version}</span>
            
            <span className="font-semibold text-muted-foreground">Created</span>
            <span className="col-span-2">{version.created_at ? new Date(version.created_at).toLocaleString() : 'Unknown'}</span>
            
            <span className="font-semibold text-muted-foreground">Nodes</span>
            <span className="col-span-2">{version.steps?.length || 0} nodes</span>
            
            <span className="font-semibold text-muted-foreground">Summary</span>
            <span className="col-span-2 text-muted-foreground">
              {/* If we had a summary field, it would go here */}
              Automated version snapshot.
            </span>
          </div>
        </div>
        <DialogFooter className="mt-4">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleRestore}>
            Restore this version
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
