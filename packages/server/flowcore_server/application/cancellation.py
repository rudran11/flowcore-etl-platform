from abc import ABC, abstractmethod
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_shared.schemas.base.enums import ExecutionState

class CancellationStrategy(ABC):
    """
    Abstract strategy for cancelling an execution run.
    """
    @abstractmethod
    async def cancel(self, run_id: str, uow: AbstractUnitOfWork) -> None:
        pass

class DefaultCancellationStrategy(CancellationStrategy):
    """
    Cancels a run by updating its status in the persistence layer,
    and signaling the cancellation event to the running engine.
    """
    def __init__(self, controller: 'CancellationController' = None):
        if controller is None:
            from flowcore_server.services.cancellation_controller import CancellationController
            controller = CancellationController()
        self.controller = controller

    async def cancel(self, run_id: str, uow: AbstractUnitOfWork) -> None:
        # Signal the engine to stop gracefully
        self.controller.cancel(run_id)
        
        async with uow:
            run = await uow.executions.get_run(run_id)
            if run and run.status not in [ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.CANCELLED]:
                await uow.executions.update_run_status(run_id, ExecutionState.CANCELLED)
            await uow.commit()
