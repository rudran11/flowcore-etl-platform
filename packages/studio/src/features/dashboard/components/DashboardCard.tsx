import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';

interface DashboardCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  description?: string;
}

export const DashboardCard: React.FC<DashboardCardProps> = ({ title, value, icon, description }) => {
  return (
    <Card className="hover:shadow-lg transition-all duration-200 border-muted bg-card">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        {icon && <div className="text-muted-foreground">{icon}</div>}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {description && (
          <p className="text-xs text-muted-foreground mt-1">
            {description}
          </p>
        )}
      </CardContent>
    </Card>
  );
};
