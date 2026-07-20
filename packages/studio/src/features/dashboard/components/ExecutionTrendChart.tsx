import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { ExecutionTrend } from '../../../types/dashboard';

interface ExecutionTrendChartProps {
  data: ExecutionTrend[];
}

export const ExecutionTrendChart: React.FC<ExecutionTrendChartProps> = ({ data }) => {
  return (
    <div className="rounded-xl border bg-card text-card-foreground shadow col-span-4">
      <div className="flex flex-col space-y-1.5 p-6">
        <h3 className="font-semibold leading-none tracking-tight">Execution Trends</h3>
        <p className="text-sm text-muted-foreground">Pipeline executions over the last 7 days</p>
      </div>
      <div className="p-6 pt-0">
        <div className="h-[350px] w-full flex items-center justify-center">
          {data.length === 0 ? (
            <div className="text-muted-foreground text-sm flex flex-col items-center">
              <span>No execution data available for this period.</span>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--muted-foreground)/0.2)" />
                <XAxis dataKey="date" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'hsl(var(--background))', borderColor: 'hsl(var(--border))', borderRadius: '8px' }}
                  itemStyle={{ color: 'hsl(var(--foreground))' }}
                />
                <Legend wrapperStyle={{ paddingTop: '20px' }} />
                <Bar dataKey="completed" name="Completed" stackId="a" fill="#10b981" radius={[0, 0, 4, 4]} />
                <Bar dataKey="failed" name="Failed" stackId="a" fill="#ef4444" radius={[0, 0, 0, 0]} />
                <Bar dataKey="running" name="Running" stackId="a" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
};
