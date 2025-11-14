"""Unit tests for FinnhubClient.

Tests HTTP client with rate limiting, retry logic, and error handling.
"""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.config import AppConfig


@pytest.fixture
def test_config(tmp_path: Path) -> AppConfig:
    """Create test configuration."""
    return AppConfig(
        finnhub_api_key="test_api_key",
        storage_directory=tmp_path / "data",
        rate_limit_rpm=60,  # 1 per second for faster tests
        request_timeout=5,
        max_retries=2,
        retry_backoff_factor=1.5,
        retry_jitter=0.1,
    )


@pytest.mark.asyncio
class TestFinnhubClient:
    """Tests for FinnhubClient class."""

    async def test_initialization(self, test_config: AppConfig):
        """Test client initialization."""
        async with FinnhubClient(test_config) as client:
            assert client.config == test_config
            assert not client._closed

    async def test_context_manager_closes_client(self, test_config: AppConfig):
        """Test that context manager closes the client."""
        client = FinnhubClient(test_config)
        async with client:
            pass
        assert client._closed

    @respx.mock
    async def test_successful_get_request(self, test_config: AppConfig):
        """Test successful GET request."""
        mock_response = {"c": 150.0, "h": 151.0, "l": 149.0}

        respx.get("https://finnhub.io/api/v1/quote").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        async with FinnhubClient(test_config) as client:
            result = await client.get("/quote", params={"symbol": "AAPL"})

        assert result == mock_response

    @respx.mock
    async def test_retry_on_429(self, test_config: AppConfig):
        """Test retry logic on 429 rate limit error."""
        mock_response = {"c": 150.0}

        # First two requests fail with 429, third succeeds
        route = respx.get("https://finnhub.io/api/v1/quote")
        route.side_effect = [
            httpx.Response(429, json={"error": "Rate limit"}),
            httpx.Response(429, json={"error": "Rate limit"}),
            httpx.Response(200, json=mock_response),
        ]

        async with FinnhubClient(test_config) as client:
            result = await client.get("/quote", params={"symbol": "AAPL"})

        assert result == mock_response
        assert route.call_count == 3

    @respx.mock
    async def test_retry_on_500(self, test_config: AppConfig):
        """Test retry logic on 500 server error."""
        mock_response = {"c": 150.0}

        route = respx.get("https://finnhub.io/api/v1/quote")
        route.side_effect = [
            httpx.Response(500, json={"error": "Server error"}),
            httpx.Response(200, json=mock_response),
        ]

        async with FinnhubClient(test_config) as client:
            result = await client.get("/quote", params={"symbol": "AAPL"})

        assert result == mock_response
        assert route.call_count == 2

    @respx.mock
    async def test_no_retry_on_401(self, test_config: AppConfig):
        """Test that 401 errors are not retried."""
        respx.get("https://finnhub.io/api/v1/quote").mock(
            return_value=httpx.Response(401, json={"error": "Unauthorized"})
        )

        async with FinnhubClient(test_config) as client:
            with pytest.raises(httpx.HTTPStatusError) as exc_info:
                await client.get("/quote", params={"symbol": "AAPL"})

        assert exc_info.value.response.status_code == 401

    @respx.mock
    async def test_no_retry_on_404(self, test_config: AppConfig):
        """Test that 404 errors are not retried."""
        respx.get("https://finnhub.io/api/v1/quote").mock(
            return_value=httpx.Response(404, json={"error": "Not found"})
        )

        async with FinnhubClient(test_config) as client:
            with pytest.raises(httpx.HTTPStatusError) as exc_info:
                await client.get("/quote", params={"symbol": "INVALID"})

        assert exc_info.value.response.status_code == 404

    @respx.mock
    async def test_max_retries_exceeded(self, test_config: AppConfig):
        """Test that max retries is enforced."""
        route = respx.get("https://finnhub.io/api/v1/quote")
        route.mock(return_value=httpx.Response(500, json={"error": "Server error"}))

        async with FinnhubClient(test_config) as client:
            with pytest.raises(httpx.HTTPStatusError):
                await client.get("/quote", params={"symbol": "AAPL"})

        # Should try initial + 2 retries = 3 total
        assert route.call_count == 3

    @respx.mock
    async def test_endpoint_normalization(self, test_config: AppConfig):
        """Test that endpoints are normalized correctly."""
        mock_response = {"c": 150.0}

        # Test without leading slash
        route = respx.get("https://finnhub.io/api/v1/quote")
        route.mock(return_value=httpx.Response(200, json=mock_response))

        async with FinnhubClient(test_config) as client:
            result = await client.get("quote", params={"symbol": "AAPL"})

        assert result == mock_response

    @respx.mock
    async def test_invalid_json_response(self, test_config: AppConfig):
        """Test handling of invalid JSON response."""
        respx.get("https://finnhub.io/api/v1/quote").mock(
            return_value=httpx.Response(200, text="Not valid JSON")
        )

        async with FinnhubClient(test_config) as client:
            with pytest.raises(ValueError, match="malformed JSON"):
                await client.get("/quote", params={"symbol": "AAPL"})
