import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { CheckCircle2, XCircle, AlertCircle, Puzzle, ChevronRight } from 'lucide-react';
import { Card, CardContent, CardFooter, CardHeader } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { PluginResponse } from '../../../types/plugin';

interface PluginCardProps {
  plugin: PluginResponse;
  healthStatus?: string;
  viewMode: 'grid' | 'list';
}

export const PluginCard: React.FC<PluginCardProps> = ({ plugin, healthStatus, viewMode }) => {
  const isGrid = viewMode === 'grid';

  const getHealthIcon = () => {
    switch (healthStatus) {
      case 'READY':
      case 'VALIDATED':
        return <CheckCircle2 className="w-4 h-4 text-emerald-500" />;
      case 'ERROR':
        return <XCircle className="w-4 h-4 text-rose-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-amber-500" />;
    }
  };

  const getHealthColor = () => {
    switch (healthStatus) {
      case 'READY':
      case 'VALIDATED':
        return 'bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20';
      case 'ERROR':
        return 'bg-rose-500/10 text-rose-500 hover:bg-rose-500/20';
      default:
        return 'bg-amber-500/10 text-amber-500 hover:bg-amber-500/20';
    }
  };

  if (!isGrid) {
    return (
      <motion.div
        whileHover={{ y: -2 }}
        className="group flex items-center justify-between p-4 bg-zinc-950/40 border border-white/5 rounded-xl hover:border-white/10 hover:bg-zinc-900/40 transition-all duration-300"
      >
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-lg bg-zinc-900 flex items-center justify-center border border-white/5 shadow-inner">
            <Puzzle className="w-6 h-6 text-zinc-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-medium text-white">{plugin.name}</h3>
              <Badge variant="outline" className="bg-white/5 border-white/10 text-xs text-zinc-400">
                v{plugin.version}
              </Badge>
            </div>
            <p className="text-sm text-zinc-400 max-w-xl truncate">{plugin.description}</p>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <Badge className={`font-medium ${getHealthColor()} border-0 shadow-none gap-1`}>
            {getHealthIcon()}
            {healthStatus || 'Unknown'}
          </Badge>
          <div className="text-sm text-zinc-500 hidden md:block">{plugin.category}</div>
          <Button variant="ghost" size="icon" asChild className="opacity-0 group-hover:opacity-100 transition-opacity">
            <Link to={`/plugins/${plugin.plugin_id}`}>
              <ChevronRight className="w-4 h-4" />
            </Link>
          </Button>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div whileHover={{ y: -4 }}>
      <Card className="h-full bg-zinc-950/40 border-white/5 backdrop-blur-sm hover:border-white/10 hover:bg-zinc-900/40 transition-all duration-300 flex flex-col group overflow-hidden">
        <CardHeader className="flex flex-row items-start justify-between pb-4">
          <div className="w-12 h-12 rounded-lg bg-zinc-900 flex items-center justify-center border border-white/5 shadow-inner">
            <Puzzle className="w-6 h-6 text-zinc-400" />
          </div>
          <Badge variant="outline" className="bg-white/5 border-white/10 text-xs text-zinc-400">
            v{plugin.version}
          </Badge>
        </CardHeader>
        
        <CardContent className="flex-1 pb-4">
          <h3 className="font-semibold text-lg text-white mb-1 group-hover:text-zinc-100 transition-colors">
            {plugin.name}
          </h3>
          <p className="text-sm text-zinc-400 line-clamp-2 leading-relaxed">
            {plugin.description}
          </p>
          
          <div className="mt-4 flex flex-wrap gap-2">
            <Badge variant="secondary" className="bg-zinc-900 hover:bg-zinc-800 text-zinc-300 text-xs font-normal border border-white/5">
              {plugin.category}
            </Badge>
            {plugin.compatibility && (
              <Badge variant="secondary" className="bg-zinc-900 hover:bg-zinc-800 text-zinc-400 text-xs font-normal border border-white/5">
                FlowCore {plugin.compatibility}
              </Badge>
            )}
          </div>
        </CardContent>

        <CardFooter className="pt-4 border-t border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Badge className={`px-2 py-0.5 text-xs font-medium ${getHealthColor()} border-0 shadow-none gap-1`}>
              {getHealthIcon()}
              {healthStatus || 'Unknown'}
            </Badge>
          </div>
          <Button variant="ghost" size="sm" asChild className="h-8 text-xs font-medium hover:bg-white/5 hover:text-white">
            <Link to={`/plugins/${plugin.plugin_id}`}>
              View Details <ChevronRight className="w-3.5 h-3.5 ml-1" />
            </Link>
          </Button>
        </CardFooter>
      </Card>
    </motion.div>
  );
};
