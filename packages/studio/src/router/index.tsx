import { createBrowserRouter, Navigate } from 'react-router-dom';
import { RootLayout } from '../layouts/RootLayout';
import { DashboardPage } from '../features/dashboard/DashboardPage';
import { PipelinesPage } from '../features/pipelines/pages/PipelinesPage';
import { PipelineDetailsPage } from '../features/pipelines/pages/PipelineDetailsPage';
import { ExecutionsPage } from '../features/executions/pages/ExecutionsPage';
import { ExecutionDetailsPage } from '../features/executions/pages/ExecutionDetailsPage';
import { PluginsPage } from '../features/plugins/pages/PluginsPage';
import { PluginDetailsPage } from '../features/plugins/pages/PluginDetailsPage';
import { SettingsPage } from '../features/settings/pages/SettingsPage';
import { SchedulesPage } from '../features/schedules/pages/SchedulesPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: <DashboardPage />,
      },
      {
        path: 'pipelines',
        element: <PipelinesPage />,
      },
      {
        path: 'pipelines/:id',
        element: <PipelineDetailsPage />,
      },
      {
        path: 'schedules',
        element: <SchedulesPage />,
      },
      {
        path: 'runs',
        element: <ExecutionsPage />,
      },
      {
        path: 'runs/:id',
        element: <ExecutionDetailsPage />,
      },
      {
        path: 'plugins',
        element: <PluginsPage />,
      },
      {
        path: 'plugins/:id',
        element: <PluginDetailsPage />,
      },
      {
        path: 'settings',
        element: <SettingsPage />,
      },
    ],
  },
]);
