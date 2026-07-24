import { useQuery } from "@tanstack/react-query";
import { fetchExecutions } from "../../../api/executions";

export const useExecutions = (
    limit: number = 25,
    skip: number = 0,
    pipelineId?: string,
    runStatus?: string
) => {
    return useQuery({
        queryKey: ["executions", limit, skip, pipelineId, runStatus],
        queryFn: () => fetchExecutions(limit, skip, pipelineId, runStatus),
        // refresh every 5 seconds for list view
        refetchInterval: 5000,
    });
};
