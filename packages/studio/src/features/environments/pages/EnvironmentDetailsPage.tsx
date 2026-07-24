import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useEnvironment, useDeleteEnvironment } from '../hooks/useEnvironments';
import { ArrowLeft, Key, Lock, Settings, Code, FileText, Trash2, Plus, Copy, Check } from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { EnvironmentEditor } from '../components/EnvironmentEditor';
import { formatDistanceToNow } from 'date-fns';

export const EnvironmentDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: env, isLoading } = useEnvironment(id!);
  const { mutateAsync: deleteEnv } = useDeleteEnvironment();
  const [activeTab, setActiveTab] = useState<'variables' | 'settings'>('variables');
  
  if (isLoading || !env) {
    return <div className="p-8 text-center animate-pulse">Loading environment details...</div>;
  }

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this environment? This action cannot be undone.')) {
      await deleteEnv(env.id);
      navigate('/environments');
    }
  };

  const getEnvColor = (type: string) => {
    switch (type) {
      case 'PRODUCTION': return 'bg-red-500/10 text-red-500 border-red-500/20';
      case 'STAGING': return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
      case 'QA': return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
      case 'DEVELOPMENT': return 'bg-green-500/10 text-green-500 border-green-500/20';
      default: return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div className="flex items-center gap-4 text-sm text-muted-foreground mb-4">
        <button onClick={() => navigate('/environments')} className="hover:text-primary transition-colors flex items-center gap-1">
          <ArrowLeft className="h-4 w-4" /> Back to Environments
        </button>
      </div>

      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight">{env.name}</h1>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getEnvColor(env.type)}`}>
              {env.type}
            </span>
          </div>
          <p className="text-muted-foreground mt-2 text-lg">
            {env.description || 'No description provided.'}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-6 border-b border-border/50 pb-px">
        <button
          onClick={() => setActiveTab('variables')}
          className={`pb-4 text-sm font-medium transition-colors border-b-2 ${
            activeTab === 'variables' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <div className="flex items-center gap-2">
            <Key className="h-4 w-4" /> Variables & Secrets
          </div>
        </button>
        <button
          onClick={() => setActiveTab('settings')}
          className={`pb-4 text-sm font-medium transition-colors border-b-2 ${
            activeTab === 'settings' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <div className="flex items-center gap-2">
            <Settings className="h-4 w-4" /> Settings
          </div>
        </button>
      </div>

      {activeTab === 'variables' && (
        <EnvironmentEditor environmentId={env.id} variables={env.variables} />
      )}

      {activeTab === 'settings' && (
        <div className="space-y-6 max-w-2xl">
          <div className="p-6 rounded-xl border bg-card/50">
            <h3 className="text-lg font-semibold mb-4 text-red-500 flex items-center gap-2">
              <Trash2 className="h-5 w-5" /> Danger Zone
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              Permanently delete this environment and all of its variables and secrets. This action cannot be undone.
            </p>
            <Button variant="destructive" onClick={handleDelete}>
              Delete Environment
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};
