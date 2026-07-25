import pytest
import asyncio
from flowcore_server.services.lineage_service import LineageService
from flowcore_server.repositories.in_memory.uow import InMemoryUnitOfWork
from flowcore_shared.schemas.lineage.dataset import DatasetCreate, DatasetType
from flowcore_shared.schemas.lineage.graph import LineageEdgeCreate, ConfidenceLevel

@pytest.mark.asyncio
async def test_lineage_graph_traversal():
    uow = InMemoryUnitOfWork()
    service = LineageService(uow)
    workspace_id = "ws-1"

    # Create Datasets
    ds1 = await service.create_dataset(workspace_id, DatasetCreate(name="DS1", type=DatasetType.DATABASE_TABLE))
    ds2 = await service.create_dataset(workspace_id, DatasetCreate(name="DS2", type=DatasetType.FILE))
    ds3 = await service.create_dataset(workspace_id, DatasetCreate(name="DS3", type=DatasetType.DATABASE_TABLE))
    ds4 = await service.create_dataset(workspace_id, DatasetCreate(name="DS4", type=DatasetType.DATABASE_TABLE))

    # Create Edges DS1 -> DS2 -> DS3 -> DS4
    async with uow:
        await uow.lineage.create_edge(LineageEdgeCreate(upstream_id=ds1.id, downstream_id=ds2.id, execution_id="e1", confidence_level=ConfidenceLevel.DETECTED))
        await uow.lineage.create_edge(LineageEdgeCreate(upstream_id=ds2.id, downstream_id=ds3.id, execution_id="e1", confidence_level=ConfidenceLevel.DETECTED))
        await uow.lineage.create_edge(LineageEdgeCreate(upstream_id=ds3.id, downstream_id=ds4.id, execution_id="e2", confidence_level=ConfidenceLevel.DETECTED))

    # Test graph traversal from DS2 (should see DS1 upstream and DS3, DS4 downstream)
    graph = await service.get_dataset_lineage_graph(ds2.id)
    assert len(graph["nodes"]) == 4
    assert len(graph["edges"]) == 3
    
    # Test impact analysis from DS1 (should affect DS2, DS3, DS4)
    impact = await service.get_dataset_impact(ds1.id)
    assert impact["criticality"] == 3
    assert impact["risk_score"] == "MEDIUM"

@pytest.mark.asyncio
async def test_lineage_graph_cycle_detection():
    uow = InMemoryUnitOfWork()
    service = LineageService(uow)
    workspace_id = "ws-1"

    ds1 = await service.create_dataset(workspace_id, DatasetCreate(name="DS1", type=DatasetType.DATABASE_TABLE))
    ds2 = await service.create_dataset(workspace_id, DatasetCreate(name="DS2", type=DatasetType.DATABASE_TABLE))

    # Create cycle DS1 -> DS2 -> DS1
    async with uow:
        await uow.lineage.create_edge(LineageEdgeCreate(upstream_id=ds1.id, downstream_id=ds2.id, execution_id="e1", confidence_level=ConfidenceLevel.DETECTED))
        await uow.lineage.create_edge(LineageEdgeCreate(upstream_id=ds2.id, downstream_id=ds1.id, execution_id="e2", confidence_level=ConfidenceLevel.DETECTED))

    # Traversal should not infinite loop
    graph = await service.get_dataset_lineage_graph(ds1.id)
    assert len(graph["nodes"]) == 2
    assert len(graph["edges"]) == 2
