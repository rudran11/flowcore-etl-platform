import React from 'react';

interface DashboardGridProps {
  children: React.ReactNode;
}

export const DashboardGrid: React.FC<DashboardGridProps> = ({ children }) => {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {children}
    </div>
  );
};
