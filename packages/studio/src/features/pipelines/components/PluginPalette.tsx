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
    <div className="w-72 bg-zinc-950/80 border-r border-white/5 flex flex-col h-full backdrop-blur-md">
      <div className="p-4 border-b border-white/5">
        <div className="flex bg-zinc-900 rounded-lg p-1 mb-4 border border-white/5">
          <button 
            className={`flex-1 text-xs font-medium py-1.5 rounded-md transition-colors ${activeTab === 'plugins' ? 'bg-zinc-800 text-white shadow-sm' : 'text-zinc-500 hover:text-zinc-300'}`}
            onClick={() => setActiveTab('plugins')}
          >
            Plugins
          </button>
          <button 
            className={`flex-1 text-xs font-medium py-1.5 rounded-md transition-colors ${activeTab === 'templates' ? 'bg-zinc-800 text-white shadow-sm' : 'text-zinc-500 hover:text-zinc-300'}`}
            onClick={() => setActiveTab('templates')}
          >
            Templates
          </button>
        </div>
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <Input 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={`Search ${activeTab}...`} 
            className="pl-9 bg-zinc-900/50 border-white/5 text-sm h-9"
          />
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
        {activeTab === 'plugins' && (
          isLoading ? (
            <>
              <Skeleton className="h-16 w-full rounded-lg bg-white/5" />
              <Skeleton className="h-16 w-full rounded-lg bg-white/5" />
            </>
          ) : filteredPlugins.length === 0 ? (
            <div className="text-center text-zinc-500 text-sm mt-8">No plugins match.</div>
          ) : (
            filteredPlugins.map(plugin => (
              <motion.div
                key={plugin.plugin_id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onDragStart={(e: any) => onDragStartPlugin(e, plugin.plugin_id)}
                draggable
                className="p-3 bg-zinc-900/50 border border-white/5 rounded-lg cursor-grab active:cursor-grabbing hover:border-white/10 hover:bg-zinc-800/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded bg-zinc-800 flex items-center justify-center text-zinc-400">
                    {getCategoryIcon(plugin.category)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-zinc-200 truncate">{plugin.name}</div>
                    <div className="text-xs text-zinc-500 truncate">{plugin.category}</div>
                  </div>
                </div>
              </motion.div>
            ))
          )
        )}

        {activeTab === 'templates' && (
          filteredTemplates.length === 0 ? (
            <div className="text-center text-zinc-500 text-sm mt-8">No templates saved yet.<br/><br/>Click the Save icon on a node on the canvas to save it as a template.</div>
          ) : (
            templateCategories.map(cat => (
              <div key={cat} className="mb-4">
                <div className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider mb-2">{cat}</div>
                <div className="space-y-2">
                  {filteredTemplates.filter(t => t.category === cat).map(tpl => (
                    <motion.div
                      key={tpl.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onDragStart={(e: any) => onDragStartTemplate(e, tpl)}
                      draggable
                      className="group p-3 bg-zinc-900/80 border border-emerald-500/20 rounded-lg cursor-grab active:cursor-grabbing hover:border-emerald-500/40 transition-colors relative"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded bg-emerald-500/10 flex items-center justify-center text-emerald-500">
                          {getCategoryIcon(tpl.category)}
                        </div>
                        <div className="flex-1 min-w-0 pr-6">
                          <div className="text-sm font-medium text-emerald-100 truncate">{tpl.name}</div>
                          <div className="text-[10px] text-zinc-500 truncate">Based on: {tpl.plugin_id}</div>
                        </div>
                      </div>
                      <button 
                        onClick={(e) => deleteTemplate(tpl.id, e)}
                        className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-zinc-500 hover:text-rose-500 opacity-0 group-hover:opacity-100 transition-opacity"
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
