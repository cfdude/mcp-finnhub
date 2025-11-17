"""Tests for SecFilingsTool."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.config import AppConfig
from mcp_finnhub.tools.sec_filings import SecFilingsTool

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def test_config(tmp_path: Path) -> AppConfig:
    """Create test configuration."""
    return AppConfig(
        finnhub_api_key="test_api_key",
        storage_directory=tmp_path / "data",
        rate_limit_rpm=60,
        request_timeout=5,
        max_retries=2,
        retry_backoff_factor=1.5,
        retry_jitter=0.1,
    )


@pytest.mark.asyncio
class TestSecFilingsTool:
    """Test suite for SecFilingsTool."""

    def test_valid_operations(self):
        """Test that all valid operations are defined."""
        expected_operations = {
            "get_sec_filings",
            "get_filing_sentiment",
            "get_similarity_index",
        }
        assert expected_operations == SecFilingsTool.VALID_OPERATIONS

    @respx.mock
    async def test_get_sec_filings(self, test_config: AppConfig):
        """Test get_sec_filings operation."""
        mock_data = [
            {
                "accessNumber": "0001193125-24-001234",
                "symbol": "AAPL",
                "cik": "0000320193",
                "form": "10-K",
            }
        ]
        respx.get("https://finnhub.io/api/v1/stock/filings").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = SecFilingsTool(client)
            result = await tool.get_sec_filings("AAPL", "2024-01-01", "2024-01-31")

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["symbol"] == "AAPL"

    @respx.mock
    async def test_get_sec_filings_no_dates(self, test_config: AppConfig):
        """Test get_sec_filings operation without date parameters."""
        mock_data = []
        respx.get("https://finnhub.io/api/v1/stock/filings").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = SecFilingsTool(client)
            result = await tool.get_sec_filings("AAPL")

        assert isinstance(result, list)
        assert len(result) == 0

    @respx.mock
    async def test_get_filing_sentiment(self, test_config: AppConfig):
        """Test get_filing_sentiment operation."""
        mock_data = {
            "accessNumber": "0001193125-24-001234",
            "symbol": "AAPL",
            "cik": "0000320193",
            "sentiment": {
                "positive": 0.65,
                "negative": 0.15,
                "neutral": 0.20,
            },
            "positiveWord": 150,
            "negativeWord": 35,
        }
        respx.get("https://finnhub.io/api/v1/stock/filings-sentiment").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = SecFilingsTool(client)
            result = await tool.get_filing_sentiment("0001193125-24-001234")

        assert result["accessNumber"] == "0001193125-24-001234"
        assert result["symbol"] == "AAPL"
        assert result["positiveWord"] == 150

    @respx.mock
    async def test_get_similarity_index(self, test_config: AppConfig):
        """Test get_similarity_index operation."""
        mock_data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "similarity": [
                {
                    "item1": 0.95,
                    "item1a": 0.92,
                    "item7": 0.88,
                }
            ],
        }
        respx.get("https://finnhub.io/api/v1/stock/similarity-index").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = SecFilingsTool(client)
            result = await tool.get_similarity_index("AAPL")

        assert result["symbol"] == "AAPL"
        assert result["cik"] == "0000320193"

    @respx.mock
    async def test_get_similarity_index_with_params(self, test_config: AppConfig):
        """Test get_similarity_index operation with optional parameters."""
        mock_data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "similarity": [],
        }
        respx.get("https://finnhub.io/api/v1/stock/similarity-index").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = SecFilingsTool(client)
            result = await tool.get_similarity_index("AAPL", cik="0000320193", freq="quarterly")

        assert result["symbol"] == "AAPL"

    @respx.mock
    async def test_execute_get_sec_filings(self, test_config: AppConfig):
        """Test execute method with get_sec_filings operation."""
        mock_data = []
        respx.get("https://finnhub.io/api/v1/stock/filings").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = SecFilingsTool(client)
            result = await tool.execute("get_sec_filings", symbol="AAPL")

        assert isinstance(result, list)

    @respx.mock
    async def test_execute_get_filing_sentiment(self, test_config: AppConfig):
        """Test execute method with get_filing_sentiment operation."""
        mock_data = {
            "accessNumber": "0001193125-24-001234",
            "symbol": "AAPL",
        }
        respx.get("https://finnhub.io/api/v1/stock/filings-sentiment").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = SecFilingsTool(client)
            result = await tool.execute(
                "get_filing_sentiment", access_number="0001193125-24-001234"
            )

        assert result["accessNumber"] == "0001193125-24-001234"

    @respx.mock
    async def test_execute_get_similarity_index(self, test_config: AppConfig):
        """Test execute method with get_similarity_index operation."""
        mock_data = {
            "symbol": "AAPL",
            "similarity": [],
        }
        respx.get("https://finnhub.io/api/v1/stock/similarity-index").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            tool = SecFilingsTool(client)
            result = await tool.execute("get_similarity_index", symbol="AAPL")

        assert result["symbol"] == "AAPL"

    async def test_validate_operation_valid(self, test_config: AppConfig):
        """Test validate_operation with valid operation."""
        async with FinnhubClient(test_config) as client:
            tool = SecFilingsTool(client)
            # Should not raise
            tool.validate_operation("get_sec_filings")

    async def test_validate_operation_invalid(self, test_config: AppConfig):
        """Test validate_operation with invalid operation."""
        async with FinnhubClient(test_config) as client:
            tool = SecFilingsTool(client)
            with pytest.raises(ValueError, match="Invalid operation"):
                tool.validate_operation("invalid_operation")

    async def test_execute_invalid_operation(self, test_config: AppConfig):
        """Test execute with invalid operation."""
        async with FinnhubClient(test_config) as client:
            tool = SecFilingsTool(client)
            with pytest.raises(ValueError, match="Invalid operation"):
                await tool.execute("invalid_operation", symbol="AAPL")
