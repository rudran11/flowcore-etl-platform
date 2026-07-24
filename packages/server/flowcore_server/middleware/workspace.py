from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from flowcore_server.dependencies.context import workspace_context

class WorkspaceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        workspace_id = request.headers.get("x-workspace-id")
        
        if workspace_id:
            token = workspace_context.set(workspace_id)
        else:
            token = workspace_context.set(None)
            
        try:
            response = await call_next(request)
            return response
        finally:
            workspace_context.reset(token)
