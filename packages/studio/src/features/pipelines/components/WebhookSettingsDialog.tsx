import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../../../components/ui/dialog';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';

import { Key, Link as LinkIcon, RefreshCw, Copy, CheckCircle2 } from 'lucide-react';
import { toast } from 'sonner';

interface WebhookSettingsDialogProps {
  pipelineId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const WebhookSettingsDialog: React.FC<WebhookSettingsDialogProps> = ({ open, onOpenChange }) => {
  const [webhookId, setWebhookId] = useState<string | null>(null);
  const [secret, setSecret] = useState<string | null>(null);
  const [isActive, setIsActive] = useState(true);
  const [copied, setCopied] = useState(false);
  const [copiedSecret, setCopiedSecret] = useState(false);

  // In a real app, this would fetch from/save to API. 
  // For UI MVP, we simulate it.
  const handleGenerate = () => {
    setWebhookId(crypto.randomUUID());
    setSecret("sec_" + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15));
    toast.success("Webhook credentials generated. Make sure to save the secret key!");
  };

  const handleCopy = (text: string, type: 'url' | 'secret') => {
    navigator.clipboard.writeText(text);
    if (type === 'url') {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } else {
      setCopiedSecret(true);
      setTimeout(() => setCopiedSecret(false), 2000);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <LinkIcon className="w-5 h-5 text-primary" />
            Webhook Settings
          </DialogTitle>
        </DialogHeader>

        <div className="py-4 space-y-6">
          <p className="text-sm text-muted-foreground">
            Configure a webhook to trigger this pipeline externally via HTTP POST requests.
          </p>

          {!webhookId ? (
            <div className="flex flex-col items-center justify-center py-6 border border-dashed border-border rounded-lg bg-accent/20">
              <Key className="w-8 h-8 text-muted-foreground mb-3 opacity-50" />
              <p className="text-sm text-muted-foreground mb-4">No webhook configured for this pipeline.</p>
              <Button onClick={handleGenerate} className="gap-2">
                <RefreshCw className="w-4 h-4" /> Generate Webhook
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium leading-none">Webhook URL</label>
                <div className="flex gap-2">
                  <Input readOnly value={`http://localhost:8000/api/v1/webhooks/${webhookId}`} className="font-mono text-xs" />
                  <Button variant="outline" size="icon" onClick={() => handleCopy(`http://localhost:8000/api/v1/webhooks/${webhookId}`, 'url')}>
                    {copied ? <CheckCircle2 className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium leading-none">HMAC Secret Key</label>
                <div className="flex gap-2">
                  <Input readOnly value={secret || ''} className="font-mono text-xs" type="password" />
                  <Button variant="outline" size="icon" onClick={() => handleCopy(secret || '', 'secret')}>
                    {copiedSecret ? <CheckCircle2 className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
                  </Button>
                </div>
                <p className="text-[11px] text-amber-500">This secret will only be shown once. Store it securely.</p>
              </div>

              <div className="flex items-center space-x-2 pt-2">
                <input type="checkbox" id="active" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary" />
                <label htmlFor="active" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                  Webhook Active
                </label>
              </div>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Close</Button>
          {webhookId && <Button onClick={() => onOpenChange(false)}>Save Settings</Button>}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
