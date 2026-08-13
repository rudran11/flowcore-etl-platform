from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import List, Dict, Any
from flowcore_shared.schemas.lineage.graph import LineageEdge, LineageGraph
from flowcore_server.dependencies.lineage import get_lineage_service
from flowcore_server.dependencies.auth import get_current_user, require_permissions
from flowcore_server.services.lineage_service import LineageService
from flowcore_shared.schemas.auth.user import UserInDB
from flowcore_shared.schemas.auth import Principal

router = APIRouter(prefix="/lineage", tags=["lineage"])

@router.get("/{dataset_id}", response_model=LineageGraph)
async def get_dataset_lineage(
    dataset_id: str,
    x_workspace_id: str = Header(...),
    service: LineageService = Depends(get_lineage_service),
    principal: Principal = Depends(require_permissions(["dataset:read"]))
):
    # Full recursive graph traversal
    dataset = await service.get_dataset(dataset_id)
    if not dataset or dataset.workspace_id != x_workspace_id:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    graph_dict = await service.get_dataset_lineage_graph(dataset_id)
    return LineageGraph(nodes=graph_dict["nodes"], edges=graph_dict["edges"])

@router.get("/impact/{dataset_id}")
async def get_dataset_impact(
    dataset_id: str,
    x_workspace_id: str = Header(...),
    service: LineageService = Depends(get_lineage_service),
    principal: Principal = Depends(require_permissions(["dataset:read"]))
):
    dataset = await service.get_dataset(dataset_id)
    if not dataset or dataset.workspace_id != x_workspace_id:
        raise HTTPException(status_code=404, detail="Dataset not found")

    return await service.get_dataset_impact(dataset_id)
