import React from 'react';

interface PipelineStatusBadgeProps {
  status: string;
}

export const PipelineStatusBadge: React.FC<PipelineStatusBadgeProps> = ({ status }) => {
  const getStatusStyles = (s: string) => {
    switch (s.toLowerCase()) {
      case 'completed':
      case 'success':
        return 'bg-emerald-500/15 text-emerald-600 border-emerald-500/20';
      case 'failed':
      case 'error':
        return 'bg-red-500/15 text-red-600 border-red-500/20';
      case 'running':
      case 'in_progress':
        return 'bg-blue-500/15 text-blue-600 border-blue-500/20 animate-pulse';
      case 'pending':
        return 'bg-amber-500/15 text-amber-600 border-amber-500/20';
      default:
        return 'bg-gray-500/15 text-gray-600 border-gray-500/20';
    }
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${getStatusStyles(status)}`}>
      {status}
    </span>
  );
};
