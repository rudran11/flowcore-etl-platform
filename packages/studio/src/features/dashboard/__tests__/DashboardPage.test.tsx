import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DashboardPage } from '../DashboardPage';
import * as useDashboardHook from '../hooks/useDashboard';
import * as useSchedulerMetricsHook from '../hooks/useSchedulerMetrics';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';

vi.mock('../components/ExecutionTrendChart', () => ({
  ExecutionTrendChart: () => <div data-testid="trend-chart">Trend Chart</div>
}));

const queryClient = new QueryClient();

const renderWithProvider = (ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {ui}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('DashboardPage', () => {
  it('renders loading state', () => {
    vi.spyOn(useDashboardHook, 'useDashboard').mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as any);

    const { container } = renderWithProvider(<DashboardPage />);
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
  });

  it('renders error state', () => {
    vi.spyOn(useDashboardHook, 'useDashboard').mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Network Error'),
    } as any);

    renderWithProvider(<DashboardPage />);
    expect(screen.getByText(/Error Loading Dashboard/i)).toBeInTheDocument();
  });

  it('renders success state', () => {
    vi.spyOn(useDashboardHook, 'useDashboard').mockReturnValue({
      data: {
        health: { server: 'healthy' },
        statistics: {
          total_pipelines: 10,
          total_runs: 100,
          success_rate: 95,
          avg_duration_ms: 1500,
        },
        trends: [],
        recent_runs: [],
      },
      isLoading: false,
      error: null,
    } as any);

    vi.spyOn(useSchedulerMetricsHook, 'useSchedulerMetrics').mockReturnValue({
      data: {
        queue_length: 5,
        avg_execution_delay_seconds: 1.5,
        success_rate: 0.95,
        failure_rate: 0.05,
        last_heartbeat: '2026-07-24T00:00:00Z',
        missed_schedules: 0
      },
      isLoading: false,
      error: null,
    } as any);

    renderWithProvider(<DashboardPage />);
    expect(screen.getByText('System Online')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();
    expect(screen.getByText('95.0%')).toBeInTheDocument();
    expect(screen.getByText('1.5s')).toBeInTheDocument();
    expect(screen.getByTestId('trend-chart')).toBeInTheDocument();
  });
});
