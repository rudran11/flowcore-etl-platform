import React, { useState } from 'react';
import { useEnvironments } from '../hooks/useEnvironments';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '../../../components/ui/dropdown-menu';
import { Button } from '../../../components/ui/button';
import { Server, Check } from 'lucide-react';
import { apiClient } from '../../../api/client';
import { toast } from 'sonner';

interface Props {
  pipelineId: string;
}

export const EnvironmentSelector: React.FC<Props> = ({ pipelineId }) => {
  const { data: environments } = useEnvironments();
  const [selectedEnvId, setSelectedEnvId] = useState<string | null>(null);

  // In a full implementation, we'd fetch bound environments for this pipeline to initialize `selectedEnvId`.
  // For MVP, we'll just let the user pick one and execute binding.

  const handleSelect = async (envId: string) => {
    try {
      await apiClient.post('/environments/bind', {
        pipeline_id: pipelineId,
        environment_id: envId
      });
      setSelectedEnvId(envId);
      toast.success('Environment bound successfully');
    } catch (err) {
      toast.error('Failed to bind environment');
    }
  };

  const selectedEnv = environments?.find(e => e.id === selectedEnvId);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" className="h-8 text-zinc-400 gap-2">
          <Server className="w-4 h-4" />
          {selectedEnv ? selectedEnv.name : 'Select Environment'}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48 bg-zinc-900 border-white/10 text-zinc-300">
        {environments?.map(env => (
          <DropdownMenuItem 
            key={env.id}
            className="hover:bg-white/5 cursor-pointer flex justify-between"
            onClick={() => handleSelect(env.id)}
          >
            <span>{env.name}</span>
            {selectedEnvId === env.id && <Check className="w-4 h-4 text-primary" />}
          </DropdownMenuItem>
        ))}
        {environments?.length === 0 && (
          <div className="px-2 py-1 text-xs text-zinc-500">No environments found</div>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
