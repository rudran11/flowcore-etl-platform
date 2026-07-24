import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DashboardCard } from '../components/DashboardCard';
import { ExecutionTable } from '../../executions/components/ExecutionTable';
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

describe('ExecutionTable', () => {
  it('renders correctly with runs', () => {
    const runs: any[] = [
      { run_id: '1', pipeline_id: 'pipe-1', pipeline_version: '1.0', status: 'COMPLETED', submitted_at: '2026-07-20T10:00:00Z', outputs: {}, steps: {} }
    ];
    render(<ExecutionTable runs={runs} />);
    expect(screen.getByText('pipe-1')).toBeInTheDocument();
    expect(screen.getByText('COMPLETED')).toBeInTheDocument();
  });

  it('renders correctly when empty', () => {
    render(<ExecutionTable runs={[]} />);
    expect(screen.getByText('No executions found.')).toBeInTheDocument();
  });
});
