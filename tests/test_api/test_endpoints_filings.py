"""Tests for SEC filings endpoint functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from mcp_finnhub.api.client import FinnhubClient
from mcp_finnhub.api.endpoints import filings
from mcp_finnhub.config import AppConfig

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
class TestFilingsEndpoints:
    """Test suite for SEC filings endpoints."""

    @respx.mock
    async def test_get_sec_filings(self, test_config: AppConfig):
        """Test get_sec_filings endpoint."""
        mock_data = [
            {
                "accessNumber": "0001193125-24-001234",
                "symbol": "AAPL",
                "cik": "0000320193",
                "form": "10-K",
                "filedDate": "2024-01-15",
                "acceptedDate": "2024-01-15 16:30:00",
                "reportUrl": "https://www.sec.gov/report.html",
                "filingUrl": "https://www.sec.gov/filing.html",
            }
        ]
        respx.get("https://finnhub.io/api/v1/stock/filings").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await filings.get_sec_filings(client, "AAPL", "2024-01-01", "2024-01-31")

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["symbol"] == "AAPL"
        assert result[0]["form"] == "10-K"

    @respx.mock
    async def test_get_sec_filings_no_dates(self, test_config: AppConfig):
        """Test get_sec_filings endpoint without date parameters."""
        mock_data = []
        respx.get("https://finnhub.io/api/v1/stock/filings").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await filings.get_sec_filings(client, "AAPL")

        assert isinstance(result, list)
        assert len(result) == 0

    @respx.mock
    async def test_get_filing_sentiment(self, test_config: AppConfig):
        """Test get_filing_sentiment endpoint."""
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
            result = await filings.get_filing_sentiment(client, "0001193125-24-001234")

        assert result["accessNumber"] == "0001193125-24-001234"
        assert result["symbol"] == "AAPL"
        assert result["positiveWord"] == 150

    @respx.mock
    async def test_get_similarity_index(self, test_config: AppConfig):
        """Test get_similarity_index endpoint."""
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
            result = await filings.get_similarity_index(client, "AAPL")

        assert result["symbol"] == "AAPL"
        assert result["cik"] == "0000320193"

    @respx.mock
    async def test_get_similarity_index_with_cik(self, test_config: AppConfig):
        """Test get_similarity_index endpoint with CIK parameter."""
        mock_data = {
            "symbol": "AAPL",
            "cik": "0000320193",
            "similarity": [],
        }
        respx.get("https://finnhub.io/api/v1/stock/similarity-index").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        async with FinnhubClient(test_config) as client:
            result = await filings.get_similarity_index(
                client, "AAPL", cik="0000320193", freq="quarterly"
            )

        assert result["symbol"] == "AAPL"
        assert result["cik"] == "0000320193"
