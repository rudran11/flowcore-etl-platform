import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchExecution, cancelExecution } from "../../../api/executions";

export const useExecution = (runId: string) => {
    return useQuery({
        queryKey: ["execution", runId],
        queryFn: () => fetchExecution(runId),
        // refresh every 2 seconds if not terminal
        refetchInterval: (query) => {
            if (!query.state.data) return 2000;
            const status = query.state.data.status;
            if (["COMPLETED", "FAILED", "CANCELLED"].includes(status)) {
                return false; // Terminal state, stop polling
            }
            return 2000;
        },
    });
};

export const useCancelExecution = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (runId: string) => cancelExecution(runId),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ["execution", data.run_id] });
            queryClient.invalidateQueries({ queryKey: ["executions"] });
        },
    });
};
