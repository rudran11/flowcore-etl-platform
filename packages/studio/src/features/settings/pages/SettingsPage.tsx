import React from 'react';
import { Settings } from 'lucide-react';
import { PageHeader } from '../../../components/ui/page-header';
import { EmptyState } from '../../../components/ui/empty-state';

export const SettingsPage: React.FC = () => {
  return (
    <div className="p-6 md:p-8 max-w-[1400px] mx-auto space-y-8 animate-in fade-in duration-500 w-full">
      <PageHeader
        title="Settings"
        subtitle="Manage your workspace preferences, API keys, and team members."
        icon={Settings}
      />
      
      <EmptyState
        icon={Settings}
        title="Settings module under construction"
        description="We are currently building out the settings and administration capabilities for FlowCore Studio."
      />
    </div>
  );
};
