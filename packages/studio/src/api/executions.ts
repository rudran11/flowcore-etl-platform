import { apiClient } from "./client";

export interface ExecutionStepResponse {
    step_id: string;
    status: string;
    start_time?: string;
    end_time?: string;
    duration_ms?: number;
    retry_count: number;
    error_message?: string;
    outputs: Record<string, any>;
    logs: string[];
}

export interface ExecutionResponse {
    run_id: string;
    pipeline_id: string;
    pipeline_version: string;
    status: string;
    submitted_at: string;
    started_at?: string;
    finished_at?: string;
    duration_ms?: number;
    error?: string;
    outputs: Record<string, any>;
    steps: Record<string, ExecutionStepResponse>;
}

export interface ExecutionListResponse {
    items: ExecutionResponse[];
    total: number;
    limit: number;
    skip: number;
}

export const fetchExecutions = async (
    limit: number = 25,
    skip: number = 0,
    pipeline_id?: string,
    run_status?: string
): Promise<ExecutionListResponse> => {
    const params = new URLSearchParams({
        limit: limit.toString(),
        skip: skip.toString(),
    });
    if (pipeline_id) params.append("pipeline_id", pipeline_id);
    if (run_status && run_status !== "ALL") params.append("run_status", run_status);

    const response = await apiClient.get(`/runs?${params.toString()}`);
    return response.data;
};

export const fetchExecution = async (run_id: string): Promise<ExecutionResponse> => {
    const response = await apiClient.get(`/runs/${run_id}`);
    return response.data;
};

export const cancelExecution = async (run_id: string): Promise<ExecutionResponse> => {
    const response = await apiClient.post(`/runs/${run_id}/cancel`);
    return response.data;
};
