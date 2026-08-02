import React from 'react';
import { cn } from '../../lib/utils';
import { LucideIcon } from 'lucide-react';

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon,
  title,
  description,
  action,
  className
}) => {
  return (
    <div className={cn("flex flex-col items-center justify-center p-12 text-center rounded-xl border border-border/50 bg-card/30 backdrop-blur-sm", className)}>
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-accent/50 text-muted-foreground mb-4">
        <Icon className="h-8 w-8 opacity-50" />
      </div>
      <h3 className="text-lg font-semibold tracking-tight text-foreground mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground max-w-[400px] mb-6 leading-relaxed">
        {description}
      </p>
      {action && (
        <div>{action}</div>
      )}
    </div>
  );
};
