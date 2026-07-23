import React from 'react';

interface DashboardCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: React.ReactNode;
  trend?: { value: number; label: string };
  loading?: boolean;
}

export const DashboardCard: React.FC<DashboardCardProps> = ({ title, value, description, icon, trend, loading }) => {
  return (
    <div className="rounded-xl border bg-card text-card-foreground shadow">
      <div className="p-6 flex flex-row items-center justify-between space-y-0 pb-2">
        <h3 className="tracking-tight text-sm font-medium">{title}</h3>
        {icon && <div className="text-muted-foreground">{icon}</div>}
      </div>
      <div className="p-6 pt-0">
        {loading ? (
          <div className="space-y-2">
            <div className="h-8 w-1/2 rounded-md bg-muted animate-pulse"></div>
            <div className="h-4 w-3/4 rounded-md bg-muted animate-pulse mt-2"></div>
          </div>
        ) : (
          <>
            <div className="text-2xl font-bold">{value}</div>
            <div className="flex items-center space-x-2 mt-1">
              {trend && (
                <span className={`text-xs ${trend.value > 0 ? 'text-emerald-500' : trend.value < 0 ? 'text-red-500' : 'text-muted-foreground'}`}>
                  {trend.value > 0 ? '+' : ''}{trend.value}%
                </span>
              )}
              {description && <p className="text-xs text-muted-foreground">{description}</p>}
            </div>
          </>
        )}
      </div>
    </div>
  );
};
