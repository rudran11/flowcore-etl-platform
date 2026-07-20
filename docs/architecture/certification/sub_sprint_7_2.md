# Sub-Sprint 7.2 Certification: Dashboard & Analytics

## Dashboard Architecture

The FlowCore Studio dashboard relies on the API gateway (`GET /api/v1/dashboard`) to serve all analytics data in a single request. 

**Architectural Enforcement:**
The frontend Studio remains purely a presentation layer. It does not contain complex business logic or data aggregations. All data operations are securely delegated to the existing FlowCore Engine and PostgreSQL Repository Layer.

## API Contract

- **Endpoint:** `GET /api/v1/dashboard`
- **Response Format:**
  - `statistics`: Total pipelines, total runs, success rate (terminal states only), avg duration.
  - `execution_summary`: Breakdown by states (completed, failed, running, etc).
  - `trends`: 7-day execution trend dataset.
  - `recent_runs`: Top 10 latest pipeline runs.
  - `health`: Component statuses.

## Components Created

- `DashboardPage`: Orchestrates the grid layout, API data fetching via React Query, and handles loading/error states.
- `DashboardGrid` & `DashboardCard`: Presents core statistics (Pipelines, Executions, Success Rate).
- `ExecutionTrendChart`: A Recharts visualization showing the 7-day execution trends. Includes an empty state placeholder.
- `RecentRunsTable`: A tabular view of the latest executions featuring status badges.
- `RootLayout`: Navigation sidebar and header structure.

## Test Summary

- **Backend:** 55/55 passed (including newly added repository aggregation and dashboard API tests).
- **Frontend (Vitest):** Unit tests verified the React components (`DashboardCard`, `RecentRunsTable`), page states (loading, error, success), and the `useDashboard` hook.
- **Frontend (Playwright):** End-to-end tests successfully verified that the UI renders data properly and navigation functions correctly.

## Known Limitations

- System Health is partially mocked. `engine` status shows as unknown since the engine doesn't emit explicit health heartbeat events to the server layer yet.
- Recent runs list doesn't currently support real-time WebSocket updates, requiring a 5-second polling interval via React Query.

## Future Improvements

- Add WebSocket streaming for live `RecentRunsTable` updates.
- Allow users to select the date range (e.g., 30 days) for the `ExecutionTrendChart`.
