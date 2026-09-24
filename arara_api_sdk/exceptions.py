from typing import Any, Dict, Optional


class AraraError(Exception):
    """Base exception for Arara SDK.

    Carries the API error envelope ``{"error": {"code", "message", "details"}}``
    unwrapped into ``code``, ``message`` and ``details``, plus the HTTP status
    and the ``Retry-After`` hint (seconds) when the server sent one.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[Dict[str, Any]] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        retry_after: Optional[int] = None,
    ):
        """Store the message and, when the API sent them, the code and details."""
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        self.code = code
        self.details = details or {}
        self.retry_after = retry_after


class AraraAuthError(AraraError):
    """Raised when the API key is missing, invalid, expired or not allowed.

    The backend answers key failures with 401 or with 403 without an error
    code (the filter rejects the request before the envelope is built).
    """


class AraraForbiddenError(AraraError):
    """Raised on a business 403 that carries an error code."""


class AraraPlanFeatureLockedError(AraraForbiddenError):
    """Raised on 403 ``PLAN_FEATURE_LOCKED``: the plan does not include the feature."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[Dict[str, Any]] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        retry_after: Optional[int] = None,
    ):
        """Expose ``feature``, ``current_plan`` and ``upgrade_to`` from details."""
        super().__init__(
            message, status_code, response_body, code, details, retry_after
        )
        self.feature = _str_or_none(self.details.get("feature"))
        self.current_plan = _str_or_none(self.details.get("currentPlan"))
        self.upgrade_to = _str_or_none(self.details.get("upgradeTo"))


class AraraValidationError(AraraError):
    """Raised when request validation fails (400)."""


class AraraUnprocessableError(AraraError):
    """Raised on 422, e.g. send pre-flight (``INVALID_RECIPIENT``)."""


class AraraRateLimitError(AraraError):
    """Raised when rate limit is exceeded (429)."""


class AraraResourceNotFoundError(AraraError):
    """Raised when a resource is not found (404)."""


class AraraServerError(AraraError):
    """Raised when the server returns a 5xx error."""


class AraraConnectionError(AraraError):
    """Raised when a connection error occurs."""


class AraraTimeoutError(AraraError):
    """Raised when a request times out."""


def _str_or_none(value: Any) -> Optional[str]:
    """Return the value when it is a string, otherwise None."""
    return value if isinstance(value, str) else None
