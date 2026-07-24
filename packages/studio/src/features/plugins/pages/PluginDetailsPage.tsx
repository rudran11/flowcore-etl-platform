import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, CheckCircle2, AlertCircle, Puzzle, 
  Terminal, Check, Copy, Download, Star, Loader2
} from 'lucide-react';
import { usePlugin, usePluginHealth, useValidatePlugin } from '../hooks/usePlugins';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { Skeleton } from '../../../components/ui/skeleton';
import { toast } from 'sonner';

export const PluginDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const { data: plugin, isLoading } = usePlugin(id!);
  const { data: health } = usePluginHealth(id!);
  const validateMutation = useValidatePlugin();

  const [yamlConfig, setYamlConfig] = useState(plugin?.example_yaml || '');
  const [isCopied, setIsCopied] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);

  // Update yaml state when plugin loads
  React.useEffect(() => {
    if (plugin?.example_yaml && !yamlConfig) {
      setYamlConfig(plugin.example_yaml);
    }
  }, [plugin, yamlConfig]);

  const handleCopy = () => {
    navigator.clipboard.writeText(yamlConfig);
    setIsCopied(true);
    toast.success('YAML configuration copied to clipboard');
    setTimeout(() => setIsCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([yamlConfig], { type: 'text/yaml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${plugin?.name || 'plugin'}-config.yaml`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Configuration downloaded');
  };

  const handleValidate = () => {
    if (!id) return;
    
    validateMutation.mutate(
      { plugin_id: id, config: { yaml: yamlConfig } },
      {
        onSuccess: (data) => {
          if (data.success) {
            toast.success('Plugin configuration is valid!');
          } else {
            toast.error('Validation failed', {
              description: data.errors.join('\\n')
            });
          }
        },
        onError: () => {
          toast.error('Validation request failed. Is the backend running?');
        }
      }
    );
  };

  if (isLoading) {
    return (
      <div className="p-8 max-w-7xl mx-auto space-y-8">
        <div className="flex items-center gap-4">
          <Skeleton className="w-10 h-10 rounded-full" />
          <Skeleton className="h-8 w-64" />
        </div>
        <Skeleton className="h-[400px] w-full rounded-xl" />
      </div>
    );
  }

  if (!plugin) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <Puzzle className="w-12 h-12 text-zinc-500 mb-4" />
        <h3 className="text-xl font-medium text-white mb-2">Plugin Not Found</h3>
        <p className="text-zinc-500 mb-6">The requested plugin does not exist or has been removed.</p>
        <Button onClick={() => navigate('/plugins')}>Back to Hub</Button>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/plugins')} className="mt-1 shrink-0">
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div className="w-14 h-14 rounded-xl bg-zinc-900 flex items-center justify-center border border-white/5 shadow-inner shrink-0 mt-0.5">
            <Puzzle className="w-7 h-7 text-zinc-400" />
          </div>
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-3xl font-bold tracking-tight text-white">{plugin.name}</h1>
              <Badge variant="outline" className="bg-white/5 border-white/10">v{plugin.version}</Badge>
              <Button 
                variant="ghost" 
                size="icon" 
                className={`h-8 w-8 ${isFavorite ? 'text-yellow-500' : 'text-zinc-500 hover:text-zinc-300'}`}
                onClick={() => setIsFavorite(!isFavorite)}
              >
                <Star className={`w-5 h-5 ${isFavorite ? 'fill-current' : ''}`} />
              </Button>
            </div>
            <p className="text-zinc-400 text-lg max-w-2xl">{plugin.description}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="outline" className="bg-zinc-950 border-white/10" onClick={handleValidate} disabled={validateMutation.isPending}>
            {validateMutation.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <CheckCircle2 className="w-4 h-4 mr-2" />}
            Validate
          </Button>
        </div>
      </div>

      {/* Meta Bar */}
      <div className="flex flex-wrap items-center gap-4 p-4 bg-zinc-950/40 rounded-xl border border-white/5 backdrop-blur-sm">
        <div className="flex items-center gap-2">
          <span className="text-sm text-zinc-500">Author:</span>
          <span className="text-sm font-medium text-zinc-300">{plugin.author || 'FlowCore'}</span>
        </div>
        <div className="w-px h-4 bg-white/10" />
        <div className="flex items-center gap-2">
          <span className="text-sm text-zinc-500">Category:</span>
          <Badge variant="secondary" className="bg-zinc-900 border-white/5 font-normal">{plugin.category}</Badge>
        </div>
        <div className="w-px h-4 bg-white/10" />
        <div className="flex items-center gap-2">
          <span className="text-sm text-zinc-500">Compatibility:</span>
          <span className="text-sm font-medium text-zinc-300">FlowCore {plugin.compatibility || '>=1.0.0'}</span>
        </div>
        <div className="w-px h-4 bg-white/10" />
        <div className="flex items-center gap-2">
          <span className="text-sm text-zinc-500">Dependencies:</span>
          {plugin.dependencies && plugin.dependencies.length > 0 ? (
            <div className="flex gap-1">
              {plugin.dependencies.map((dep: string) => (
                <Badge key={dep} variant="outline" className="bg-zinc-900 border-white/5 font-normal">{dep}</Badge>
              ))}
            </div>
          ) : (
            <span className="text-sm font-medium text-zinc-500">None</span>
          )}
        </div>
        <div className="w-px h-4 bg-white/10" />
        <div className="flex items-center gap-2">
          <span className="text-sm text-zinc-500">Health:</span>
          {health ? (
            <Badge className="bg-emerald-500/10 text-emerald-500 border-0 shadow-none gap-1 font-medium">
              <CheckCircle2 className="w-3.5 h-3.5" />
              {health.status}
            </Badge>
          ) : (
            <Skeleton className="w-20 h-5" />
          )}
        </div>
      </div>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="bg-zinc-950/50 border border-white/5 w-full justify-start p-1 rounded-lg">
          <TabsTrigger value="overview" className="data-[state=active]:bg-zinc-900 data-[state=active]:text-white">Overview</TabsTrigger>
          <TabsTrigger value="configuration" className="data-[state=active]:bg-zinc-900 data-[state=active]:text-white">Configuration</TabsTrigger>
          <TabsTrigger value="diagnostics" className="data-[state=active]:bg-zinc-900 data-[state=active]:text-white">Diagnostics</TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview" className="mt-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="bg-zinc-950/40 border-white/5">
              <CardHeader>
                <CardTitle className="text-lg">Capabilities</CardTitle>
              </CardHeader>
              <CardContent>
                {plugin.capabilities?.length > 0 ? (
                  <ul className="space-y-3">
                    {plugin.capabilities.map((cap, i) => (
                      <li key={i} className="flex items-start gap-3 text-zinc-300">
                        <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
                        <span>{cap}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-zinc-500 text-sm">No capabilities documented.</p>
                )}
              </CardContent>
            </Card>

            <Card className="bg-zinc-950/40 border-white/5">
              <CardHeader>
                <CardTitle className="text-lg">Supported Operations</CardTitle>
              </CardHeader>
              <CardContent>
                {plugin.supported_operations?.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {plugin.supported_operations.map((op, i) => (
                      <Badge key={i} variant="outline" className="bg-white/5 border-white/10 text-zinc-300 font-normal py-1 px-3">
                        {op}
                      </Badge>
                    ))}
                  </div>
                ) : (
                  <p className="text-zinc-500 text-sm">No specific operations documented.</p>
                )}
              </CardContent>
            </Card>
          </div>

          <Card className="bg-zinc-950/40 border-white/5">
            <CardHeader>
              <CardTitle className="text-lg">Documentation</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="prose prose-invert max-w-none text-zinc-300">
                {plugin.documentation ? (
                  <div dangerouslySetInnerHTML={{ __html: plugin.documentation.replace(/\\n/g, '<br/>') }} />
                ) : (
                  <p className="text-zinc-500 italic">No detailed documentation provided for this plugin.</p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="configuration" className="mt-6">
          <Card className="bg-zinc-950/40 border-white/5 overflow-hidden">
            <CardHeader className="flex flex-row items-center justify-between bg-zinc-900/50 border-b border-white/5 pb-4">
              <div>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Terminal className="w-5 h-5 text-zinc-400" />
                  YAML Configuration
                </CardTitle>
                <CardDescription>Example configuration payload for pipeline steps.</CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={handleDownload} className="bg-zinc-950 border-white/10">
                  <Download className="w-4 h-4 mr-2" /> Download
                </Button>
                <Button variant="secondary" size="sm" onClick={handleCopy} className="w-24">
                  {isCopied ? <Check className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
                  {isCopied ? 'Copied!' : 'Copy'}
                </Button>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="bg-[#0d1117] p-6 font-mono text-sm text-zinc-300 overflow-x-auto">
                <pre>
                  <code>{plugin.example_yaml || '# No example configuration available'}</code>
                </pre>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="diagnostics" className="mt-6">
          <Card className="bg-zinc-950/40 border-white/5">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-zinc-400" />
                Health Diagnostics
              </CardTitle>
            </CardHeader>
            <CardContent>
              {health?.diagnostics?.length ? (
                <ul className="space-y-2">
                  {health.diagnostics.map((diag, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-zinc-400 bg-zinc-900/50 p-3 rounded-lg border border-white/5">
                      <ArrowLeft className="w-4 h-4 text-zinc-500 shrink-0 mt-0.5" />
                      {diag}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-zinc-500 text-sm">No diagnostic issues reported. Plugin is healthy.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};
