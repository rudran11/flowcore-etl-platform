import { createBrowserRouter } from 'react-router-dom';
import { RootLayout } from '../layouts/RootLayout';
import { DashboardPage } from '../features/dashboard/DashboardPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      {
        index: true,
        element: <DashboardPage />,
      },
      {
        path: 'pipelines',
        element: <div className="p-8">Pipelines Page (Coming Soon)</div>,
      },
      {
        path: 'runs',
        element: <div className="p-8">Runs Page (Coming Soon)</div>,
      },
      {
        path: 'settings',
        element: <div className="p-8">Settings Page (Coming Soon)</div>,
      },
    ],
  },
]);
