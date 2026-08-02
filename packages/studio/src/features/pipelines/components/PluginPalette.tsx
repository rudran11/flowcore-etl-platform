import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { usePlugins } from '../../plugins/hooks/usePlugins';
import { Input } from '../../../components/ui/input';
import { Search, Puzzle, Database, Box, Bolt, Cloud, ArrowRightLeft, LayoutTemplate, Trash2 } from 'lucide-react';
import { Skeleton } from '../../../components/ui/skeleton';

interface Template {
  id: string;
  name: string;
  category: string;
  plugin_id: string;
  config: any;
}

export const PluginPalette: React.FC = () => {
  const { data: plugins, isLoading } = usePlugins();
  const [search, setSearch] = useState('');
  const [activeTab, setActiveTab] = useState<'plugins' | 'templates'>('plugins');
  const [templates, setTemplates] = useState<Template[]>([]);

  const loadTemplates = () => {
    const saved = localStorage.getItem('flowcore_templates');
    if (saved) setTemplates(JSON.parse(saved));
  };

  useEffect(() => {
    loadTemplates();
    const handleUpdate = () => loadTemplates();
    window.addEventListener('flowcore_templates_updated', handleUpdate);
    return () => window.removeEventListener('flowcore_templates_updated', handleUpdate);
  }, []);

  const onDragStartPlugin = (event: React.DragEvent, pluginId: string) => {
    event.dataTransfer.setData('application/reactflow', JSON.stringify({ type: 'plugin', plugin_id: pluginId }));
    event.dataTransfer.effectAllowed = 'move';
  };

  const onDragStartTemplate = (event: React.DragEvent, tpl: Template) => {
    event.dataTransfer.setData('application/reactflow', JSON.stringify({ type: 'template', plugin_id: tpl.plugin_id, config: tpl.config }));
    event.dataTransfer.effectAllowed = 'move';
  };

  const deleteTemplate = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const updated = templates.filter(t => t.id !== id);
    localStorage.setItem('flowcore_templates', JSON.stringify(updated));
    setTemplates(updated);
  };

  const filteredPlugins = plugins?.filter(p => 
    p.name.toLowerCase().includes(search.toLowerCase()) || 
    p.category.toLowerCase().includes(search.toLowerCase())
  ) || [];

  const filteredTemplates = templates.filter(t => 
    t.name.toLowerCase().includes(search.toLowerCase()) || 
    t.category.toLowerCase().includes(search.toLowerCase())
  );

  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'database': return <Database className="w-4 h-4" />;
      case 'integration': return <Box className="w-4 h-4" />;
      case 'compute': return <Bolt className="w-4 h-4" />;
      case 'cloud': return <Cloud className="w-4 h-4" />;
      case 'transform': return <ArrowRightLeft className="w-4 h-4" />;
      case 'api': return <Box className="w-4 h-4" />;
      case 'file': return <Puzzle className="w-4 h-4" />;
      case 'messaging': return <Cloud className="w-4 h-4" />;
      case 'ai/ml': return <Bolt className="w-4 h-4" />;
      default: return <LayoutTemplate className="w-4 h-4" />;
    }
  };

  const templateCategories = Array.from(new Set(filteredTemplates.map(t => t.category)));

  return (
    <div className="w-72 bg-card border-r border-border/50 flex flex-col h-full shadow-sm z-10">
      <div className="p-4 border-b border-border/50 bg-background/50 backdrop-blur-sm">
        <div className="flex bg-accent/50 rounded-lg p-1 mb-4 border border-border/50">
          <button 
            className={`flex-1 text-xs font-semibold py-1.5 rounded-md transition-all ${activeTab === 'plugins' ? 'bg-background text-foreground shadow-sm ring-1 ring-border' : 'text-muted-foreground hover:text-foreground hover:bg-background/50'}`}
            onClick={() => setActiveTab('plugins')}
          >
            Connectors
          </button>
          <button 
            className={`flex-1 text-xs font-semibold py-1.5 rounded-md transition-all ${activeTab === 'templates' ? 'bg-background text-foreground shadow-sm ring-1 ring-border' : 'text-muted-foreground hover:text-foreground hover:bg-background/50'}`}
            onClick={() => setActiveTab('templates')}
          >
            Templates
          </button>
        </div>
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={`Search ${activeTab}...`} 
            className="pl-9 bg-background border-border/50 text-sm h-9 shadow-sm focus-visible:ring-primary/20"
          />
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar bg-background/20">
        {activeTab === 'plugins' && (
          isLoading ? (
            <div className="space-y-3">
              <Skeleton className="h-16 w-full rounded-xl bg-accent" />
              <Skeleton className="h-16 w-full rounded-xl bg-accent" />
              <Skeleton className="h-16 w-full rounded-xl bg-accent" />
            </div>
          ) : filteredPlugins.length === 0 ? (
            <div className="text-center text-muted-foreground text-sm mt-8 p-4 bg-accent/30 rounded-xl border border-border/50">No plugins match your search.</div>
          ) : (
            <div className="space-y-2.5">
              {filteredPlugins.map(plugin => (
                <motion.div
                  key={plugin.plugin_id}
                  whileHover={{ scale: 1.01, y: -1 }}
                  whileTap={{ scale: 0.99 }}
                  onDragStart={(e: any) => onDragStartPlugin(e, plugin.plugin_id)}
                  draggable
                  className="group p-3 bg-card border border-border/50 rounded-xl cursor-grab active:cursor-grabbing hover:border-primary/50 hover:shadow-md transition-all"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-accent/50 flex items-center justify-center text-muted-foreground border border-border/50 group-hover:bg-primary/5 group-hover:text-primary transition-colors">
                      {getCategoryIcon(plugin.category)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <div className="text-sm font-semibold text-foreground truncate">{plugin.name}</div>
                        <span className="text-[9px] font-mono bg-accent text-muted-foreground px-1.5 py-0.5 rounded border border-border/50">v1.0</span>
                      </div>
                      <div className="text-[11px] text-muted-foreground truncate mt-0.5">{plugin.category}</div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )
        )}

        {activeTab === 'templates' && (
          filteredTemplates.length === 0 ? (
            <div className="text-center text-muted-foreground text-sm mt-8 p-4 bg-accent/30 rounded-xl border border-border/50">
              No templates saved yet.<br/><br/>Click the Save icon on a node on the canvas to save it as a template.
            </div>
          ) : (
            templateCategories.map(cat => (
              <div key={cat} className="mb-5">
                <div className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mb-2.5 px-1">{cat}</div>
                <div className="space-y-2.5">
                  {filteredTemplates.filter(t => t.category === cat).map(tpl => (
                    <motion.div
                      key={tpl.id}
                      whileHover={{ scale: 1.01, y: -1 }}
                      whileTap={{ scale: 0.99 }}
                      onDragStart={(e: any) => onDragStartTemplate(e, tpl)}
                      draggable
                      className="group p-3 bg-card border border-emerald-500/20 rounded-xl cursor-grab active:cursor-grabbing hover:border-emerald-500/50 hover:shadow-md hover:shadow-emerald-500/5 transition-all relative overflow-hidden"
                    >
                      <div className="absolute left-0 top-0 bottom-0 w-1 bg-emerald-500/20 group-hover:bg-emerald-500 transition-colors" />
                      <div className="flex items-center gap-3 pl-1">
                        <div className="w-9 h-9 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-600 dark:text-emerald-500 border border-emerald-500/20">
                          {getCategoryIcon(tpl.category)}
                        </div>
                        <div className="flex-1 min-w-0 pr-6">
                          <div className="text-sm font-semibold text-foreground truncate">{tpl.name}</div>
                          <div className="text-[10px] text-muted-foreground truncate mt-0.5">Based on: {tpl.plugin_id}</div>
                        </div>
                      </div>
                      <button 
                        onClick={(e) => deleteTemplate(tpl.id, e)}
                        className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive rounded-md opacity-0 group-hover:opacity-100 transition-all"
                        title="Delete Template"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </motion.div>
                  ))}
                </div>
              </div>
            ))
          )
        )}
      </div>
    </div>
  );
};
