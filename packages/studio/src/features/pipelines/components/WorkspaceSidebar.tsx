import React, { useState } from 'react';
import { Folder, Star, Clock, Archive, Plus } from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { useFolders, useCreateFolder } from '../hooks/useFolders';
import { cn } from '../../../lib/utils';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../../../components/ui/dialog';
import { Input } from '../../../components/ui/input';

interface SidebarItemProps {
  icon: React.ElementType;
  label: string;
  count?: number;
  isActive?: boolean;
  onClick?: () => void;
  className?: string;
  actionIcon?: React.ElementType;
  onAction?: () => void;
}

const SidebarItem = ({ icon: Icon, label, count, isActive, onClick, className, actionIcon: ActionIcon, onAction }: SidebarItemProps) => (
  <div className="group flex items-center relative">
    <button 
      onClick={onClick}
      className={cn(
        "w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
        isActive ? "bg-accent text-accent-foreground font-medium" : "text-muted-foreground hover:bg-accent/50 hover:text-foreground",
        className
      )}
    >
      <Icon className="w-4 h-4 shrink-0" />
      <span className="flex-1 text-left truncate">{label}</span>
      {count !== undefined && (
        <span className={cn("text-xs bg-muted px-1.5 py-0.5 rounded-full transition-opacity", ActionIcon && "group-hover:opacity-0 mr-4")}>
          {count}
        </span>
      )}
    </button>
    {ActionIcon && (
      <button 
        className="absolute right-2 opacity-0 group-hover:opacity-100 p-1 hover:bg-background rounded-md transition-opacity"
        onClick={(e) => { e.stopPropagation(); onAction?.(); }}
      >
        <ActionIcon className="h-3.5 w-3.5 text-muted-foreground hover:text-foreground" />
      </button>
    )}
  </div>
);

interface WorkspaceSidebarProps {
  selectedFolderId?: string;
  onSelectFolder: (id?: string) => void;
  currentView: 'all' | 'favorites' | 'recent' | 'archived';
  onViewChange: (view: 'all' | 'favorites' | 'recent' | 'archived') => void;
  onCreatePipelineInFolder?: (folderId: string) => void;
}

export const WorkspaceSidebar: React.FC<WorkspaceSidebarProps> = ({ 
  selectedFolderId, 
  onSelectFolder,
  currentView,
  onViewChange,
  onCreatePipelineInFolder
}) => {
  const { data: folders } = useFolders();
  const [isFolderDialogOpen, setFolderDialogOpen] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const createFolder = useCreateFolder();

  const handleCreateFolder = async () => {
    if (newFolderName.trim()) {
      await createFolder.mutateAsync({ name: newFolderName });
      setNewFolderName('');
      setFolderDialogOpen(false);
    }
  };

  return (
    <div className="w-64 border-r bg-card/30 flex flex-col h-[calc(100vh-4rem)]">
      <div className="p-4 space-y-1">
        <SidebarItem 
          icon={Folder} 
          label="All Pipelines" 
          isActive={currentView === 'all' && !selectedFolderId}
          onClick={() => { onViewChange('all'); onSelectFolder(undefined); }}
        />
        <SidebarItem 
          icon={Star} 
          label="Favorites" 
          isActive={currentView === 'favorites'}
          onClick={() => { onViewChange('favorites'); onSelectFolder(undefined); }}
        />
        <SidebarItem 
          icon={Clock} 
          label="Recent" 
          isActive={currentView === 'recent'}
          onClick={() => { onViewChange('recent'); onSelectFolder(undefined); }}
        />
      </div>

      <div className="px-4 py-2 border-t">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Folders</span>
          <Button variant="ghost" size="icon" className="h-5 w-5" onClick={() => setFolderDialogOpen(true)}>
            <Plus className="h-3 w-3" />
          </Button>
        </div>
        
        <div className="space-y-1">
          {folders?.map(f => (
            <SidebarItem 
              key={f.folder.id}
              icon={Folder}
              label={f.folder.name}
              count={f.pipeline_count}
              isActive={selectedFolderId === f.folder.id && currentView === 'all'}
              onClick={() => { onViewChange('all'); onSelectFolder(f.folder.id); }}
              actionIcon={Plus}
              onAction={() => onCreatePipelineInFolder?.(f.folder.id)}
            />
          ))}
        </div>
      </div>

      <div className="mt-auto p-4 border-t space-y-1">
        <SidebarItem 
          icon={Archive} 
          label="Archived" 
          isActive={currentView === 'archived'}
          onClick={() => { onViewChange('archived'); onSelectFolder(undefined); }}
        />
      </div>

      <Dialog open={isFolderDialogOpen} onOpenChange={setFolderDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>New Folder</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <Input 
              placeholder="Folder name" 
              value={newFolderName}
              onChange={e => setNewFolderName(e.target.value)}
              autoFocus
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setFolderDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleCreateFolder} disabled={!newFolderName.trim() || createFolder.isPending}>
              {createFolder.isPending ? "Creating..." : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
