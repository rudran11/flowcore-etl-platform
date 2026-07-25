import React, { useState } from 'react';
import { EnvironmentVariable } from '../types';
import { useAddVariable, useDeleteVariable, useImportEnv } from '../hooks/useEnvironments';
import { Key, Lock, Trash2, Plus, Upload, Eye, EyeOff } from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Switch } from '../../../components/ui/switch';

interface Props {
  environmentId: string;
  variables: EnvironmentVariable[];
}

export const EnvironmentEditor: React.FC<Props> = ({ environmentId, variables }) => {
  const [newKey, setNewKey] = useState('');
  const [newValue, setNewValue] = useState('');
  const [newIsSecret, setNewIsSecret] = useState(false);
  const [showValues, setShowValues] = useState<Record<string, boolean>>({});
  
  const { mutateAsync: addVar } = useAddVariable(environmentId);
  const { mutateAsync: deleteVar } = useDeleteVariable(environmentId);
  const { mutateAsync: importEnv } = useImportEnv(environmentId);
  
  const handleAdd = async () => {
    if (!newKey.trim()) return;
    await addVar({ key: newKey.trim(), value: newValue, is_secret: newIsSecret });
    setNewKey('');
    setNewValue('');
    setNewIsSecret(false);
  };
  
  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const text = await file.text();
      await importEnv(text);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          Configuration <span className="text-sm font-normal text-muted-foreground">({variables.length})</span>
        </h3>
        <div className="flex gap-2">
          <label className="cursor-pointer">
            <Input type="file" className="hidden" accept=".env" onChange={handleImport} />
            <Button variant="outline" asChild>
              <span><Upload className="mr-2 h-4 w-4" /> Import .env</span>
            </Button>
          </label>
        </div>
      </div>
      
      <div className="space-y-4">
        {variables.map(v => (
          <div key={v.id} className="flex items-center gap-4 p-4 rounded-xl border bg-card/50">
            <div className="flex-1">
              <Input 
                value={v.key} 
                disabled 
                className="bg-transparent border-0 font-mono text-sm" 
              />
            </div>
            <div className="flex-1 relative">
              <Input 
                value={v.value === '********' && !showValues[v.id] ? '••••••••••••••••' : v.value} 
                disabled 
                className="bg-transparent border-0 font-mono text-sm pr-10" 
              />
              {v.is_secret && (
                <button 
                  onClick={() => setShowValues(prev => ({...prev, [v.id]: !prev[v.id]}))}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showValues[v.id] ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              )}
            </div>
            <div className="w-32 flex items-center gap-2 text-sm text-muted-foreground">
              {v.is_secret ? (
                <><Lock className="h-4 w-4 text-primary" /> Secret</>
              ) : (
                <><Key className="h-4 w-4" /> Plain</>
              )}
            </div>
            <Button variant="ghost" size="icon" onClick={() => deleteVar(v.id)} className="text-destructive hover:text-destructive hover:bg-destructive/10">
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        ))}
      </div>
      
      <div className="flex items-center gap-4 p-4 rounded-xl border bg-primary/5 border-primary/20">
        <div className="flex-1">
          <Input 
            placeholder="KEY_NAME" 
            value={newKey} 
            onChange={e => setNewKey(e.target.value)}
            className="font-mono text-sm"
          />
        </div>
        <div className="flex-1">
          <Input 
            placeholder="Value" 
            value={newValue} 
            onChange={e => setNewValue(e.target.value)}
            className="font-mono text-sm"
          />
        </div>
        <div className="w-32 flex items-center gap-2">
          <Switch 
            checked={newIsSecret} 
            onCheckedChange={setNewIsSecret}
          />
          <span className="text-sm font-medium">{newIsSecret ? 'Secret' : 'Plain'}</span>
        </div>
        <Button onClick={handleAdd} disabled={!newKey.trim()}>
          <Plus className="h-4 w-4" /> Add
        </Button>
      </div>
    </div>
  );
};
