import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { usePipelines } from '../hooks/usePipelines';
import { PipelineTable } from '../components/PipelineTable';
import { PipelineSearch } from '../components/PipelineSearch';
import { PageTransition } from '../../../components/ui/PageTransition';
import { Button } from '../../../components/ui/button';
import { ChevronLeft, ChevronRight, Filter } from 'lucide-react';
import { toast } from 'sonner';
import { Skeleton } from '../../../components/ui/skeleton';

export const PipelinesPage: React.FC = () => {
  const [search, setSearch] = useState('');
  const [skip, setSkip] = useState(0);
  const [limit] = useState(25);

  const { data, isLoading, error } = usePipelines({ 
    skip, 
    limit, 
    search: search ? search : undefined,
    tags: undefined 
  });

  useEffect(() => {
    if (error) {
      toast.error('Failed to load pipelines data');
    }
  }, [error]);

  const handleNext = () => setSkip(prev => prev + limit);
  const handlePrev = () => setSkip(prev => Math.max(0, prev - limit));

  return (
    <PageTransition className="flex-1 space-y-6">
      <div className="flex items-center justify-between space-y-2">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Pipelines</h2>
          <p className="text-muted-foreground mt-1 text-sm">Manage and monitor all your data pipelines in one place.</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex-1 max-w-md">
          <PipelineSearch value={search} onChange={(val) => { setSearch(val); setSkip(0); }} placeholder="Search pipelines by name or description..." />
        </div>
        <Button variant="outline" className="flex items-center gap-2">
          <Filter className="h-4 w-4" />
          Filter
        </Button>
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-xl border bg-card text-card-foreground shadow-sm overflow-hidden"
      >
        {isLoading ? (
          <div className="p-6 space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex gap-4">
                <Skeleton className="h-6 w-1/4" />
                <Skeleton className="h-6 w-1/4" />
                <Skeleton className="h-6 w-1/2" />
              </div>
            ))}
          </div>
        ) : (
          <PipelineTable pipelines={data?.items || []} loading={isLoading} />
        )}
      </motion.div>
      
      {data && data.total > 0 && (
        <div className="flex items-center justify-between px-2">
          <div className="text-sm text-muted-foreground font-medium">
            Showing {data.skip + 1} to {Math.min(data.skip + data.limit, data.total)} of {data.total} pipelines
          </div>
          <div className="flex space-x-2">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handlePrev} 
              disabled={skip === 0}
              className="w-24"
            >
              <ChevronLeft className="mr-2 h-4 w-4" />
              Previous
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleNext} 
              disabled={skip + limit >= data.total}
              className="w-24"
            >
              Next
              <ChevronRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </PageTransition>
  );
};
