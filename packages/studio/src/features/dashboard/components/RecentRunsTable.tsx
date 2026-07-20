import React from 'react';

interface RecentRunsTableProps {
  runs: any[];
}

const getStatusColor = (status: string) => {
  switch (status.toUpperCase()) {
    case 'COMPLETED': return 'bg-emerald-500/10 text-emerald-500';
    case 'FAILED': return 'bg-red-500/10 text-red-500';
    case 'RUNNING': return 'bg-blue-500/10 text-blue-500';
    case 'QUEUED': return 'bg-yellow-500/10 text-yellow-500';
    default: return 'bg-gray-500/10 text-gray-500';
  }
};

export const RecentRunsTable: React.FC<RecentRunsTableProps> = ({ runs }) => {
  return (
    <div className="rounded-xl border bg-card text-card-foreground shadow col-span-3">
      <div className="flex flex-col space-y-1.5 p-6">
        <h3 className="font-semibold leading-none tracking-tight">Recent Executions</h3>
        <p className="text-sm text-muted-foreground">The latest pipeline runs across the system</p>
      </div>
      <div className="p-6 pt-0">
        <div className="relative w-full overflow-auto">
          <table className="w-full caption-bottom text-sm">
            <thead className="[&_tr]:border-b">
              <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Pipeline ID</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Status</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Trigger</th>
                <th className="h-12 px-4 text-right align-middle font-medium text-muted-foreground">Started</th>
              </tr>
            </thead>
            <tbody className="[&_tr:last-child]:border-0">
              {runs.map((run, i) => (
                <tr key={i} className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                  <td className="p-4 align-middle font-medium">{run.pipeline_id}</td>
                  <td className="p-4 align-middle">
                    <div className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 ${getStatusColor(run.status)} border-transparent`}>
                      {run.status}
                    </div>
                  </td>
                  <td className="p-4 align-middle">{run.trigger_type}</td>
                  <td className="p-4 align-middle text-right text-muted-foreground">
                    {run.start_time ? new Date(run.start_time).toLocaleString() : 'N/A'}
                  </td>
                </tr>
              ))}
              {runs.length === 0 && (
                <tr>
                  <td colSpan={4} className="p-4 text-center text-muted-foreground">No recent runs</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
