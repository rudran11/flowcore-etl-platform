import pytest
from fastapi import FastAPI
from flowcore_server.dependencies.core import (
    get_run_registry,
    get_pipeline_repository,
    get_cancellation_strategy,
    get_engine_factory
)
from flowcore_server.dependencies.engine import get_plugin_manager

def test_di_resolves_correctly():
    assert get_run_registry() is not None
    assert get_pipeline_repository() is not None
    assert get_cancellation_strategy() is not None
    assert get_engine_factory() is not None
    assert get_plugin_manager() is not None

def test_singleton_instances():
    r1 = get_run_registry()
    r2 = get_run_registry()
    assert r1 is r2
    
    p1 = get_pipeline_repository()
    p2 = get_pipeline_repository()
    assert p1 is p2
