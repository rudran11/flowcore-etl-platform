import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './card';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { cn } from '../../lib/utils';

export interface StatCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  description?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({ title, value, icon, description, trend, trendValue, className }) => {
  return (
    <Card className={cn("group relative overflow-hidden transition-all duration-300 border-border/50 bg-card hover:border-primary/50 hover:shadow-md", className)}>
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
      <CardHeader className="relative flex flex-row items-center justify-between pb-2 z-10 space-y-0">
        <CardTitle className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{title}</CardTitle>
        {icon && <div className="text-muted-foreground bg-accent/50 p-1.5 rounded-md text-primary">{icon}</div>}
      </CardHeader>
      <CardContent className="relative z-10">
        <div className="flex items-baseline gap-2">
          <div className="text-3xl font-bold tracking-tight text-foreground">{value}</div>
          {trend && trendValue && (
            <div className={cn(
              "flex items-center text-xs font-medium",
              trend === 'up' ? "text-emerald-500" : trend === 'down' ? "text-destructive" : "text-muted-foreground"
            )}>
              {trend === 'up' && <TrendingUp className="mr-1 h-3 w-3" />}
              {trend === 'down' && <TrendingDown className="mr-1 h-3 w-3" />}
              {trendValue}
            </div>
          )}
        </div>
        {description && (
          <p className="text-xs text-muted-foreground mt-2 font-medium">
            {description}
          </p>
        )}
      </CardContent>
    </Card>
  );
};
