"""Async Finnhub API client with retry and rate-limit handling.

Provides centralized HTTP client with authentication, retry logic, error mapping,
and rate limiting for consistent behavior across all endpoint modules.
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from collections import deque
from typing import TYPE_CHECKING, Any, ClassVar

import httpx

from mcp_finnhub.api.errors import handle_api_error

if TYPE_CHECKING:
    from collections.abc import Mapping

    from mcp_finnhub.config import AppConfig

logger = logging.getLogger(__name__)


class _AsyncRateLimiter:
    """Async rate limiter for per-minute request quotas.

    Uses token bucket algorithm with sliding window to enforce rate limits.
    """

    __slots__ = ("_lock", "_max_calls", "_period", "_timestamps")

    def __init__(self, max_calls: int, period_seconds: float = 60.0):
        """Initialize rate limiter.

        Args:
            max_calls: Maximum number of calls allowed per period
            period_seconds: Time period in seconds (default: 60.0 for per-minute)
        """
        self._max_calls = max_calls
        self._period = period_seconds
        self._timestamps: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until the caller may proceed within the configured quota."""
        while True:
            async with self._lock:
                now = time.monotonic()
                self._evict_older_than(now)
                if len(self._timestamps) < self._max_calls:
                    self._timestamps.append(now)
                    return
                # Need to wait - calculate how long
                oldest = self._timestamps[0]
                wait_for = self._period - (now - oldest)
            await asyncio.sleep(max(wait_for, 0.1))

    def _evict_older_than(self, current_time: float) -> None:
        """Remove timestamps older than the period window."""
        while self._timestamps and (current_time - self._timestamps[0]) >= self._period:
            self._timestamps.popleft()


class FinnhubClient:
    """Async client for Finnhub REST API.

    Provides rate limiting, retry logic with exponential backoff, and
    comprehensive error handling. Designed to work as an async context manager.

    Example:
        >>> async with FinnhubClient(config) as client:
        ...     data = await client.get("/quote", params={"symbol": "AAPL"})
    """

    RETRYABLE_STATUS_CODES: ClassVar[set[int]] = {429, 500, 502, 503, 504}

    def __init__(
        self,
        config: AppConfig,
        *,
        client: httpx.AsyncClient | None = None,
    ):
        """Initialize Finnhub API client.

        Args:
            config: Application configuration with API key and settings
            client: Optional pre-configured httpx client for testing
        """
        self.config = config
        self._provided_client = client is not None
        self._client = client or httpx.AsyncClient(
            base_url="https://finnhub.io/api/v1",
            timeout=config.request_timeout,
            headers={"X-Finnhub-Token": config.finnhub_api_key},
        )
        self._rate_limiter = _AsyncRateLimiter(config.rate_limit_rpm, period_seconds=60.0)
        self._closed = False

    async def __aenter__(self) -> FinnhubClient:
        """Enter async context manager."""
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        """Exit async context manager and close client."""
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying httpx client if we own it."""
        if not self._closed and not self._provided_client:
            await self._client.aclose()
            self._closed = True

    async def get(
        self,
        endpoint: str,
        params: Mapping[str, Any] | None = None,
        *,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Perform a GET request against Finnhub API.

        Args:
            endpoint: API endpoint path (e.g., "/quote")
            params: Query parameters (symbol, etc.)
            timeout: Optional timeout override

        Returns:
            Parsed JSON response as dictionary

        Raises:
            httpx.HTTPStatusError: On non-retryable HTTP errors
            Exception: On other request failures

        Example:
            >>> data = await client.get("/quote", params={"symbol": "AAPL"})
        """
        return await self._request(
            "GET",
            endpoint,
            params=params,
            timeout=timeout,
        )

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Mapping[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Internal request method with rate limiting and retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            timeout: Optional timeout override

        Returns:
            Parsed JSON response

        Raises:
            httpx.HTTPStatusError: On non-retryable errors (401, 400, 404)
            Exception: On max retries exceeded
        """
        # Normalize endpoint to ensure correct path
        path = endpoint if endpoint.startswith("/") else f"/{endpoint}"

        attempt = 0
        last_exception: Exception | None = None

        while attempt <= self.config.max_retries:
            # Wait for rate limit clearance
            await self._rate_limiter.acquire()

            try:
                response = await self._client.request(
                    method,
                    path,
                    params=params or {},
                    timeout=timeout or self.config.request_timeout,
                )
                response.raise_for_status()

                # Parse JSON response
                try:
                    return response.json()
                except ValueError as exc:
                    logger.error(f"Invalid JSON from Finnhub: {response.text[:200]}")
                    raise ValueError(f"Finnhub API returned malformed JSON for {path}") from exc

            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code

                # Don't retry on client errors (except 429)
                if status_code in {400, 401, 403, 404} and status_code != 429:
                    logger.error(f"Non-retryable error {status_code} for {path}")
                    # Convert to FinnhubAPIError with context
                    raise handle_api_error(exc.response) from exc

                # Retry on server errors and rate limits
                if status_code in self.RETRYABLE_STATUS_CODES:
                    attempt += 1
                    last_exception = exc

                    if attempt > self.config.max_retries:
                        logger.error(f"Max retries ({self.config.max_retries}) exceeded for {path}")
                        # Convert to FinnhubAPIError after max retries
                        raise handle_api_error(exc.response) from exc

                    # Calculate exponential backoff with jitter
                    backoff = self.config.retry_backoff_factor**attempt
                    jitter = random.uniform(0, self.config.retry_jitter * backoff)
                    sleep_time = backoff + jitter

                    logger.warning(
                        f"Retry {attempt}/{self.config.max_retries} for {path} "
                        f"after {status_code}, sleeping {sleep_time:.2f}s"
                    )
                    await asyncio.sleep(sleep_time)
                    continue

                # Other HTTP errors - raise with context
                raise handle_api_error(exc.response) from exc

            except (TimeoutError, httpx.RequestError) as exc:
                # Network errors - retry
                attempt += 1
                last_exception = exc

                if attempt > self.config.max_retries:
                    logger.error(f"Max retries exceeded for {path} due to network error")
                    raise

                backoff = self.config.retry_backoff_factor**attempt
                jitter = random.uniform(0, self.config.retry_jitter * backoff)
                sleep_time = backoff + jitter

                logger.warning(
                    f"Network error on attempt {attempt}/{self.config.max_retries} "
                    f"for {path}, sleeping {sleep_time:.2f}s"
                )
                await asyncio.sleep(sleep_time)
                continue

        # Should not reach here, but handle gracefully
        if last_exception:
            raise last_exception
        raise RuntimeError(f"Unexpected error in request to {path}")


__all__ = ["FinnhubClient"]
