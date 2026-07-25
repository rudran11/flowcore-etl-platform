import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDataset, useDatasetImpact } from './hooks/useDatasets';
import { LineageExplorer } from './LineageExplorer';
import { Database, File, Cloud, ArrowLeft, Tag, ShieldAlert, GitCommit, GitBranch } from 'lucide-react';
import { format } from 'date-fns';

export const DatasetDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: dataset, isLoading } = useDataset(id || '');
  const { data: impactData } = useDatasetImpact(id || '');
  const [activeTab, setActiveTab] = useState<'overview' | 'schema' | 'lineage' | 'history'>('overview');

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!dataset) {
    return (
      <div className="p-8">
        <button onClick={() => navigate('/datasets')} className="flex items-center text-slate-400 hover:text-white mb-6 transition-colors">
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Catalog
        </button>
        <div className="text-center py-20 text-slate-500">Dataset not found</div>
      </div>
    );
  }

  const getIconForType = (type: string) => {
    switch (type) {
      case 'DATABASE_TABLE': return <Database className="h-8 w-8 text-blue-500" />;
      case 'FILE': return <File className="h-8 w-8 text-green-500" />;
      case 'API': return <Cloud className="h-8 w-8 text-purple-500" />;
      default: return <Database className="h-8 w-8 text-slate-500" />;
    }
  };

  return (
    <div className="p-8 h-full overflow-auto space-y-6">
      <button 
        onClick={() => navigate('/datasets')} 
        className="flex items-center text-slate-400 hover:text-white transition-colors text-sm font-medium"
      >
        <ArrowLeft className="w-4 h-4 mr-1" /> Back to Catalog
      </button>

      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 bg-slate-900/50 p-6 rounded-2xl border border-white/5 backdrop-blur-sm">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-slate-950 rounded-xl shadow-inner border border-white/5">
            {getIconForType(dataset.type)}
          </div>
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-bold text-white">{dataset.name}</h1>
              <span className="text-xs font-semibold text-primary bg-primary/10 px-2 py-1 rounded-full uppercase tracking-wider">
                {dataset.type.replace('_', ' ')}
              </span>
            </div>
            <p className="text-slate-400 max-w-2xl">{dataset.description || 'No description provided for this dataset.'}</p>
          </div>
        </div>

        <div className="flex gap-4 items-center bg-slate-950/50 px-4 py-3 rounded-xl border border-white/5">
          <div className="flex flex-col">
            <span className="text-xs text-slate-500 uppercase font-semibold">Owner</span>
            <span className="text-sm text-slate-200">{dataset.owner || 'Unassigned'}</span>
          </div>
          <div className="w-px h-8 bg-white/10 mx-2"></div>
          <div className="flex flex-col">
            <span className="text-xs text-slate-500 uppercase font-semibold">Version</span>
            <span className="text-sm text-slate-200 flex items-center gap-1">
              <GitCommit className="w-3 h-3 text-primary" /> v{dataset.version}
            </span>
          </div>
          <div className="w-px h-8 bg-white/10 mx-2"></div>
          <div className="flex flex-col">
            <span className="text-xs text-slate-500 uppercase font-semibold">Updated</span>
            <span className="text-sm text-slate-200">{format(new Date(dataset.updated_at), 'MMM d, yyyy')}</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-6 border-b border-white/10 px-2">
        <button 
          className={`pb-3 text-sm font-medium transition-colors relative ${activeTab === 'overview' ? 'text-primary' : 'text-slate-400 hover:text-white'}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
          {activeTab === 'overview' && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary rounded-t-full"></div>}
        </button>
        <button 
          className={`pb-3 text-sm font-medium transition-colors relative ${activeTab === 'schema' ? 'text-primary' : 'text-slate-400 hover:text-white'}`}
          onClick={() => setActiveTab('schema')}
        >
          Schema & Columns
          {activeTab === 'schema' && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary rounded-t-full"></div>}
        </button>
        <button 
          className={`pb-3 text-sm font-medium transition-colors relative flex items-center gap-2 ${activeTab === 'lineage' ? 'text-primary' : 'text-slate-400 hover:text-white'}`}
          onClick={() => setActiveTab('lineage')}
        >
          <GitBranch className="w-4 h-4" /> Lineage Graph
          {activeTab === 'lineage' && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary rounded-t-full"></div>}
        </button>
      </div>

      {/* Content */}
      <div className="mt-6">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-slate-900 rounded-xl p-6 border border-white/10">
                <h3 className="text-lg font-medium text-white mb-4">Business Context</h3>
                <div className="prose prose-invert max-w-none text-slate-300">
                  <p>This dataset represents a core entity in the data platform.</p>
                  <p>Data quality checks are actively running and lineage is tracked automatically through FlowCore's Execution Engine.</p>
                </div>
              </div>
              
              <div className="bg-slate-900 rounded-xl p-6 border border-white/10">
                <h3 className="text-lg font-medium text-white mb-4">Impact Analysis</h3>
                <div className={`flex items-center gap-4 p-4 rounded-lg border ${
                  impactData?.risk_score === 'HIGH' ? 'bg-red-500/10 text-red-500 border-red-500/20' : 
                  impactData?.risk_score === 'MEDIUM' ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20' : 
                  'bg-green-500/10 text-green-500 border-green-500/20'
                }`}>
                  <ShieldAlert className="w-8 h-8" />
                  <div>
                    <h4 className="font-medium">{impactData?.risk_score || 'UNKNOWN'} Impact Risk</h4>
                    <p className="text-sm opacity-80">This dataset affects {impactData?.criticality || 0} downstream datasets.</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="space-y-6">
              <div className="bg-slate-900 rounded-xl p-6 border border-white/10">
                <h3 className="text-sm font-medium text-slate-300 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <Tag className="w-4 h-4" /> Classifications
                </h3>
                <div className="flex flex-wrap gap-2">
                  <span className="px-3 py-1 bg-slate-800 text-slate-300 text-xs rounded-full border border-white/10">PII</span>
                  <span className="px-3 py-1 bg-slate-800 text-slate-300 text-xs rounded-full border border-white/10">Tier 1</span>
                  <span className="px-3 py-1 bg-slate-800 text-slate-300 text-xs rounded-full border border-white/10">Production</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'lineage' && (
          <div className="w-full">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-medium text-white">End-to-End Lineage</h3>
              <div className="text-sm text-slate-400 bg-slate-900 px-3 py-1 rounded-full border border-white/5">
                Automatically detected via Engine Tracking
              </div>
            </div>
            <LineageExplorer datasetId={id || ''} />
          </div>
        )}
        
        {activeTab === 'schema' && (
          <div className="bg-slate-900 rounded-xl border border-white/10 overflow-hidden">
            <table className="w-full text-left">
              <thead className="bg-slate-950 border-b border-white/10 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-6 py-4 font-semibold">Column Name</th>
                  <th className="px-6 py-4 font-semibold">Data Type</th>
                  <th className="px-6 py-4 font-semibold">Description</th>
                  <th className="px-6 py-4 font-semibold">Attributes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                <tr className="hover:bg-slate-800/50 transition-colors">
                  <td className="px-6 py-4 font-medium text-white">id</td>
                  <td className="px-6 py-4 text-blue-400 font-mono text-sm">UUID</td>
                  <td className="px-6 py-4 text-slate-400 text-sm">Primary identifier</td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary/20 text-primary">PK</span>
                  </td>
                </tr>
                <tr className="hover:bg-slate-800/50 transition-colors">
                  <td className="px-6 py-4 font-medium text-white">created_at</td>
                  <td className="px-6 py-4 text-blue-400 font-mono text-sm">TIMESTAMP</td>
                  <td className="px-6 py-4 text-slate-400 text-sm">Record creation time</td>
                  <td className="px-6 py-4"></td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
