import React, { useState } from 'react';
import { useDatasets } from './hooks/useDatasets';
import { useNavigate } from 'react-router-dom';
import { Database, File, Cloud, LayoutGrid, List as ListIcon, Search, AlertCircle, DatabaseBackup } from 'lucide-react';
import { format } from 'date-fns';
import { motion } from 'framer-motion';

export const DatasetsPage: React.FC = () => {
  const { data: datasets, isLoading, error } = useDatasets();
  const navigate = useNavigate();
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-full flex-col items-center justify-center text-red-500">
        <AlertCircle className="h-12 w-12 mb-4" />
        <p>Failed to load datasets</p>
      </div>
    );
  }

  const filteredDatasets = datasets?.filter(d => 
    d.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    (d.description && d.description.toLowerCase().includes(searchQuery.toLowerCase()))
  ) || [];

  const getIconForType = (type: string) => {
    switch (type) {
      case 'DATABASE_TABLE': return <Database className="h-5 w-5 text-blue-500" />;
      case 'FILE': return <File className="h-5 w-5 text-green-500" />;
      case 'API': return <Cloud className="h-5 w-5 text-purple-500" />;
      case 'WAREHOUSE': return <DatabaseBackup className="h-5 w-5 text-indigo-500" />;
      default: return <Database className="h-5 w-5 text-slate-500" />;
    }
  };

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.05 }
    }
  };

  const item = {
    hidden: { opacity: 0, y: 10 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <div className="p-8 h-full overflow-auto space-y-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-2">
          <Database className="h-8 w-8 text-primary" />
          Data Catalog
        </h1>
        <p className="text-slate-400">
          Discover, understand, and manage your organization's data assets.
        </p>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between bg-slate-900/50 p-4 rounded-xl border border-white/5 backdrop-blur-md">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search datasets, tables, files..."
            className="w-full bg-slate-950 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
        </div>
        
        <div className="flex items-center gap-2 bg-slate-950 p-1 rounded-lg border border-white/10">
          <button 
            className={`p-1.5 rounded-md transition-all ${viewMode === 'grid' ? 'bg-primary text-white shadow-md' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}
            onClick={() => setViewMode('grid')}
          >
            <LayoutGrid className="h-4 w-4" />
          </button>
          <button 
            className={`p-1.5 rounded-md transition-all ${viewMode === 'list' ? 'bg-primary text-white shadow-md' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}
            onClick={() => setViewMode('list')}
          >
            <ListIcon className="h-4 w-4" />
          </button>
        </div>
      </div>

      {filteredDatasets.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 text-slate-500 border border-dashed border-white/10 rounded-xl">
          <Database className="h-16 w-16 mb-4 opacity-50" />
          <p className="text-lg font-medium">No datasets found</p>
          <p className="text-sm">Try adjusting your search criteria</p>
        </div>
      ) : (
        <motion.div 
          className={viewMode === 'grid' ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6" : "flex flex-col gap-4"}
          variants={container}
          initial="hidden"
          animate="show"
        >
          {filteredDatasets.map(dataset => (
            <motion.div 
              key={dataset.id}
              variants={item}
              onClick={() => navigate(`/datasets/${dataset.id}`)}
              className={`group bg-slate-900 border border-white/10 rounded-xl overflow-hidden hover:border-primary/50 hover:shadow-[0_0_15px_rgba(59,130,246,0.15)] transition-all cursor-pointer ${
                viewMode === 'list' ? 'flex items-center p-4' : 'flex flex-col'
              }`}
            >
              <div className={`${viewMode === 'grid' ? 'p-5 border-b border-white/5' : 'mr-4 bg-slate-800/50 p-3 rounded-lg'}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-slate-950 rounded-lg shadow-inner">
                      {getIconForType(dataset.type)}
                    </div>
                    {viewMode === 'grid' && (
                      <span className="text-xs font-semibold text-primary bg-primary/10 px-2 py-1 rounded-full uppercase tracking-wider">
                        {dataset.type.replace('_', ' ')}
                      </span>
                    )}
                  </div>
                </div>
                {viewMode === 'grid' && (
                  <h3 className="text-lg font-medium text-white mt-4 mb-1 truncate group-hover:text-primary transition-colors">
                    {dataset.name}
                  </h3>
                )}
              </div>
              
              <div className={`${viewMode === 'list' ? 'flex-1 flex items-center justify-between' : 'p-5 flex-1 flex flex-col'}`}>
                {viewMode === 'list' ? (
                  <>
                    <div>
                      <h3 className="text-lg font-medium text-white group-hover:text-primary transition-colors truncate">
                        {dataset.name}
                      </h3>
                      <p className="text-sm text-slate-400 mt-1">
                        {dataset.description || 'No description available'}
                      </p>
                    </div>
                    <div className="flex items-center gap-8">
                      <span className="text-xs font-semibold text-primary bg-primary/10 px-2 py-1 rounded-full uppercase tracking-wider">
                        {dataset.type.replace('_', ' ')}
                      </span>
                      <div className="text-right text-sm">
                        <p className="text-slate-300">v{dataset.version}</p>
                        <p className="text-slate-500 text-xs">{format(new Date(dataset.updated_at), 'MMM d, yyyy')}</p>
                      </div>
                    </div>
                  </>
                ) : (
                  <>
                    <p className="text-sm text-slate-400 line-clamp-2 mb-4 flex-1">
                      {dataset.description || 'No description available for this dataset.'}
                    </p>
                    <div className="flex items-center justify-between text-xs text-slate-500 mt-auto pt-4 border-t border-white/5">
                      <span>Version {dataset.version}</span>
                      <span>Updated {format(new Date(dataset.updated_at), 'MMM d, yyyy')}</span>
                    </div>
                  </>
                )}
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
};
