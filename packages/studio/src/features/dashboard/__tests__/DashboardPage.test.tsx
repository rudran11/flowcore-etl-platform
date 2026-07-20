import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DashboardPage } from '../DashboardPage';
import * as useDashboardHook from '../hooks/useDashboard';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('../components/ExecutionTrendChart', () => ({
  ExecutionTrendChart: () => <div data-testid="trend-chart">Trend Chart</div>
}));

const queryClient = new QueryClient();

const renderWithProvider = (ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      {ui}
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

    renderWithProvider(<DashboardPage />);
    expect(screen.getByText('Loading dashboard...')).toBeInTheDocument();
  });

  it('renders error state', () => {
    vi.spyOn(useDashboardHook, 'useDashboard').mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Network Error'),
    } as any);

    renderWithProvider(<DashboardPage />);
    expect(screen.getByText(/Error loading dashboard data/i)).toBeInTheDocument();
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

    renderWithProvider(<DashboardPage />);
    expect(screen.getByText('System Online')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();
    expect(screen.getByText('95%')).toBeInTheDocument();
    expect(screen.getByText('1.5s')).toBeInTheDocument();
    expect(screen.getByTestId('trend-chart')).toBeInTheDocument();
  });
});
