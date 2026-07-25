from typing import List, Optional
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_shared.schemas.lineage.dataset import Dataset, DatasetCreate, DatasetUpdate
from flowcore_shared.schemas.lineage.graph import LineageEdge, LineageEdgeCreate

class LineageService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def create_dataset(self, workspace_id: str, data: DatasetCreate) -> Dataset:
        async with self.uow:
            return await self.uow.lineage.create_dataset(workspace_id, data)

    async def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        async with self.uow:
            return await self.uow.lineage.get_dataset(dataset_id)

    async def list_datasets(self, workspace_id: str) -> List[Dataset]:
        async with self.uow:
            return await self.uow.lineage.list_datasets(workspace_id)

    async def update_dataset(self, dataset_id: str, data: DatasetUpdate) -> Dataset:
        async with self.uow:
            return await self.uow.lineage.update_dataset(dataset_id, data)

    async def delete_dataset(self, dataset_id: str) -> None:
        async with self.uow:
            await self.uow.lineage.delete_dataset(dataset_id)

    async def register_execution_lineage(self, workspace_id: str, execution_id: str, inputs: List[DatasetCreate], outputs: List[DatasetCreate]) -> None:
        # Create/resolve input datasets
        input_datasets = []
        for ds in inputs:
            # In MVP, just create. Ideally we'd search first.
            created_ds = await self.uow.lineage.create_dataset(workspace_id, ds)
            input_datasets.append(created_ds)

        # Create/resolve output datasets
        output_datasets = []
        for ds in outputs:
            created_ds = await self.uow.lineage.create_dataset(workspace_id, ds)
            output_datasets.append(created_ds)

        # Create edges from inputs to outputs (Cartesian product for MVP)
        from flowcore_shared.schemas.lineage.graph import LineageEdgeCreate, ConfidenceLevel
        for input_ds in input_datasets:
            for output_ds in output_datasets:
                edge = LineageEdgeCreate(
                    upstream_id=input_ds.id,
                    downstream_id=output_ds.id,
                    execution_id=execution_id,
                    confidence_level=ConfidenceLevel.DETECTED
                )
                await self.uow.lineage.create_edge(edge)

    async def get_dataset_lineage_graph(self, dataset_id: str) -> dict:
        """
        Builds a full lineage graph via BFS for both upstream and downstream.
        Returns a dict with 'nodes' and 'edges'.
        """
        async with self.uow:
            visited_nodes = set()
            nodes = []
            edges = []
            
            queue = [dataset_id]
            visited_nodes.add(dataset_id)
            
            # Fetch root dataset
            root_ds = await self.uow.lineage.get_dataset(dataset_id)
            if not root_ds:
                return {"nodes": [], "edges": []}
            
            nodes.append({
                "id": root_ds.id,
                "type": root_ds.type,
                "name": root_ds.name
            })
            
            # Upstream BFS
            queue_up = [dataset_id]
            while queue_up:
                current_id = queue_up.pop(0)
                upstream_edges = await self.uow.lineage.get_upstream(current_id)
                for edge in upstream_edges:
                    edges.append({
                        "id": edge.id,
                        "created_at": edge.created_at,
                        "upstream_id": edge.upstream_id,
                        "downstream_id": edge.downstream_id,
                        "pipeline_id": edge.pipeline_id,
                        "execution_id": edge.execution_id,
                        "confidence_level": edge.confidence_level
                    })
                    if edge.upstream_id not in visited_nodes:
                        visited_nodes.add(edge.upstream_id)
                        queue_up.append(edge.upstream_id)
                        ds = await self.uow.lineage.get_dataset(edge.upstream_id)
                        if ds:
                            nodes.append({
                                "id": ds.id,
                                "type": ds.type,
                                "name": ds.name
                            })

            # Downstream BFS
            queue_down = [dataset_id]
            while queue_down:
                current_id = queue_down.pop(0)
                downstream_edges = await self.uow.lineage.get_downstream(current_id)
                for edge in downstream_edges:
                    edges.append({
                        "id": edge.id,
                        "created_at": edge.created_at,
                        "upstream_id": edge.upstream_id,
                        "downstream_id": edge.downstream_id,
                        "pipeline_id": edge.pipeline_id,
                        "execution_id": edge.execution_id,
                        "confidence_level": edge.confidence_level
                    })
                    if edge.downstream_id not in visited_nodes:
                        visited_nodes.add(edge.downstream_id)
                        queue_down.append(edge.downstream_id)
                        ds = await self.uow.lineage.get_dataset(edge.downstream_id)
                        if ds:
                            nodes.append({
                                "id": ds.id,
                                "type": ds.type,
                                "name": ds.name
                            })
                            
            # Deduplicate edges
            unique_edges = []
            seen_edges = set()
            for e in edges:
                sig = f"{e['upstream_id']}->{e['downstream_id']}"
                if sig not in seen_edges:
                    seen_edges.add(sig)
                    unique_edges.append(e)

            return {"nodes": nodes, "edges": unique_edges}

    async def get_dataset_impact(self, dataset_id: str) -> dict:
        """
        Calculates impact by traversing downstream.
        """
        async with self.uow:
            visited_nodes = set()
            affected_datasets = []
            
            queue_down = [dataset_id]
            while queue_down:
                current_id = queue_down.pop(0)
                downstream_edges = await self.uow.lineage.get_downstream(current_id)
                for edge in downstream_edges:
                    if edge.downstream_id not in visited_nodes:
                        visited_nodes.add(edge.downstream_id)
                        queue_down.append(edge.downstream_id)
                        ds = await self.uow.lineage.get_dataset(edge.downstream_id)
                        if ds:
                            affected_datasets.append({
                                "id": ds.id,
                                "name": ds.name,
                                "type": ds.type
                            })
                            
            return {
                "source_dataset_id": dataset_id,
                "affected_pipelines": [], # Pipelines can be derived if execution_id -> pipeline exists
                "affected_datasets": affected_datasets,
                "affected_schedules": [],
                "risk_score": "HIGH" if len(affected_datasets) > 5 else "MEDIUM" if len(affected_datasets) > 0 else "LOW",
                "criticality": len(affected_datasets)
            }
