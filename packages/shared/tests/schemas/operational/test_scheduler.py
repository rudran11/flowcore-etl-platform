import pytest
from pydantic import ValidationError
from flowcore_shared.schemas.operational.scheduler import SchedulerTrigger

def test_scheduler_trigger_creation():
    trigger = SchedulerTrigger(
        id="sched-1",
        pipeline_id="etl-001",
        cron_expression="0 0 * * *"
    )
    assert trigger.enabled is True
    assert trigger.cron_expression == "0 0 * * *"
