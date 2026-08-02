import React, { useState } from 'react';
import { Plus, Search, Server, Activity, Shield, MoreVertical } from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { useEnvironments } from '../hooks/useEnvironments';
import { useNavigate } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '../../../components/ui/dialog';
import { useCreateEnvironment } from '../hooks/useEnvironments';
import { PageHeader } from '../../../components/ui/page-header';
import { StatCard } from '../../../components/ui/stat-card';
import { EmptyState } from '../../../components/ui/empty-state';

export const EnvironmentsPage: React.FC = () => {
  const { data: environments, isLoading } = useEnvironments();
  const { mutateAsync: createEnv, isPending: isCreating } = useCreateEnvironment();
  const [searchTerm, setSearchTerm] = useState('');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newEnvName, setNewEnvName] = useState('');
  const [newEnvDesc, setNewEnvDesc] = useState('');
  const [newEnvType, setNewEnvType] = useState('DEVELOPMENT');
  const navigate = useNavigate();

  const handleCreate = async () => {
    if (!newEnvName.trim()) return;
    try {
      const env = await createEnv({
        name: newEnvName.trim(),
        description: newEnvDesc.trim(),
        type: newEnvType as any
      });
      setIsDialogOpen(false);
      setNewEnvName('');
      setNewEnvDesc('');
      navigate(`/environments/${env.id}`);
    } catch (e) {
      // Error handled by mutation
    }
  };

  const filteredEnvs = environments?.filter(env => 
    env.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    env.type.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
    <div className="p-6 md:p-8 max-w-[1400px] mx-auto space-y-8 animate-in fade-in duration-500 w-full">
      <div className="flex items-center justify-between">
        <PageHeader
          title="Environments"
          subtitle="Manage configuration profiles and secure secrets for your deployments."
          icon={Server}
        />
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button size="lg" className="shadow-lg shadow-primary/20">
              <Plus className="mr-2 h-5 w-5" />
              Create Environment
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Create Environment</DialogTitle>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <label className="text-sm font-medium">Name</label>
                <Input 
                  value={newEnvName} 
                  onChange={e => setNewEnvName(e.target.value)}
                  placeholder="e.g. Production Data Warehouse"
                />
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium">Description</label>
                <Input 
                  value={newEnvDesc} 
                  onChange={e => setNewEnvDesc(e.target.value)}
                  placeholder="Optional description"
                />
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium">Type</label>
                <select 
                  className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  value={newEnvType}
                  onChange={e => setNewEnvType(e.target.value)}
                >
                  <option value="DEVELOPMENT">Development</option>
                  <option value="QA">QA</option>
                  <option value="STAGING">Staging</option>
                  <option value="PRODUCTION">Production</option>
                </select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
              <Button onClick={handleCreate} disabled={!newEnvName.trim() || isCreating}>
                {isCreating ? 'Creating...' : 'Create'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard 
          title="Active Environments" 
          value={environments?.length || 0} 
          icon={<Server className="h-4 w-4" />}
          description="Total configured profiles"
        />
        <StatCard 
          title="Production Profiles" 
          value={environments?.filter(e => e.type === 'PRODUCTION').length || 0} 
          icon={<Activity className="h-4 w-4" />}
          description="High-security targets"
          trend="up"
          trendValue="Secured"
        />
        <StatCard 
          title="Total Secrets Managed" 
          value={environments?.reduce((acc, env) => acc + env.variables.filter(v => v.is_secret).length, 0) || 0} 
          icon={<Shield className="h-4 w-4" />}
          description="Encrypted variables"
        />
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Search environments..." 
            className="pl-10 bg-background/50 backdrop-blur border-muted/50 focus:border-primary/50 transition-colors"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1,2,3].map(i => (
            <div key={i} className="h-48 rounded-xl border bg-card/50 animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredEnvs?.map(env => (
            <div 
              key={env.id} 
              className="group relative p-6 rounded-xl border bg-card/50 hover:bg-card/80 transition-all cursor-pointer shadow-sm hover:shadow-xl hover:shadow-primary/5 hover:-translate-y-1 overflow-hidden"
              onClick={() => navigate(`/environments/${env.id}`)}
            >
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="font-semibold text-lg">{env.name}</h3>
                  <div className={`mt-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getEnvColor(env.type)}`}>
                    {env.type}
                  </div>
                </div>
                <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity" onClick={(e) => { e.stopPropagation(); }}>
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </div>
              
              <p className="text-sm text-muted-foreground mb-6 line-clamp-2 min-h-[40px]">
                {env.description || 'No description provided.'}
              </p>
              
              <div className="flex items-center justify-between text-xs text-muted-foreground pt-4 border-t border-border/50">
                <div className="flex items-center gap-2">
                  <span className="flex h-2 w-2 rounded-full bg-primary/50" />
                  {env.variables.length} Variables
                </div>
                <div>
                  Updated {formatDistanceToNow(new Date(env.updated_at))} ago
                </div>
              </div>
            </div>
          ))}
          {filteredEnvs?.length === 0 && (
            <div className="col-span-full">
              <EmptyState 
                icon={Server}
                title="No environments found"
                description="We couldn't find any environments matching your search query."
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};
