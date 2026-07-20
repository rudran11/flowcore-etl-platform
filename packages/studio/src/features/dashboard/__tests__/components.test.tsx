import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DashboardCard } from '../components/DashboardCard';
import { RecentRunsTable } from '../components/RecentRunsTable';
import { DashboardGrid } from '../components/DashboardGrid';

describe('DashboardCard', () => {
  it('renders title and value', () => {
    render(<DashboardCard title="Total Pipelines" value={42} description="Test desc" />);
    expect(screen.getByText('Total Pipelines')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
    expect(screen.getByText('Test desc')).toBeInTheDocument();
  });
});

describe('DashboardGrid', () => {
  it('renders children', () => {
    render(
      <DashboardGrid>
        <div data-testid="child">Child</div>
      </DashboardGrid>
    );
    expect(screen.getByTestId('child')).toBeInTheDocument();
  });
});

describe('RecentRunsTable', () => {
  it('renders correctly with runs', () => {
    const runs = [
      { pipeline_id: 'pipe-1', status: 'COMPLETED', trigger_type: 'API', start_time: '2026-07-20T10:00:00Z' }
    ];
    render(<RecentRunsTable runs={runs} />);
    expect(screen.getByText('pipe-1')).toBeInTheDocument();
    expect(screen.getByText('COMPLETED')).toBeInTheDocument();
    expect(screen.getByText('API')).toBeInTheDocument();
  });

  it('renders correctly when empty', () => {
    render(<RecentRunsTable runs={[]} />);
    expect(screen.getByText('No recent runs')).toBeInTheDocument();
  });
});
