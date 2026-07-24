import React, { useState } from 'react';
import { usePlugins, usePluginCategories, usePluginStats } from '../hooks/usePlugins';
import { PluginCard } from '../components/PluginCard';
import { Input } from '../../../components/ui/input';
import { Button } from '../../../components/ui/button';
import { Search, LayoutGrid, List as ListIcon, Loader2, ArrowUpDown, Filter } from 'lucide-react';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuLabel, 
  DropdownMenuRadioGroup, 
  DropdownMenuRadioItem, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from '../../../components/ui/dropdown-menu';

export const PluginsPage: React.FC = () => {
  const { data: plugins, isLoading } = usePlugins();
  const { data: categories } = usePluginCategories();
  const { data: stats } = usePluginStats();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState<'name' | 'version'>('name');

  const filteredPlugins = React.useMemo(() => {
    if (!plugins) return [];
    let filtered = plugins;

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter(p => 
        p.name.toLowerCase().includes(q) || 
        p.description?.toLowerCase().includes(q)
      );
    }

    if (selectedCategory !== 'All') {
      filtered = filtered.filter(p => p.category === selectedCategory);
    }

    return filtered.sort((a, b) => {
      if (sortBy === 'name') return a.name.localeCompare(b.name);
      if (sortBy === 'version') return a.version.localeCompare(b.version);
      return 0;
    });
  }, [plugins, searchQuery, selectedCategory, sortBy]);

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header & Stats */}
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Plugin Hub</h1>
          <p className="text-zinc-400">Discover, manage, and configure enterprise connectors and plugins.</p>
        </div>
        
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-zinc-950/50 border border-white/5 p-4 rounded-xl">
              <div className="text-sm font-medium text-zinc-400 mb-1">Total Plugins</div>
              <div className="text-2xl font-bold text-white">{stats.total}</div>
            </div>
            <div className="bg-zinc-950/50 border border-emerald-500/10 p-4 rounded-xl">
              <div className="text-sm font-medium text-emerald-500/80 mb-1">Healthy</div>
              <div className="text-2xl font-bold text-emerald-500">{stats.healthy}</div>
            </div>
            <div className="bg-zinc-950/50 border border-rose-500/10 p-4 rounded-xl">
              <div className="text-sm font-medium text-rose-500/80 mb-1">Unhealthy</div>
              <div className="text-2xl font-bold text-rose-500">{stats.unhealthy}</div>
            </div>
            <div className="bg-zinc-950/50 border border-white/5 p-4 rounded-xl">
              <div className="text-sm font-medium text-zinc-400 mb-1">Disabled</div>
              <div className="text-2xl font-bold text-white">{stats.disabled}</div>
            </div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between bg-zinc-950/30 p-2 rounded-lg border border-white/5">
        <div className="relative w-full sm:w-96">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
          <Input 
            placeholder="Search plugins..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 bg-zinc-900/50 border-white/5 focus-visible:ring-1 focus-visible:ring-zinc-700" 
          />
        </div>
        
        <div className="flex items-center gap-2 w-full sm:w-auto">
          {/* Categories Dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="bg-zinc-900/50 border-white/5 gap-2">
                <Filter className="h-4 w-4 text-zinc-400" />
                {selectedCategory}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48 bg-zinc-950 border-white/10">
              <DropdownMenuLabel>Categories</DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-white/5" />
              <DropdownMenuRadioGroup value={selectedCategory} onValueChange={setSelectedCategory}>
                <DropdownMenuRadioItem value="All">All Categories</DropdownMenuRadioItem>
                {categories?.map(c => (
                  <DropdownMenuRadioItem key={c} value={c}>{c}</DropdownMenuRadioItem>
                ))}
              </DropdownMenuRadioGroup>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Sort Dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="bg-zinc-900/50 border-white/5 gap-2">
                <ArrowUpDown className="h-4 w-4 text-zinc-400" />
                Sort
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-40 bg-zinc-950 border-white/10">
              <DropdownMenuLabel>Sort By</DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-white/5" />
              <DropdownMenuRadioGroup value={sortBy} onValueChange={(v) => setSortBy(v as any)}>
                <DropdownMenuRadioItem value="name">Name</DropdownMenuRadioItem>
                <DropdownMenuRadioItem value="version">Version</DropdownMenuRadioItem>
              </DropdownMenuRadioGroup>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* View Mode Toggle */}
          <div className="flex items-center bg-zinc-900/50 rounded-md border border-white/5 p-0.5">
            <Button 
              variant="ghost" 
              size="icon" 
              className={`h-8 w-8 rounded-sm ${viewMode === 'grid' ? 'bg-white/10 text-white' : 'text-zinc-500 hover:text-zinc-300'}`}
              onClick={() => setViewMode('grid')}
            >
              <LayoutGrid className="h-4 w-4" />
            </Button>
            <Button 
              variant="ghost" 
              size="icon" 
              className={`h-8 w-8 rounded-sm ${viewMode === 'list' ? 'bg-white/10 text-white' : 'text-zinc-500 hover:text-zinc-300'}`}
              onClick={() => setViewMode('list')}
            >
              <ListIcon className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Grid / List */}
      {filteredPlugins.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="w-16 h-16 bg-zinc-900/50 rounded-full flex items-center justify-center mb-4">
            <Search className="w-8 h-8 text-zinc-500" />
          </div>
          <h3 className="text-lg font-medium text-white mb-1">No plugins found</h3>
          <p className="text-zinc-500">Try adjusting your search or filters.</p>
        </div>
      ) : (
        <div className={viewMode === 'grid' ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6" : "flex flex-col gap-3"}>
          {filteredPlugins.map(plugin => (
            <PluginCard 
              key={plugin.plugin_id} 
              plugin={plugin} 
              viewMode={viewMode}
              // healthStatus="READY" // In a real app, you'd fetch health per plugin or in the list endpoint. Mocking for now.
              healthStatus="READY"
            />
          ))}
        </div>
      )}
    </div>
  );
};
