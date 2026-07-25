import asyncio
from flowcore_server.dependencies.core import _repository_factory
from flowcore_server.services.pipeline import PipelineService
from flowcore_server.models.pipeline_version import PipelineVersionCreate
from flowcore_server.dependencies.context import workspace_context

async def run():
    uow = _repository_factory.get_unit_of_work()
    service = PipelineService(uow)
    workspace_context.set("00000000-0000-0000-0000-000000000002")
    
    req = PipelineVersionCreate(
        version_tag="vtest123",
        dsl_definition={"steps": {"step-1": {"plugin_id": "flowcore-postgres", "config": {}}}},
        graph_definition={}
    )
    
    try:
        res = await service.create_pipeline_version("b71fd3d3-2ce2-41ae-ac66-e41a2d123ce7", req)
        print("Success:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(run())
