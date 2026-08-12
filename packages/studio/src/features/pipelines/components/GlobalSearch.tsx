import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent } from '../../../components/ui/dialog';
import { Input } from '../../../components/ui/input';
import { Search, GitMerge } from 'lucide-react';
import { usePipelines } from '../hooks/usePipelines';
import { useNavigate } from 'react-router-dom';
import { Skeleton } from '../../../components/ui/skeleton';

export const GlobalSearch: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const navigate = useNavigate();
  
  const { data, isLoading } = usePipelines({ 
    search: query.length > 1 ? query : undefined,
    limit: 10
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

  const handleSelect = (id: string) => {
    setOpen(false);
    navigate(`/pipelines/${id}/builder`);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="sm:max-w-[600px] p-0 overflow-hidden gap-0 bg-background/95 backdrop-blur-md">
        <div className="flex items-center border-b px-3">
          <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
          <Input 
            className="flex h-12 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50 border-0 focus-visible:ring-0 shadow-none"
            placeholder="Type a command or search pipelines..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
          />
        </div>
        
        <div className="max-h-[300px] overflow-y-auto p-2">
          {query.length > 1 ? (
            isLoading ? (
              <div className="p-2 space-y-2">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            ) : data?.items?.length === 0 ? (
              <p className="p-4 text-center text-sm text-muted-foreground">
                No results found.
              </p>
            ) : (
              <div className="space-y-1">
                {data?.items?.map((item) => (
                  <button
                    key={item.id}
                    className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-left hover:bg-accent hover:text-accent-foreground"
                    onClick={() => handleSelect(item.id)}
                  >
                    <GitMerge className="h-4 w-4 text-muted-foreground" />
                    <div className="flex flex-col">
                      <span className="font-medium">{item.name}</span>
                      {item.description && (
                        <span className="text-xs text-muted-foreground truncate">{item.description}</span>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )
          ) : (
            <p className="p-4 text-center text-sm text-muted-foreground">
              Start typing to search across your workspace...
            </p>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};
