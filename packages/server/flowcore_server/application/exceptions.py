class ApplicationError(Exception):
    """Base class for application layer errors."""
    pass

class ResourceNotFoundError(ApplicationError):
    """Raised when a requested resource is not found."""
    pass
