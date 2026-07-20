import pytest
from fastapi import FastAPI
from flowcore_server.dependencies.core import (
    get_uow,
    get_cancellation_strategy,
    get_engine_factory
)
from flowcore_server.dependencies.engine import get_plugin_manager

@pytest.mark.asyncio
async def test_di_resolves_correctly():
    assert await get_uow() is not None
    assert get_cancellation_strategy() is not None
    assert get_engine_factory() is not None
    assert get_plugin_manager() is not None

@pytest.mark.asyncio
async def test_singleton_instances():
    # Cancellation strategy should be a singleton (or default)
    c1 = get_cancellation_strategy()
    c2 = get_cancellation_strategy()
    assert c1 is c2
    
    # Engine factory should be a singleton
    e1 = get_engine_factory()
    e2 = get_engine_factory()
    assert e1 is e2
