import pytest
import threading
from flowcore_engine.scheduler.manager import ExecutionScheduler
from flowcore_engine.scheduler.models import ScheduledTask
from flowcore_engine.scheduler.enums import InternalTaskStatus

def test_deterministic_ordering():
    scheduler = ExecutionScheduler(max_concurrent_tasks=5)
    
    # Submit out of order, mixed priorities
    scheduler.submit_task("step_c", priority=1)
    scheduler.submit_task("step_a", priority=1)
    scheduler.submit_task("step_z", priority=10) # Highest priority
    scheduler.submit_task("step_b", priority=1)
    scheduler.submit_task("step_m", priority=0)  # Lowest priority
    
    assert scheduler.queue_size() == 5
    
    # Expected order: step_z (priority 10), then a, b, c (priority 1), then m (priority 0)
    assert scheduler.get_next_task() == "step_z"
    assert scheduler.get_next_task() == "step_a"
    assert scheduler.get_next_task() == "step_b"
    assert scheduler.get_next_task() == "step_c"
    assert scheduler.get_next_task() == "step_m"
    
    # Queue is now empty
    assert scheduler.get_next_task() is None
    assert scheduler.running_tasks() == 5
    assert scheduler.available_slots() == 0

def test_concurrent_task_submissions():
    """Verify thread-safe submissions maintain deterministic ordering."""
    scheduler = ExecutionScheduler(max_concurrent_tasks=100)
    
    # We will submit 20 tasks concurrently with priority 1
    # They should come out alphabetically
    def submitter(step_id):
        scheduler.submit_task(step_id, priority=1)
        
    threads = []
    # Mix up alphabet 
    letters = "ztymnxobpcqrakslvdew"
    for char in letters:
        t = threading.Thread(target=submitter, args=(f"step_{char}",))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    assert scheduler.queue_size() == 20
    
    # Pull them all out
    results = []
    for _ in range(20):
        results.append(scheduler.get_next_task())
        
    expected_order = [f"step_{c}" for c in sorted(letters)]
    assert results == expected_order

def test_concurrency_limits():
    scheduler = ExecutionScheduler(max_concurrent_tasks=2)
    
    scheduler.submit_task("A")
    scheduler.submit_task("B")
    scheduler.submit_task("C")
    
    assert scheduler.available_slots() == 2
    
    task1 = scheduler.get_next_task()
    task2 = scheduler.get_next_task()
    task3 = scheduler.get_next_task()
    
    assert task1 == "A"
    assert task2 == "B"
    assert task3 is None # Blocked by limiter
    
    assert scheduler.running_tasks() == 2
    assert scheduler.available_slots() == 0
    assert scheduler.queue_size() == 1
    
    # Complete A
    scheduler.complete_task(task1)
    assert scheduler.running_tasks() == 1
    assert scheduler.available_slots() == 1
    
    # Now C can run
    task3 = scheduler.get_next_task()
    assert task3 == "C"
    
def test_cancellation_not_implemented():
    scheduler = ExecutionScheduler()
    with pytest.raises(NotImplementedError):
        scheduler.cancel("some_step")
