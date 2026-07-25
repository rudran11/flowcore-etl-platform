import asyncio
import logging
import uuid
import sys
from flowcore_server.dependencies.core import get_repository_factory

async def test():
    repo_factory = get_repository_factory()
    uow = repo_factory.get_unit_of_work()
    
    # We need a workspace_id context
    from flowcore_server.dependencies.auth import _workspace_context
    # Mock workspace id (from test data, e.g. b71fd3d3-...)
    # But wait, we can just query directly.
    async with uow:
        result = await uow.session.execute("SELECT * FROM pipeline_versions")
        rows = result.fetchall()
        for row in rows:
            print("PIPELINE VERSION ID:", row.id)
            print("PIPELINE ID:", row.pipeline_id)
            print("DSL_DEFINITION:", row.dsl_definition)
            print("GRAPH_DEFINITION:", row.graph_definition)
            print("-------------")

if __name__ == "__main__":
    asyncio.run(test())
