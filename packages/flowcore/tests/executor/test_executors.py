import pytest
import time
from flowcore.engine.executor.models import ExecutionResult
from flowcore.engine.executor.local import LocalExecutor
from flowcore.engine.executor.thread import ThreadExecutor

def success_task(val: int) -> int:
    return val * 2

def failing_task(msg: str) -> None:
    raise ValueError(msg)

def slow_task(duration: float) -> str:
    time.sleep(duration)
    return "done"

class TestLocalExecutor:
    def test_success_execution(self):
        with LocalExecutor() as executor:
            future = executor.submit(success_task, 21)
            assert future.done()
            result = future.result()
            
            assert isinstance(result, ExecutionResult)
            assert result.success is True
            assert result.output == 42
            assert result.exception is None
            assert result.duration_ms >= 0
            
    def test_failing_execution(self):
        with LocalExecutor() as executor:
            future = executor.submit(failing_task, "test error")
            assert future.done()
            result = future.result()
            
            assert isinstance(result, ExecutionResult)
            assert result.success is False
            assert result.output is None
            assert isinstance(result.exception, ValueError)
            assert str(result.exception) == "test error"

class TestThreadExecutor:
    def test_success_execution(self):
        with ThreadExecutor(max_workers=2) as executor:
            future = executor.submit(success_task, 5)
            result = future.result()
            
            assert isinstance(result, ExecutionResult)
            assert result.success is True
            assert result.output == 10
            
    def test_failing_execution(self):
        with ThreadExecutor(max_workers=1) as executor:
            future = executor.submit(failing_task, "thread fail")
            result = future.result()
            
            assert result.success is False
            assert isinstance(result.exception, ValueError)
            assert str(result.exception) == "thread fail"

    def test_multiple_concurrent_tasks(self):
        with ThreadExecutor(max_workers=3) as executor:
            f1 = executor.submit(slow_task, 0.1)
            f2 = executor.submit(slow_task, 0.1)
            f3 = executor.submit(slow_task, 0.1)
            
            # Start times should be close, meaning they run concurrently
            results = [f1.result(), f2.result(), f3.result()]
            
            for res in results:
                assert res.success is True
                assert res.output == "done"
                assert res.duration_ms >= 100
