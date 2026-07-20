import logging
import sys
from flowcore_server.middleware.tracing import request_id_var

class RequestIdFilter(logging.Filter):
    """
    Logging filter that injects the current request_id from ContextVar into log records.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True

def setup_logging(level: int = logging.INFO):
    """
    Configures the root logger with the RequestIdFilter and a standard format.
    """
    logger = logging.getLogger()
    logger.setLevel(level)

    # Clear existing handlers
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # [%(asctime)s] [%(levelname)s] [%(request_id)s] %(message)s
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(request_id)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z"
    )
    handler.setFormatter(formatter)
    
    # Add our context filter
    handler.addFilter(RequestIdFilter())
    
    logger.addHandler(handler)
