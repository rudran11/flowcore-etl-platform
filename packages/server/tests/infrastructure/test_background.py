from fastapi import BackgroundTasks
from flowcore_server.application.background import FastAPIBackgroundStrategy, TaskHandle

def dummy_task():
    pass

def test_fastapi_background_strategy():
    bt = BackgroundTasks()
    strategy = FastAPIBackgroundStrategy(bt)
    
    handle = strategy.submit(dummy_task)
    assert isinstance(handle, TaskHandle)
    assert handle.task_id == "fastapi-task"
    assert handle.status == "PENDING"
    
    assert len(bt.tasks) == 1
    assert bt.tasks[0].func == dummy_task
    
    # Test shutdown
    strategy.shutdown() # Should not raise
