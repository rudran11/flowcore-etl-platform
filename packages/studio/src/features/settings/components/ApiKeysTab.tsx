import React, { useState } from 'react';
import { useApiKeys, useCreateApiKey, useRevokeApiKey } from '../hooks/useSettings';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Loader2, Key, Trash2, Copy, CheckCircle2, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';
import { formatDistanceToNow } from 'date-fns';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

export const ApiKeysTab: React.FC = () => {
  const { data: keys, isLoading } = useApiKeys();
  const createMutation = useCreateApiKey();
  const revokeMutation = useRevokeApiKey();

  const [newKeyName, setNewKeyName] = useState('');
  const [createdKey, setCreatedKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleCreate = async () => {
    if (!newKeyName.trim()) return;
    try {
      const result = await createMutation.mutateAsync({ name: newKeyName, scopes: ["dataset:read", "pipeline:read"] });
      setCreatedKey(result.key);
      setNewKeyName('');
      toast.success("Your new API key is ready to use.");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "An error occurred.");
    }
  };

  const handleRevoke = async (keyId: string) => {
    if (!window.confirm("Are you sure you want to revoke this API key? Any applications using it will lose access.")) return;
    try {
      await revokeMutation.mutateAsync(keyId);
      toast.success("The API key can no longer be used.");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "An error occurred.");
    }
  };

  const copyToClipboard = () => {
    if (createdKey) {
      navigator.clipboard.writeText(createdKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const closeDialog = () => {
    setCreatedKey(null);
    setCopied(false);
  };

  if (isLoading) {
    return <div className="flex justify-center p-8"><Loader2 className="h-8 w-8 animate-spin text-white/40" /></div>;
  }

  return (
    <div className="space-y-6">
      <Card className="bg-black/40 border-white/10">
        <CardHeader>
          <CardTitle className="text-xl font-medium text-white">API Keys</CardTitle>
          <CardDescription className="text-white/60">
            Create and manage API keys for programmatic access to this workspace.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-3 mb-8">
            <Input 
              placeholder="Key Name (e.g. CI/CD Pipeline)" 
              value={newKeyName}
              onChange={e => setNewKeyName(e.target.value)}
              className="bg-black/50 border-white/10 text-white max-w-sm"
            />
            <Button 
              onClick={handleCreate} 
              disabled={!newKeyName.trim() || createMutation.isPending}
              className="bg-indigo-600 hover:bg-indigo-700 text-white"
            >
              {createMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Key className="mr-2 h-4 w-4" />}
              Generate New Key
            </Button>
          </div>

          <div className="space-y-4">
            {keys?.map(k => (
              <div key={k.id} className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400">
                    <Key className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white">{k.name}</p>
                    <p className="text-xs text-white/50 font-mono mt-1">{k.prefix}</p>
                    <div className="flex items-center space-x-3 mt-1 text-xs text-white/40">
                      <span>Created {formatDistanceToNow(new Date(k.created_at), { addSuffix: true })}</span>
                      <span>•</span>
                      <span>Last used {k.last_used_at ? formatDistanceToNow(new Date(k.last_used_at), { addSuffix: true }) : 'Never'}</span>
                    </div>
                  </div>
                </div>
                
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => handleRevoke(k.id)}
                  disabled={revokeMutation.isPending}
                  className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Revoke
                </Button>
              </div>
            ))}
            {keys?.length === 0 && (
              <div className="text-center py-8 text-white/50">
                No active API keys found.
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Dialog open={!!createdKey} onOpenChange={(open) => !open && closeDialog()}>
        <DialogContent className="bg-slate-900 border-white/10 text-white sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center text-emerald-400">
              <CheckCircle2 className="h-5 w-5 mr-2" />
              API Key Generated
            </DialogTitle>
            <DialogDescription className="text-white/70 mt-2">
              Please copy your API key now. For security reasons, <strong className="text-white">it will not be shown again.</strong>
            </DialogDescription>
          </DialogHeader>
          
          <div className="bg-black/50 p-4 rounded-md border border-white/10 flex items-center justify-between mt-4">
            <code className="text-emerald-400 font-mono text-sm break-all">{createdKey}</code>
            <Button variant="ghost" size="icon" onClick={copyToClipboard} className="text-white/60 hover:text-white shrink-0 ml-2">
              {copied ? <CheckCircle2 className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
            </Button>
          </div>
          
          <div className="bg-amber-500/10 text-amber-400/90 text-xs p-3 rounded mt-4 flex items-start">
            <AlertTriangle className="h-4 w-4 mr-2 shrink-0 mt-0.5" />
            <p>Keep this key secure. Treat it like a password. Do not commit it to version control.</p>
          </div>

          <DialogFooter className="mt-6">
            <Button onClick={closeDialog} className="bg-white/10 hover:bg-white/20 text-white w-full">
              I have copied my key
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
