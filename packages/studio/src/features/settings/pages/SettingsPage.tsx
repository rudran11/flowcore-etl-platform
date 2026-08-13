import React from 'react';
import { Settings, Users, Key, Sliders } from 'lucide-react';
import { PageHeader } from '../../../components/ui/page-header';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { GeneralTab } from '../components/GeneralTab';
import { MembersTab } from '../components/MembersTab';
import { ApiKeysTab } from '../components/ApiKeysTab';

export const SettingsPage: React.FC = () => {
  return (
    <div className="p-6 md:p-8 max-w-[1400px] mx-auto space-y-8 animate-in fade-in duration-500 w-full">
      <PageHeader
        title="Settings"
        subtitle="Manage your workspace preferences, API keys, and team members."
        icon={Settings}
      />
      
      <Tabs defaultValue="general" className="w-full">
        <TabsList className="bg-black/40 border border-white/10 p-1 mb-8">
          <TabsTrigger value="general" className="data-[state=active]:bg-white/10 data-[state=active]:text-white">
            <Sliders className="h-4 w-4 mr-2" />
            General
          </TabsTrigger>
          <TabsTrigger value="members" className="data-[state=active]:bg-white/10 data-[state=active]:text-white">
            <Users className="h-4 w-4 mr-2" />
            Members
          </TabsTrigger>
          <TabsTrigger value="apikeys" className="data-[state=active]:bg-white/10 data-[state=active]:text-white">
            <Key className="h-4 w-4 mr-2" />
            API Keys
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="general" className="mt-0 outline-none">
          <GeneralTab />
        </TabsContent>
        
        <TabsContent value="members" className="mt-0 outline-none">
          <MembersTab />
        </TabsContent>
        
        <TabsContent value="apikeys" className="mt-0 outline-none">
          <ApiKeysTab />
        </TabsContent>
      </Tabs>
    </div>
  );
};
