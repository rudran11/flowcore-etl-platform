import contextvars
from typing import Optional

workspace_context: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('workspace_context', default=None)

def get_workspace_id() -> str:
    ws_id = workspace_context.get()
    if not ws_id:
        raise ValueError("No workspace context active.")
    return ws_id
