import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useDashboard } from '../hooks/useDashboard';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { apiClient } from '../../../api/client';

vi.mock('../../../api/client', () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

vi.mock('../../../stores/authStore', () => ({
  useAuthStore: vi.fn(() => ({ activeWorkspaceId: 'mock-ws' })),
}));

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
);

describe('useDashboard', () => {
  beforeEach(() => {
    queryClient.clear();
    vi.clearAllMocks();
  });

  it('fetches dashboard data', async () => {
    const mockData = {
      health: { server: 'healthy' },
      statistics: { total_pipelines: 1 },
      trends: [],
      recent_runs: [],
    };
    (apiClient.get as any).mockResolvedValue({ data: mockData });

    const { result } = renderHook(() => useDashboard(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockData);
  });
});
