from typing import Optional, Dict, Any

class AraraError(Exception):
    """Base exception for Arara SDK."""
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None, 
        response_body: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body

class AraraAuthError(AraraError):
    """Raised when authentication fails."""
    pass

class AraraValidationError(AraraError):
    """Raised when request validation fails (400)."""
    pass

class AraraRateLimitError(AraraError):
    """Raised when rate limit is exceeded (429)."""
    pass

class AraraResourceNotFoundError(AraraError):
    """Raised when a resource is not found (404)."""
    pass

class AraraServerError(AraraError):
    """Raised when the server returns a 5xx error."""
    pass

class AraraConnectionError(AraraError):
    """Raised when a connection error occurs."""
    pass

class AraraTimeoutError(AraraError):
    """Raised when a request times out."""
    pass
