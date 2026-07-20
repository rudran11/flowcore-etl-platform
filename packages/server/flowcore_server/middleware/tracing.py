import uuid
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# ContextVar to store request ID globally for the current async context
request_id_var: ContextVar[str] = ContextVar("request_id", default="")

class TracingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that ensures every request has an X-Request-ID.
    Sets the ID into a ContextVar for downstream access (e.g. logging, exception handlers).
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Extract existing or generate new UUID
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Set the ContextVar
        token = request_id_var.set(req_id)
        
        try:
            response = await call_next(request)
            # Ensure the response carries the request ID
            response.headers["X-Request-ID"] = req_id
            return response
        finally:
            request_id_var.reset(token)
