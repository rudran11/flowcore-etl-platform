import { createBrowserRouter, Navigate } from 'react-router-dom';
import { RootLayout } from '../layouts/RootLayout';
import { ProtectedRoute } from '../features/auth/components/ProtectedRoute';
import { LoginPage } from '../features/auth/LoginPage';
import { DashboardPage } from '../features/dashboard/DashboardPage';
import { PipelinesPage } from '../features/pipelines/pages/PipelinesPage';
import { PipelineDetailsPage } from '../features/pipelines/pages/PipelineDetailsPage';
import { ExecutionsPage } from '../features/executions/pages/ExecutionsPage';
import { ExecutionDetailsPage } from '../features/executions/pages/ExecutionDetailsPage';
import { PluginsPage } from '../features/plugins/pages/PluginsPage';
import { PluginDetailsPage } from '../features/plugins/pages/PluginDetailsPage';
import { SettingsPage } from '../features/settings/pages/SettingsPage';
import { SchedulesPage } from '../features/schedules/pages/SchedulesPage';
import { EnvironmentsPage } from '../features/environments/pages/EnvironmentsPage';
import { EnvironmentDetailsPage } from '../features/environments/pages/EnvironmentDetailsPage';
import { DatasetsPage } from '../features/datasets/DatasetsPage';
import { DatasetDetailsPage } from '../features/datasets/DatasetDetailsPage';
import { ErrorBoundary } from '../components/ErrorBoundary';

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: <ProtectedRoute />,
    children: [
      {
        path: '/',
        element: (
          <ErrorBoundary>
            <RootLayout />
          </ErrorBoundary>
        ),
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
        path: 'environments',
        element: <EnvironmentsPage />,
      },
      {
        path: 'environments/:id',
        element: <EnvironmentDetailsPage />,
      },
      {
        path: 'datasets',
        element: <DatasetsPage />,
      },
      {
        path: 'datasets/:id',
        element: <DatasetDetailsPage />,
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
    ],
  },
]);
