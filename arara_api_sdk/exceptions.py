from typing import Any, Dict, Optional


class AraraError(Exception):
    """Base exception for Arara SDK."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[Dict[str, Any]] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Store the message and, when the API sent them, the code and details."""
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        self.code = code
        self.details = details or {}

class AraraAuthError(AraraError):
    """Raised when authentication fails."""

    pass

class AraraValidationError(AraraError):
    """Raised when request validation fails (400)."""

    pass

class AraraRateLimitError(AraraError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[Dict[str, Any]] = None,
        retry_after: Optional[int] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Store the error plus the Retry-After hint, in seconds."""
        super().__init__(message, status_code, response_body, code, details)
        self.retry_after = retry_after

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
