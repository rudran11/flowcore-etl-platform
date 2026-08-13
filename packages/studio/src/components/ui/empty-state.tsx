import React from 'react';
import { cn } from '../../lib/utils';
import { LucideIcon } from 'lucide-react';

interface EmptyStateProps {
  icon?: LucideIcon;
  illustration?: React.ReactNode;
  title: string;
  description: string;
  action?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon,
  illustration,
  title,
  description,
  action,
  className
}) => {
  return (
    <div className={cn("flex flex-col items-center justify-center p-12 text-center rounded-xl border border-border shadow-surface bg-card/50 backdrop-blur-sm relative overflow-hidden", className)}>
      <div className="absolute inset-0 bg-dot-topology opacity-20 pointer-events-none" />
      
      {illustration ? (
        <div className="mb-6 relative z-10 w-48 h-32 flex items-center justify-center text-primary">
          {illustration}
        </div>
      ) : Icon ? (
        <div className="flex h-16 w-16 items-center justify-center rounded-xl bg-accent/50 text-muted-foreground mb-4 border border-border shadow-sm relative z-10">
          <Icon className="h-8 w-8 opacity-70" />
        </div>
      ) : null}
      
      <h3 className="text-lg font-bold tracking-tight text-foreground mb-2 relative z-10">{title}</h3>
      <p className="text-sm text-muted-foreground max-w-[400px] mb-6 leading-relaxed">
        {description}
      </p>
      {action && (
        <div>{action}</div>
      )}
    </div>
  );
};
