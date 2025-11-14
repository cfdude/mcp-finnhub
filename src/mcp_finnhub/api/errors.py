"""Exception classes and error handling for Finnhub API.

Provides structured error types for different API failures with detailed context
for debugging and error recovery strategies.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import httpx


class FinnhubAPIError(Exception):
    """Base exception for all Finnhub API errors.

    Attributes:
        status_code: HTTP status code from the response
        message: Human-readable error message
        response_data: Raw response data from API (if available)
        request_url: URL that was requested
        request_params: Query parameters that were sent
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
        request_url: str | None = None,
        request_params: dict[str, Any] | None = None,
    ):
        """Initialize FinnhubAPIError.

        Args:
            message: Human-readable error message
            status_code: HTTP status code (if applicable)
            response_data: Raw response data from API
            request_url: URL that was requested
            request_params: Query parameters sent with request
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        self.request_url = request_url
        self.request_params = request_params or {}

    def __str__(self) -> str:
        """Format error message with context."""
        parts = [self.message]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.request_url:
            parts.append(f"URL: {self.request_url}")
        if self.request_params:
            params_str = ", ".join(f"{k}={v}" for k, v in self.request_params.items())
            parts.append(f"Params: {params_str}")
        return " | ".join(parts)


class AuthenticationError(FinnhubAPIError):
    """Raised when API key is invalid or missing (401)."""

    def __init__(
        self,
        message: str = "Invalid or missing API key",
        **kwargs: Any,
    ):
        """Initialize AuthenticationError with 401 status."""
        super().__init__(message, status_code=401, **kwargs)


class PermissionError(FinnhubAPIError):
    """Raised when API key lacks permission for endpoint (403)."""

    def __init__(
        self,
        message: str = "Insufficient permissions for this endpoint",
        **kwargs: Any,
    ):
        """Initialize PermissionError with 403 status."""
        super().__init__(message, status_code=403, **kwargs)


class NotFoundError(FinnhubAPIError):
    """Raised when requested resource is not found (404)."""

    def __init__(
        self,
        message: str = "Requested resource not found",
        **kwargs: Any,
    ):
        """Initialize NotFoundError with 404 status."""
        super().__init__(message, status_code=404, **kwargs)


class RateLimitError(FinnhubAPIError):
    """Raised when API rate limit is exceeded (429)."""

    def __init__(
        self,
        message: str = "API rate limit exceeded",
        **kwargs: Any,
    ):
        """Initialize RateLimitError with 429 status."""
        super().__init__(message, status_code=429, **kwargs)


class ServerError(FinnhubAPIError):
    """Raised when Finnhub API experiences server issues (500-504)."""

    def __init__(
        self,
        message: str = "Finnhub API server error",
        **kwargs: Any,
    ):
        """Initialize ServerError with 5xx status."""
        super().__init__(message, **kwargs)


class ValidationError(FinnhubAPIError):
    """Raised when request parameters are invalid (400)."""

    def __init__(
        self,
        message: str = "Invalid request parameters",
        **kwargs: Any,
    ):
        """Initialize ValidationError with 400 status."""
        super().__init__(message, status_code=400, **kwargs)


def handle_api_error(response: httpx.Response) -> FinnhubAPIError:
    """Convert httpx.Response to appropriate FinnhubAPIError.

    Maps HTTP status codes to specific error types and extracts error
    details from response body when available.

    Args:
        response: httpx Response object with error status

    Returns:
        Appropriate FinnhubAPIError subclass instance

    Example:
        >>> try:
        ...     response.raise_for_status()
        ... except httpx.HTTPStatusError as exc:
        ...     raise handle_api_error(exc.response) from exc
    """
    status_code = response.status_code
    request_url = str(response.request.url)

    # Extract error message from response body
    try:
        response_data = response.json()
        error_msg = response_data.get("error", response_data.get("message", ""))
    except Exception:
        response_data = {}
        error_msg = response.text[:200] if response.text else ""

    # Extract query params from request URL
    request_params = dict(response.request.url.params)

    # Map status codes to specific error types
    error_kwargs = {
        "response_data": response_data,
        "request_url": request_url,
        "request_params": request_params,
    }

    if status_code == 401:
        return AuthenticationError(
            error_msg or "Invalid or missing API key",
            **error_kwargs,
        )
    elif status_code == 403:
        return PermissionError(
            error_msg or "Insufficient permissions for this endpoint",
            **error_kwargs,
        )
    elif status_code == 404:
        return NotFoundError(
            error_msg or "Requested resource not found",
            **error_kwargs,
        )
    elif status_code == 429:
        return RateLimitError(
            error_msg or "API rate limit exceeded",
            **error_kwargs,
        )
    elif status_code == 400:
        return ValidationError(
            error_msg or "Invalid request parameters",
            **error_kwargs,
        )
    elif 500 <= status_code < 600:
        return ServerError(
            error_msg or f"Finnhub API server error ({status_code})",
            status_code=status_code,
            **error_kwargs,
        )
    else:
        # Generic error for unexpected status codes
        return FinnhubAPIError(
            error_msg or f"Unexpected API error ({status_code})",
            status_code=status_code,
            **error_kwargs,
        )


__all__ = [
    "AuthenticationError",
    "FinnhubAPIError",
    "NotFoundError",
    "PermissionError",
    "RateLimitError",
    "ServerError",
    "ValidationError",
    "handle_api_error",
]
