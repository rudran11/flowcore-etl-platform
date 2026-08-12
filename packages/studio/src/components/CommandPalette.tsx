import React, { useEffect, useState } from 'react';
import { Command } from 'cmdk';
import { useNavigate } from 'react-router-dom';
import { Search, GitMerge, Activity, Settings, Database, Server, Puzzle, Moon, Sun } from 'lucide-react';
import { useTheme } from 'next-themes';
import { Dialog, DialogContent, DialogTitle } from './ui/dialog';
import { usePipelines } from '../features/pipelines/hooks/usePipelines';

export const CommandPalette: React.FC = () => {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const { setTheme } = useTheme();
  const [search, setSearch] = useState('');
  
  const { data: pipelineData, isLoading } = usePipelines({ 
    search: search.length > 1 ? search : undefined,
    limit: 5
  });

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };

    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  const runCommand = (command: () => void) => {
    setOpen(false);
    command();
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="overflow-hidden p-0 shadow-2xl rounded-xl sm:max-w-[550px] border-border/50 bg-[#111113]/95 dark:bg-[#09090b]/95 backdrop-blur-md">
        <DialogTitle className="sr-only">Command Palette</DialogTitle>
        <Command className="w-full flex flex-col h-full bg-transparent">
          <div className="flex items-center border-b border-border/50 px-3">
            <Search className="mr-2 h-4 w-4 shrink-0 text-muted-foreground" />
            <Command.Input 
              placeholder="Type a command or search pipelines..." 
              className="flex h-12 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50 border-0 focus:ring-0" 
              value={search}
              onValueChange={setSearch}
              autoFocus 
            />
          </div>
          <Command.List className="max-h-[300px] overflow-y-auto overflow-x-hidden p-2 pb-4">
            <Command.Empty className="py-6 text-center text-sm text-muted-foreground">
              No results found.
            </Command.Empty>
            
            <Command.Group heading="Navigation" className="px-2 py-1.5 text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
              <Command.Item onSelect={() => runCommand(() => navigate('/'))} className="flex cursor-default select-none items-center rounded-md px-2 py-2 text-[13px] text-foreground hover:bg-accent/50 aria-selected:bg-accent/50 aria-selected:text-foreground">
                <Activity className="mr-2 h-4 w-4 text-muted-foreground" />
                Dashboard
              </Command.Item>
              <Command.Item onSelect={() => runCommand(() => navigate('/pipelines'))} className="flex cursor-default select-none items-center rounded-md px-2 py-2 text-[13px] text-foreground hover:bg-accent/50 aria-selected:bg-accent/50 aria-selected:text-foreground">
                <GitMerge className="mr-2 h-4 w-4 text-muted-foreground" />
                Pipelines
              </Command.Item>
              <Command.Item onSelect={() => runCommand(() => navigate('/datasets'))} className="flex cursor-default select-none items-center rounded-md px-2 py-2 text-[13px] text-foreground hover:bg-accent/50 aria-selected:bg-accent/50 aria-selected:text-foreground">
                <Database className="mr-2 h-4 w-4 text-muted-foreground" />
                Data Catalog
              </Command.Item>
              <Command.Item onSelect={() => runCommand(() => navigate('/environments'))} className="flex cursor-default select-none items-center rounded-md px-2 py-2 text-[13px] text-foreground hover:bg-accent/50 aria-selected:bg-accent/50 aria-selected:text-foreground">
                <Server className="mr-2 h-4 w-4 text-muted-foreground" />
                Environments
              </Command.Item>
              <Command.Item onSelect={() => runCommand(() => navigate('/plugins'))} className="flex cursor-default select-none items-center rounded-md px-2 py-2 text-[13px] text-foreground hover:bg-accent/50 aria-selected:bg-accent/50 aria-selected:text-foreground">
                <Puzzle className="mr-2 h-4 w-4 text-muted-foreground" />
                Plugins
              </Command.Item>
              <Command.Item onSelect={() => runCommand(() => navigate('/settings'))} className="flex cursor-default select-none items-center rounded-md px-2 py-2 text-[13px] text-foreground hover:bg-accent/50 aria-selected:bg-accent/50 aria-selected:text-foreground">
                <Settings className="mr-2 h-4 w-4 text-muted-foreground" />
                Settings
              </Command.Item>
            </Command.Group>

            {search.length > 1 && (
              <Command.Group heading="Pipelines" className="px-2 py-1.5 text-[11px] font-medium text-muted-foreground uppercase tracking-wider mt-2">
                {isLoading ? (
                  <div className="py-2 px-2 text-sm text-muted-foreground">Searching...</div>
                ) : pipelineData?.items?.length === 0 ? (
                  <div className="py-2 px-2 text-sm text-muted-foreground">No pipelines found matching "{search}"</div>
                ) : (
                  pipelineData?.items?.map(pipeline => (
                    <Command.Item 
                      key={pipeline.id} 
                      onSelect={() => runCommand(() => navigate(`/pipelines/${pipeline.id}/builder`))} 
                      className="flex cursor-default select-none items-center rounded-md px-2 py-2 text-[13px] text-foreground hover:bg-accent/50 aria-selected:bg-accent/50 aria-selected:text-foreground"
                    >
                      <GitMerge className="mr-2 h-4 w-4 text-muted-foreground" />
                      <div className="flex flex-col">
                        <span>{pipeline.name}</span>
                        {pipeline.description && <span className="text-[10px] text-muted-foreground">{pipeline.description}</span>}
                      </div>
                    </Command.Item>
                  ))
                )}
              </Command.Group>
            )}
            
            <Command.Group heading="Theme" className="px-2 py-1.5 text-[11px] font-medium text-muted-foreground uppercase tracking-wider mt-2">
              <Command.Item onSelect={() => runCommand(() => setTheme('light'))} className="flex cursor-default select-none items-center rounded-md px-2 py-2 text-[13px] text-foreground hover:bg-accent/50 aria-selected:bg-accent/50 aria-selected:text-foreground">
                <Sun className="mr-2 h-4 w-4 text-muted-foreground" />
                Light Mode
              </Command.Item>
              <Command.Item onSelect={() => runCommand(() => setTheme('dark'))} className="flex cursor-default select-none items-center rounded-md px-2 py-2 text-[13px] text-foreground hover:bg-accent/50 aria-selected:bg-accent/50 aria-selected:text-foreground">
                <Moon className="mr-2 h-4 w-4 text-muted-foreground" />
                Dark Mode
              </Command.Item>
            </Command.Group>
          </Command.List>
        </Command>
      </DialogContent>
    </Dialog>
  );
};
