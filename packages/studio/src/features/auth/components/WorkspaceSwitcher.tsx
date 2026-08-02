import React, { useEffect } from 'react';
import { ChevronsUpDown, Check, Building } from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from '../../../components/ui/dropdown-menu';
import { useAuthStore } from '../../../stores/authStore';
import { useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

export const WorkspaceSwitcher: React.FC = () => {
  const { workspaces, activeWorkspaceId, setActiveWorkspace, setWorkspaces } = useAuthStore();
  const queryClient = useQueryClient();
  
  useEffect(() => {
    // Fetch user's workspaces
    const fetchWorkspaces = async () => {
      try {
        const { data } = await axios.get('http://localhost:8000/api/v1/workspaces/', {
          withCredentials: true,
          headers: {
            Authorization: `Bearer ${useAuthStore.getState().accessToken}`
          }
        });
        setWorkspaces(data);
      } catch (e) {
        console.error("Failed to fetch workspaces", e);
      }
    };
    if (useAuthStore.getState().accessToken) {
      fetchWorkspaces();
    }
  }, [setWorkspaces]);

  const activeWorkspace = workspaces.find(w => w.id === activeWorkspaceId) || workspaces[0];

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="w-full justify-between px-2 text-sm font-medium hover:bg-accent/50">
          <div className="flex items-center gap-2 truncate">
            <div className="flex h-5 w-5 items-center justify-center rounded-sm bg-primary/10 text-primary">
              <Building className="h-3 w-3" />
            </div>
            <span className="truncate">{activeWorkspace?.name || "Select Workspace"}</span>
          </div>
          <ChevronsUpDown className="h-3 w-3 shrink-0 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-[220px]" align="start">
        <DropdownMenuLabel>Workspaces</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {workspaces.map((workspace) => (
          <DropdownMenuItem
            key={workspace.id}
            onSelect={() => {
              setActiveWorkspace(workspace.id);
              queryClient.clear();
              // queryClient.invalidateQueries() or resetQueries() could also work, but clear completely purges the cache so old workspace data doesn't leak
            }}
            className="flex items-center justify-between"
          >
            {workspace.name}
            {activeWorkspaceId === workspace.id && (
              <Check className="h-4 w-4 ml-auto" />
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
